#coding=utf-8

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.options import define, options
import json
import uuid

port = 9600

from PIL import Image
import time
import torch
from torch.autograd import Variable
from torchvision import transforms
import numpy as np
import torchvision.models as models


name_file = "./labels-c206.txt"
checkpoint_file = "./model_best-c206.pth.tar"
num_classes = 206
use_cuda = False

with open(name_file, "r") as f:
    data = f.readlines()

labels = []
for li in data:
    line = li.strip()
    chi_name = line
    labels.append(chi_name)

normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225])

test_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    normalize
])


# create model
model_ft = models.resnet18(pretrained=True)
num_ftrs = model_ft.fc.in_features
model_ft.fc = torch.nn.Linear(num_ftrs, num_classes)
model = model_ft

if use_cuda:
    model = torch.nn.DataParallel(model).cuda()
    checkpoint = torch.load(checkpoint_file)
    model.load_state_dict(checkpoint['state_dict'])
else:
    checkpoint = torch.load(checkpoint_file, map_location=lambda storage, loc: storage)
    # original saved file with DataParallel
    state_dict = checkpoint['state_dict']
    # create new OrderedDict that does not contain `module.`
    from collections import OrderedDict

    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = k[7:]  # remove `module.`
        new_state_dict[name] = v
    # load params
    model.load_state_dict(new_state_dict)


print("=> loaded checkpoint.")


for param in model.parameters():
    param.requires_grad = False
model.eval()


def preprocess(image, transformer):
    x = transformer(image)
    return Variable(x.unsqueeze(0))


def softmax(x):
    return np.exp(x) / np.sum(np.exp(x), axis=0)


define("port", default=port, help='run a test')


class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, *args, **kwargs):
        print self.request
        imgfile = self.request.files.get('up_img')
        with open('./cache/' + imgfile[0]['filename'], 'wb') as f:
            f.write(imgfile[0]['body'])

        img_path = './cache/' + imgfile[0]['filename']
        start = time.time()
        image = Image.open(img_path).convert('RGB')
        if test_transform is not None:
            image = test_transform(image)
        inputs = image
        inputs = Variable(inputs, volatile=True)
        if use_cuda:
            inputs = inputs.cuda()
        inputs = inputs.view(1, inputs.size(0), inputs.size(1), inputs.size(2))

        outputs = model(inputs)
        softmax_res = softmax(outputs.data.cpu().numpy()[0])
        score_np = np.array(softmax_res)
        ind = np.argsort(score_np)
        topk = list(ind[-10:])  # top5
        topk.reverse()

        print "time of reference: ", time.time() - start

        print "topk idxs: ", topk

        ret = []
        for idx in topk:
            print("idx:", idx)
            print(labels[idx+1])
            print(softmax_res[idx])
            print idx, "      ", idx, "      ", labels[idx+1], softmax_res[idx]
            ret.append((labels[idx+1], "%f"%softmax_res[idx]))

        response = {}
        response["success"] = 0
        response["result"] = ret
        self.finish(json.dumps(response))



application = tornado.web.Application([
    (r"/factory_ir/", MainHandler),

])

if __name__ == "__main__":
    application.listen(port)
    print "Srv started at %d." % port
    tornado.ioloop.IOLoop.instance().start()
