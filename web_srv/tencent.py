# -*- coding: UTF-8 -*-
# _author_ = 'cz'
import glob
import json
import os
import io
import sys
import urllib,urllib2
import sys
sys.getdefaultencoding()
import imghdr
import cv2
import random
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import urllib2
from qcloud_image import Client

import requests
import re
import hashlib
import hmac
import requests
import base64
def draw_rect(path):
    def post1(path):
        appid = '1257232266'
        secret_id = 'AKIDHVaUCjAHGfw52mLjbHl3EMRsAHCvxnwu'
        secret_key = '2tmU02yqX2XqxshMp184pPuFQVPExVrL'
        bucket = 'test'
        client = Client(appid, secret_id, secret_key, bucket)
        client.use_http()
        client.set_timeout(30)
        vision_base_url ="http://recognition.image.myqcloud.com/ocr/handwriting"
        expired = time.time() + 259200
        current = time.time()
        rdm = ''.join(random.choice("0123456789") for i in range(10))
        info = "a=" + appid  +  "&b=" + bucket + "&k=" + secret_id + "&e=" + str(expired) + "&t=" + str(current) + "&r=" + str(
            rdm) + "&u=0&f="
        signindex = hmac.new(secret_key, info, hashlib.sha1).digest()
        sign = base64.b64encode(signindex + info)
        headers={
                        "Authorization": sign,
                        "Host": "recognition.image.myqcloud.com",
            }
        files={
            "appid":(None,appid),
            "bucket":(None,bucket),
            "image":("0057.jpg",open(path, 'rb'),"image/jpg")

            }
        r=requests.post(vision_base_url,files=files,headers=headers)
        responseinfo=r.content
        return responseinfo
    def find(txt):
        index=txt.find("itemcoord")
        txt=txt[index+9:]
        index=txt.find("x")
        txt1=[]
        index=index+3
        count=0
        txt1.append("x")
        for i in txt[index:index+4]:
            if(i=='\n' or i==','):
                count+=1
                break
            elif(i==" "):
                count += 1
                pass
            else:
                count += 1
                txt1.append(i)
        index=index+count
        txt=txt[index:]
        index=txt.find("y")
        index+=3
        txt1.append("y")
        count=0
        for i in txt[index:index+4]:
            if(i=='\n' or i==','):
                count+=1
                break
            elif(i=="\""):
                count += 1
                pass
            else:
                count += 1
                txt1.append(i)
        index=index+count
        txt=txt[index:]
        index=txt.find("width")
        index+=7
        txt1.append("width")
        count=0
        for i in txt[index:index+4]:
            if(i=='\n' or i==','):
                count+=1
                break
            elif(i==" "):
                count += 1
                pass
            elif(i=="\""):
                count+=1
                break
            else:
                count += 1
                txt1.append(i)
        index=index+count
        txt=txt[index:]
        index=txt.find("height")
        index+=8
        txt1.append("height")
        count=0
        for i in txt[index:index+4]:
            if(i=='\n' or i==','):
                count+=1
                break
            if(i=='}'):
                break
            elif(i==" " or i==":"):
                count += 1
                pass
            elif( i=="}"):
                count+=1
                break
            else:
                count += 1
                txt1.append(i)
        index=index+count
        txt=txt[index:]
        index=txt.find("itemstring")+13

        txt=txt[index:]
        txt1.append("word")
        while(1):
            index1=txt.find("character")
            index2=txt.find("candword")
            if index1==-1:
                break
            if index1<index2:
                if txt[index1+12]=="\"":
                    txt1.append(" ")
                    index = index1 + 12
                    txt = txt[index:]
                else:
                    txt1.append(txt[index1+12])
                    index=index1+12
                    txt=txt[index:]
            else:
                index=index2+11
                txt=txt[index:]
                break
        if(index1==-1):
            return txt1,txt,-1
        else:
            lenth=len(txt)
            return (txt1,txt,lenth)

    def finddsize(txt):
        index=txt.find("height")
        index += 8
        txt1=[]
        for i in txt[index:index + 4]:
            if (i == '\n' or i == ','):
                break
            if (i == '}'):
                break
            elif (i == " " or i == ":"):
                pass
            elif (i == "}"):
                break
            else:
                txt1.append(i)
            index = txt.rfind("height")
            index += 8
            txt2 = []
            for i in txt[index:index + 4]:
                if (i == '\n' or i == ','):
                    break
                if (i == '}'):
                    break
                elif (i == " " or i == ":"):
                    pass
                elif (i == "}"):
                    break
                else:
                    txt2.append(i)
        realdsize1=[]
        realdsize1=int(''.join(txt1[:]))
        realdsize2=[]
        realdsize2=int(''.join(txt2[:]))
        realdsize=0.6*(realdsize1+realdsize2)/2
        return  int(realdsize)

    responseinfo = post1(path)
    res_result = json.loads(responseinfo)
    items = res_result["data"]["items"]
    # dsize=finddsize(responseinfo)
    img = Image.open(path)
    dsize = 30
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('simhei.ttf', dsize)

    for item in items:
        itemstring = item["itemstring"]
        itemcoord = item["itemcoord"] # dict
        x_min = itemcoord["x"]
        y_min = itemcoord["y"]
        width = itemcoord["width"]
        height = itemcoord["height"]
        draw.rectangle([x_min, y_min, x_min+width, y_min+height], fill=None, outline=(255, 0, 0))
        draw.text([x_min, y_min-dsize], itemstring, (255, 0, 0), font=font)
    
    if img.mode != "RGB":
        img = img.convert('RGB')
    else:
        pass
    
    return img



