# coding=utf-8

import os
import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import json
import urllib
import urllib2

IMAGE_PATH = "/home/nd/project/ocr_recog_client/web_srv/eng2.png"

def detect_result(IMAGE_PATH):
    """"""
    url = "http://192.168.46.40:3699/detector_ks/"

    f = open(IMAGE_PATH, 'rb')
    img = base64.b64encode(f.read())

    params = {
        # 'img_str': img,
        'upl_img': img,
    }

    params = urllib.urlencode(params).encode(encoding='utf-8')
    request = urllib2.Request(url=url, data=params)
    response = urllib2.urlopen(request)
    content = response.read().decode()

    if content:
        # print(content)
        print(type(content))

    return content


def draw_rect(IMAGE_PATH):
    """"""
    img = Image.open(IMAGE_PATH)
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('simhei.ttf', 20)

    content = detect_result(IMAGE_PATH)
    content = eval(content)
    result = content["result"]

    for i in range(len(result)):
        box = result[i]["box"]
        label = result[i]["label"]
        # print(box, label)
        draw.rectangle([int(box[0]), int(box[1]), int(box[2]), int(box[3])], fill=None, outline=(0, 255, 0))
        draw.text([int(box[0]), int(box[1])-10], label, (255, 0, 0), font=font)

    # img.show()
    if img.mode != "RGB":
        img = img.convert('RGB')
    else:
        pass

    return img


if __name__ == '__main__':

    draw_rect(IMAGE_PATH)