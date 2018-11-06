#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import time
import urllib
import json
import hashlib
import base64
import cv2
from PIL import Image, ImageDraw, ImageFont
import os


IMAGE_PATH = "/home/nd/project/ocr_recog_client/web_srv/eng2.png"

def detect_result(IMAGE_PATH):
    f = open(IMAGE_PATH, 'rb')
    file_content = f.read()
    base64_image = base64.b64encode(file_content)
    body = urllib.urlencode({'image': base64_image})

    url = 'http://webapi.xfyun.cn/v1/service/v1/ocr/handwriting'
    # url = 'http://webapi.xfyun.cn/v1/service/v1/ocr/general'
    api_key = 'f4659d73ff3c563cb1af5c950690eed6'
    param = {"language": "en", "location": "true"}

    x_appid = '5ad01b8a'
    x_param = base64.b64encode(json.dumps(param).replace(' ', ''))
    x_time = int(int(round(time.time() * 1000)) / 1000)
    x_checksum = hashlib.md5(api_key + str(x_time) + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib2.Request(url, body, x_header)
    result = urllib2.urlopen(req)
    result = result.read()
    # print result
    return result

def draw_rect(IMAGE_PATH):
    img = Image.open(IMAGE_PATH)
    w, h = img.size
    # dsize = int(max(w / 60), 30)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('simhei.ttf', 30)
    
    # print(w, h)
    result = detect_result(IMAGE_PATH)
    print(result)
    result_format = eval(result)
    block = result_format["data"]["block"][0]
    # print(type(block))
    lines = block["line"]

    words = []
    confs = []
    rects = []
    for i in range(len(lines)):
        line = lines[i]
        conf = line["confidence"]
        location = line["location"]
        x_min = location["top_left"]["x"]
        y_min = location["top_left"]["y"]
        x_max = location["right_bottom"]["x"]
        y_max = location["right_bottom"]["y"]
        rect = [x_min, y_min, x_max, y_max]
        # print("line: ", line["word"])
        word = [e["content"] for e in line["word"]]
        word = "".join(word)
        word = word.decode('utf-8')
        # print(conf)
        # print(rect)
        draw.rectangle([int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])], fill=None, outline=(0, 255, 0))
        draw.text([int(rect[0]), int(rect[1])-10], word, (255, 0, 0), font=font)

        words.append(word)
        confs.append(conf)
        rects.append(rect)

    # img.show()
    if img.mode != "RGB":
        img = img.convert('RGB')
    else:
        pass
    # img.save("result_6.jpg")
    return words, confs, rects, img

if __name__ == '__main__':

    # 单张测试
    result = detect_result(IMAGE_PATH)
    # print(result)
    words, confs, rects, img = draw_rect(IMAGE_PATH)
    for i in words:
        print(i)



    # 批量测试
    # orig_image_dir = "E:/workspace/180723/yangye-copy/"
    # save_image_dir = "E:/workspace/180723/yangye_result/"
    #
    # for file in os.listdir(orig_image_dir):
    #     print(file)
    #     IMAGE_PATH = os.path.join(orig_image_dir, file)
    #     # img = Image.open(IMAGE_PATH)
    #     # w, h = img.size
    #     # img = img.resize((w // 2, h // 2))
    #     words, confs, rects, img = draw_rect(IMAGE_PATH)
    #     save_image_path = os.path.join(save_image_dir, file)
    #     img.save(save_image_path)