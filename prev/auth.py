# coding: utf-8

from grpc.beta import implementations
import tensorflow as tf

from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

import requests
import pycurl
import os
from PIL import Image

import subprocess
import json

import json
from StringIO import StringIO
import pycurl


import json
import os
import socket
import sys
from copy import deepcopy
import pickle
import numpy as np
import tornado
import tornado.web
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.ioloop import IOLoop
from tornado.ioloop import PeriodicCallback
import requests

alco_tags = {
    'beaker',
    'beer bottle',
    'beer glass',
    'bottlecap',
    'cocktail shaker',
    'coffee mug',
    'corkscrew, bottle screw',
    'cup',
    'eggnog',
    'measuring cup',
    'mixing bowl',
    'pill bottle',
    'pop bottle, soda bottle',
    'red wine',
    'restaurant, eating house, eating place, eatery',
    'schooner',
    'water bottle',
    'water jug',
    'whiskey jug',
    'wine bottle',
}

tf.app.flags.DEFINE_string('server', 'localhost:9000', 'PredictionService host:port')
tf.app.flags.DEFINE_string('image', '', 'path to image in JPEG format')
FLAGS = tf.app.flags.FLAGS


host, port = 'localhost', '9000'
channel = implementations.insecure_channel(host, int(port))
stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

c = pycurl.Curl()

from urllib2 import urlopen

tok0='&v=5.69&access_token='
tok1='&v=5.69&access_token=709f696035fd55211f90869b5e9a5c634c694147dd80b2567c386c63b0b7b9ad658a0d035c3ff360aca67'
tok2='&v=5.69&access_token=abb54876ef302a77472ceb2135b1ec21edc91648b810ecb695fb1431a7e0eb6010757de63ea47e13caa46'
tok3='&v=5.69&access_token=49a54eefeb367cf8aef33799a15f29cdef03f6879bdafc9066f24f851182a0945426aea52b8e2a73e468d'
tok = [tok1,tok2,tok3]
meth_gr='https://api.vk.com/method/photos.getAll.json?owner_id='
of = '&count=200&offset='

def get_photos(ids, token):
    ids = str(ids)
    res_p = []
    offset = 0
    m = 0

    while (True):
        req = meth_gr+ids+of+str(offset)+tok0+token#tok[m]
        req = urlopen(req)
        req = req.read()
        try:
            req = req.decode()
        except:
            pass
        data = json.loads(req)
        coun = data['response']['count']
        d = coun-len(res_p)
        if d <=200:
            for i in range(d):
                try:
                    res_p += [data['response']['items'][i]['photo_604']]
                except:
                    pass
            break
        else:
            for i in range(200):
                try:
                    res_p += [data['response']['items'][i]['photo_604']]
                except:
                    pass
            offset += 200
            #m = (m + 1) % 3
    return res_p


def download_img(img_url):
    from StringIO import StringIO
    import pycurl
    buffer = StringIO()
    c.setopt(c.URL, img_url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(c.SSL_VERIFYPEER, 0) # That is you key line for this purpose!

    c.perform()

    #im = Image.open(buffer,)
    return buffer.getvalue()


def all_photos(img_urls):
    imgs = map(download_img, img_urls)
    result = get_trues_alco(imgs, img_urls)
    return result


def get_trues_alco(imgs, phts):
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'inception'
    request.model_spec.signature_name = 'predict_images'
    request.inputs['images'].CopyFrom(
        tf.contrib.util.make_tensor_proto(np.array(imgs), shape=[len(imgs)]))
    result = stub.Predict(request, 360) # 6 minutes timeout
    all_tags= result.outputs['classes'].string_val
    alco_photos = []
    for i in range(5*len(imgs)//5):
        tags = all_tags[5*i : 5*(i+1)]
        if len(set(tags)&alco_tags) > 0:
            alco_photos += [phts[i]]
    return alco_photos
    


class PhotosHandler(tornado.web.RequestHandler):
    # def get(self):
    #     token=self.get_argument('access_token')
    #     print(token)
    #     self.application.token=token
    #     self.write('<html><body><form action="/alco-detector" method="POST">'
    #                '<input type="text" name="message">'
    #                '<input type="submit" value="Submit">'
    #                '</form></body></html>')

    def get(self):
        token=self.get_argument('access_token')
        print(token)
        self.set_header("Content-Type", "text/html")
        self.write(token)
        # msg = self.get_body_argument("message")
        # user_id = msg
        # print('user:', user_id)
        # phts = get_photos(user_id)[:100]
        # print('photos:', len(phts))
        # res = all_photos(phts)
        # print('alco_photos:', len(res), '/', len(phts))
        # for img_url in res:
        #     self.write("""<br><img src="{0}"/>""".format(img_url))



class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/html")
        self.write('<html><body><form method="POST" action="https://oauth.vk.com/authorize?client_id=6309323&display=mobile&redirect_uri=http://ec2-34-242-141-128.eu-west-1.compute.amazonaws.com/authorize&scope=photos&response_type=code&v=5.69">'
                   '<input type="submit" value="authorize me!">'
                   '</form></body></html>')


class AuthorizedHandler(tornado.web.RequestHandler):
    def get(self):
        print('authorized!')
        self.set_header("Content-Type", "text/html")
        code = self.get_argument("code")
        print(code)

        url = 'https://oauth.vk.com/access_token?client_id=6309323&client_secret=BUW4dzvk0XS0ifyyynps&redirect_uri=http://ec2-34-242-141-128.eu-west-1.compute.amazonaws.com/authorize&code='+code  + '">'
        text = requests.get(url).text
        text = json.loads(text)
        print(text)
        user_id, access_token = text['user_id'], text['access_token']
        phts = get_photos(user_id, access_token)[:100]
        res = all_photos(phts)
        print('alco_photos:', len(res), '/', len(phts))
        for img_url in res:
            self.write("""<br><img src="{0}"/>""".format(img_url))




class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/alco-detector", PhotosHandler),
            (r"/hello", HelloHandler),
            (r"/authorize", AuthorizedHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    loop = IOLoop.instance()
    app.listen(80)
    loop.start()

if __name__=='__main__':
    main()


