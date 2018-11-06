# coding-utf-8

import os.path
import json
import tornado
from tornado import httpserver
from tornado import ioloop
from tornado import web
from tornado.options import define, options
import requests
import time
import base64
import cv2
import numpy as np

from web_srv import xunfei, baidu, tencent, google, nd


port = 9800
define("port", type=int, default=port, help='run a test server')


def check_dir(dir_path):
    if os.path.exists(dir_path):
        pass
    else:
        os.makedirs(dir_path)


def save_image_str(img_str, img_save_name):
    img_str = base64.b64decode(img_str)
    img_data = np.frombuffer(img_str, dtype='uint8')
    decimg = cv2.imdecode(img_data, 1)
    cv2.imwrite(img_save_name, decimg)


class OcrRecogHandler(web.RequestHandler):
    """docstring for ClassName"""
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        """get algorithm result"""
        save_recog_home = "./web_srv/static/img/"
        save_home = "./web_srv/load_images"
        check_dir(save_home)

        args = self.request.files.keys()
        print(args)
        print(self.request.arguments)
        timestamp = time.time()
        error_response = {}
        if "img_str" in args:
            imgfile = self.request.files.get('img_str')
            img_content = imgfile[0]['body']
            img_type = imgfile[0].filename.split('.')[-1]
            print(img_type)
            img_type_lower = img_type.lower()
            if img_type_lower not in ["jpg", "png", "jpeg", "bmp"]:
                error_response["error_code"] = 7001
                error_response["error_msg"] = "Data type is %s, need image." % img_type
                print(error_response)
                self.finish(json.dumps(error_response))
                return 
            else:
                save_file_name = time.strftime('%Y-%m-%d %H%M%S', time.localtime(timestamp)) + '.jpg'
                save_file_name_path = os.path.join(save_home, save_file_name)
                with open(save_file_name_path, 'wb') as f:
                    f.write(img_content)
                print(save_file_name_path)


        inter_args = self.request.arguments["interface"]
        print(inter_args)
        response = {}
        result = []
        
        if "1" in inter_args:
            img = nd.draw_rect(save_file_name_path)
            img.save(save_recog_home + "/ours/{}.jpg".format(str(int(timestamp))))
            result.append("ours")
        if "2" in inter_args:
            words, confs, rects, img = xunfei.draw_rect(save_file_name_path)
            img.save(save_recog_home + "/xunfei/{}.jpg".format(str(int(timestamp))))
            result.append("xunfei")
        if "3" in inter_args:
            img = baidu.draw_rect(save_file_name_path)
            img.save(save_recog_home + "/baidu/{}.jpg".format(str(int(timestamp))))
            result.append("baidu")
        if "4" in inter_args:
            img = tencent.draw_rect(save_file_name_path)
            img.save(save_recog_home + "/tencent/{}.jpg".format(str(int(timestamp))))
            result.append("tencent")
        if "5" in inter_args:
            img = google.draw_rect(save_file_name_path)
            img.save(save_recog_home + "/google/{}.jpg".format(str(int(timestamp))))
            result.append("google")
        if "0" in inter_args:
            img = nd.draw_rect(save_file_name_path)
            img.save(save_recog_home + "/ours/{}.jpg".format(str(int(timestamp))))
            result.append("ours")

            words, confs, rects, img = xunfei.draw_rect(save_file_name_path)
            img.save(save_recog_home + "/xunfei/{}.jpg".format(str(int(timestamp))))
            result.append("xunfei")

            img = baidu.draw_rect(save_file_name_path)
            img.save(save_recog_home + "/baidu/{}.jpg".format(str(int(timestamp))))
            result.append("baidu")

            img = tencent.draw_rect(save_file_name_path)
            img.save(save_recog_home + "/tencent/{}.jpg".format(str(int(timestamp))))
            result.append("tencent")

            img = google.draw_rect(save_file_name_path)
            img.save(save_recog_home + "/google/{}.jpg".format(str(int(timestamp))))
            result.append("google")

        response["filename"] = str(int(timestamp))
        response["success"] = 1
        response["result"] = result
        print(response)
        self.finish(json.dumps(response))


def main():

    application = web.Application([
        (r"/result/show/", OcrRecogHandler),
    ])

    ## ssl certificate
    # ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_ctx.load_cert_chain(os.path.join(os.path.abspath("."), "fullchain1.pem"),
    #                         os.path.join(os.path.abspath("."), "privkey1.pem"))
    # server = httpserver.HTTPServer(application, ssl_options=ssl_ctx)

    application.listen(port)
    print("Srv started at %d." % port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
