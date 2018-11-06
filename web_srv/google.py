# -*- coding: UTF-8 -*-
# _author_ = 'jliangqiu'
import base64
import io
import os
import json
import cv2
import requests
import numpy as np
import time
from PIL import Image, ImageDraw, ImageFont
def draw_rect(path):
    IS_SAVE = True
    ttf_path = "simhei.ttf"

    def resize_imshow(im, scale = 1080, max_scale=None):
        h, w = im.shape[:2]
        if h >= 1080:
            f = float(scale) / h
            if max_scale != None and f * max(h, w) > max_scale:
                f = float(max_scale) / max(h, w)
            return cv2.resize(im, None, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC)
        else:
            return im

    def text_recognize_post_url(img_url):
        url = 'https://ai101-google-ocr.awsca.101.com/ai/detect_text?key=AIzaSyDaBXVvSNjBvEwwjpA-rjsmfJ0QPrjz7CM'
        # url = 'https://vision.googleapis.com/v1/images:annotate?key=AIzaSyDaBXVvSNjBvEwwjpA-rjsmfJ0QPrjz7CM'
        # "type": "DOCUMENT_TEXT_DETECTION",
        data = json.dumps({"requests": [
            {
                "image": {
                             "source": {
                                 "imageUri": img_url
                             }
                         },
                "features": [
                    {
                        "type": "TEXT_DETECTION",
                        "maxResults": 1
                    }
                ]
            }
        ]})
        header = {'Content-Type': 'application/json'}
        response = requests.post(url=url, headers = header,data=data)
        analysis = response.json()
        return analysis

    def text_recognize_post_local(img_path, is_rewrite = False):
        global analysis
        json_path = img_path.replace('.jpg', 'google_analysis.txt')
        json_path = json_path.replace('.JPG', 'google_analysis.txt')
        json_path = json_path.replace('.png', 'google_analysis.txt')
        if os.path.exists(json_path):
            if is_rewrite:
                os.remove(json_path)
            else:
                with open(json_path, 'r') as j_f:
                    for line in j_f:
                        line = line.rstrip("\n")
                        analysis = json.loads(line)
                return analysis, json_path
        start = time.time()
        url = 'https://ai101-google-ocr.awsca.101.com/ai/detect_text?key=AIzaSyDaBXVvSNjBvEwwjpA-rjsmfJ0QPrjz7CM'#转接口 代替翻墙 比较慢
        # url = 'https://vision.googleapis.com/v1/images:annotate?key=AIzaSyDaBXVvSNjBvEwwjpA-rjsmfJ0QPrjz7CM' #直接访问 二选一
        with io.open(img_path, 'rb') as image_file:
            content = base64.b64encode(image_file.read())
        data = json.dumps({"requests": [
            {
                "image": {
                            "content": content
                    },
                "features": [
                    {
                        "type": "TEXT_DETECTION",
                        "maxResults": 1
                    }
                ]
            }
        ]})
        header = {'Content-Type': 'application/json'}
        response = requests.post(url=url, headers = header,data=data)
        analysis = response.json()

        if IS_SAVE:
            with open(json_path, 'w') as j_f:
                j_f.write(json.dumps(analysis) + "\n")

        return analysis, json_path

    def analysis_json_path(json_path):
        if not os.path.exists(json_path):
            return [], [], [], [], 0

        global analysis
        position_y = 0
        with open(json_path, 'r') as j_f:
            for line in j_f:
                line = line.rstrip("\n")
                analysis = json.loads(line)
        responses = analysis['responses'][0]

        if len(responses) == 0:
            return [], [], [], [], position_y

        fullTextAnnotation = responses['fullTextAnnotation']
        textAnnotations = responses['textAnnotations']
        text_description, text_bbox = [], []
        for text_line in textAnnotations:
            text_description.append(text_line["description"])
            text_bbox.append(text_line["boundingPoly"])

        len_text = len(text_bbox)
        boxes_list, texts_list = [], []
        for i in range(len_text):
            if i == 0:
                continue
            text = text_description[i]
            texts_list.append(text)
            boxe = text_bbox[i]['vertices']
            if len(boxe) == 4 and len(boxe[0]) == 2 and len(boxe[1]) == 2 and len(boxe[2]) == 2 and len(boxe[3]) == 2:
                boxes = np.array([boxe[0]['x'], boxe[0]['y'], boxe[3]['x'], boxe[3]['y'], boxe[2]['x'], boxe[2]['y'], boxe[1]['x'],
                     boxe[1]['y']])
                box = np.int0(boxes.reshape((4, 2)))
                boxes_list.append([np.min(box[:, 0]), np.min(box[:, 1]), np.max(box[:, 0]), np.max(box[:, 1])])
            else:
                boxes_list.append([])

        return text_description, text_bbox, boxes_list, texts_list, position_y

    def show_src(img_bgr, answer_boxes_list, gt_texts):
        a_len = len(answer_boxes_list)
        if a_len <= 0:
            return img_bgr
        h, w = img_bgr.shape[:2]
        # draw_size = int(max(h / 70, 10))
        draw_size = 30
        cv2_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(cv2_img)
        draw = ImageDraw.Draw(pil_img)
        font = ImageFont.truetype(ttf_path, draw_size, encoding="utf-8")
        for iy in range(a_len):
            if len(answer_boxes_list[iy]) < 4:
                continue
            # print(answer_boxes_list[iy])
            x1, y1, x2, y2 = answer_boxes_list[iy]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            label_str = gt_texts[iy]
            origin = (max(x1, x2), min(y1, y2))
            draw.rectangle([x1, y1, x2, y2], fill=None, outline='red')
            draw.text((x1, origin[1] - draw_size), label_str, (255, 0, 0), font=font)  # 参数1：打印坐标，参数2：文本，参数3：字体颜色，参数4：字体
        cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return cv2_img

    img_path=path
    img_path = img_path.replace("\\", "/")
    img_bgr = cv2.imread(img_path)

    analysis, json_path = text_recognize_post_local(img_path, True)

    text_description, text_bbox, boxes_list, texts_list, position_y = analysis_json_path(json_path)
    cv2_img = show_src(img_bgr, boxes_list, texts_list)
    cv2img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    im = Image.fromarray(cv2img)

    if im.mode != "RGB":
        im = im.convert('RGB')
    else:
        pass

    os.remove(json_path)
    return im
