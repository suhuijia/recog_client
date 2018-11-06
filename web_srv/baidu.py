# -*- coding: UTF-8 -*-
import urllib,urllib2
import base64
import cv2
import numpy as np
import imghdr
import json
from PIL import Image,ImageDraw,ImageFont
def draw_rect(path):
    # ttf_path = "d:/orc//simhei.ttf"

    def get_token():
        host='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=tnH5yLrSCjsc4WMDWOX4RpWn&client_secret=eAK5R5mvEu7msTI6MrL6wG2eexZEnhVg'
        request = urllib2.Request(host)
        request.add_header('Content-Type', 'application/json; charset=UTF-8')
        response = urllib2.urlopen(request)
        content = response.read()
        # if (content):
        #     print(content)
        index1=content.find("access_token")
        index2=content.find("session_key")
        return(content[index1+15:index2-3])

    def post1(path):
        access_token = get_token()
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token=" + access_token
        # f=open(r'd:/data1/1/22.jpg','rb')
        f=open(path,'rb')
        im = base64.b64encode(f.read())
        params={'image':im}
        params=urllib.urlencode(params)
        request=urllib2.Request(url,params)
        request.add_header('Content-Type','application/x-www-form-urlencoded')
        response=urllib2.urlopen(request)
        content=response.read()
        return content

    def findnum(json):
        index=json.find("words_result_num")
        if(int(json[index+19])==0):
            num=-1
            return (num)
        else:
            index2=json.find("location")
            num=json[index+19:index2-21]
            return(num)



    def find(json):
        index=json.find("location")
        txt=json[index+8:]
        index=txt.find("width")
        txt1=[]
        index=index+7
        count=0
        txt1.append("width")
        for i in txt[index:index+5]:
            if(i=='\n' or i==','):
                count+=1
                break
            elif(i=="}"):
                count+=1
                break
            elif(i==" "or i==" "):
                count += 1
                pass
            else:
                # sys.stdout.write(i)#无空格输出
                count += 1
                txt1.append(i)
                # print(i,end='')
        # print(index,txt[index],index+count,txt[index+count])
        index=index+count
        txt=txt[index:]
        # print(index)
        index=txt.find("top")
        # print(index)
        # # print(index,txt[index])
        # d="0123456"
        # index=d.find("0")
        # print(index,d[index+1],d[index:])#[index:]计数
        index+=6#这个位置是个空格
        txt1.append("top")
        count=0
        for i in txt[index:index+5]:
            if(i=='\n' or i==','):
                count+=1
                break
            elif(i=="}"):
                count+=1
                break
            elif(i=="\""or i==" "):
                count += 1
                pass
            else:
                # sys.stdout.write(i)#无空格输出
                count += 1
                txt1.append(i)
                # print(i,end='')
        # print(index)
        # print(txt[index],count)
        index=index+count
        txt=txt[index:]
        # print(count)
        # print(index,txt[0],txt[1],txt[2])
        index=txt.find("left")
        # print(index)
        index+=6
        txt1.append("left")
        count=0
        for i in txt[index:index+5]:
            if(i=='\n' or i==','):
                count+=1
                break
            elif(i==" "or i==" "):
                count += 1
                pass
            elif(i=="}"):
                count+=1
                break
            elif(i=="\""):
                count+=1
                break
            else:
                # sys.stdout.write(i)#无空格输出
                count += 1
                txt1.append(i)
        # print(index,count,txt[index+count])
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
            elif(i==" " or i==" "):
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
        index=txt.find("words")+9

        txt=txt[index:]
        txt1.append("word")
        while(1):
            if(txt[0]=="\""and txt[1]=='}'):
                    txt=txt[1:]
                    break
            else:
                txt1.append(txt[0])
                txt=txt[1:]
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
                # sys.stdout.write(i)#无空格输出
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
                    # sys.stdout.write(i)#无空格输出
                    txt2.append(i)
        realdsize1=[]
        realdsize1=int(''.join(txt1[:]))
        realdsize2=[]
        realdsize2=int(''.join(txt2[:]))
        realdsize=0.6*(realdsize1+realdsize2)/2
        return  int(realdsize)

    responseinfo = post1(path)
    res_result = json.loads(responseinfo)
    items = res_result["words_result"]
    # dsize=finddsize(responseinfo)
    img = Image.open(path)
    dsize = 30
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('simhei.ttf', dsize)

    for item in items:
        itemstring = item["words"]
        itemcoord = item["location"] # dict
        x_min = itemcoord["left"]
        y_min = itemcoord["top"]
        width = itemcoord["width"]
        height = itemcoord["height"]
        draw.rectangle([x_min, y_min, x_min+width, y_min+height], fill=None, outline=(255, 0, 0))
        draw.text([x_min, y_min-dsize], itemstring, (255, 0, 0), font=font)
    
    if img.mode != "RGB":
        img = img.convert('RGB')
    else:
        pass

    return img


