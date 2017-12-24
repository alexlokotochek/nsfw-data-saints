# coding: utf-8

# from grpc.beta import implementations
# import tensorflow as tf

# from tensorflow_serving.apis import predict_pb2
# from tensorflow_serving.apis import prediction_service_pb2
from keras.applications.inception_v3 import InceptionV3
#, preprocess_input
import numpy as np

import requests
import pycurl
import os
from PIL import Image

import subprocess
import json

import json
from StringIO import StringIO
import pycurl

from urllib2 import urlopen
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

model=InceptionV3(include_top=True, weights='imagenet', classes=1000)

with open('keys.txt','r') as f:
    keys=np.array(f.read().split('\n'))
    

from PIL import Image
import tensorflow as tf

graph = tf.get_default_graph()
import cv2
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

from urllib2 import urlopen
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

tok1='&v=5.69&access_token=709f696035fd55211f90869b5e9a5c634c694147dd80b2567c386c63b0b7b9ad658a0d035c3ff360aca67'
tok2='&v=5.69&access_token=abb54876ef302a77472ceb2135b1ec21edc91648b810ecb695fb1431a7e0eb6010757de63ea47e13caa46'
tok3='&v=5.69&access_token=49a54eefeb367cf8aef33799a15f29cdef03f6879bdafc9066f24f851182a0945426aea52b8e2a73e468d'
tok = [tok1,tok2,tok3]
meth_gr='https://api.vk.com/method/photos.getAll.json?owner_id='
of = '&count=200&offset='



tf.app.flags.DEFINE_string('server', 'localhost:9000', 'PredictionService host:port')
tf.app.flags.DEFINE_string('image', '', 'path to image in JPEG format')
FLAGS = tf.app.flags.FLAGS


host, port = 'localhost', '9000'
channel = implementations.insecure_channel(host, int(port))
stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

c = pycurl.Curl()

def get_user_photos(ids):
    ids = str(ids)
    res_p = []
    res_d = []
    offset = 0
    m = 0

    while (True):
        req = meth_gr+ids+of+str(offset)+tok[m]
        req= urlopen(req)
        data = req.read()
        print(data)
        try:
            data = json.loads(data.decode())
        except:
            data = json.loads(data)
        coun = data['response']['count']
        d = coun-len(res_p)
        if d <=200:
            for i in range(d):
                res_p += [data['response']['items'][i]['photo_604']]
                res_d += [data['response']['items'][i]['date']]
            break
        else:
            for i in range(200):
                res_p += [data['response']['items'][i]['photo_604']]
                res_d += [data['response']['items'][i]['date']]
            offset += 200
            m = (m + 1) % 3
    return(res_p,res_d)


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
    return buffer.getvalue(), buffer

def preprocess_input(x):
    y = x / 255.
    y = y - 0.5
    y = y * 2.
    return y


def all_images(bufs):
    global graph
    with graph.as_default():
        new_images = []
        for image in bufs:
            image = Image.open(image)
            image=cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            image=np.array([cv2.resize(image,(100,100))])
            image = preprocess_input(image)[0]
            new_images += [image]
        scores=model.predict(np.array(new_images))
        answers = []
        for i, score in enumerate(scores):
            nv = {}
            for key,sc in zip(keys,score):
                if sc > 0.15 and key in alco_tags:
                    nv[key] = float(sc)
            answers += [nv]
        return answers
            
        

def get_alcourls_by_urls(img_urls):
    bufs = []
    for u in img_urls:
        img, image_buf = download_img(u)
        bufs += [image_buf]
        
    ai = all_images(bufs)
    show_imgs = []
    for i, a in enumerate(ai):
        if len(a) > 0:
            show_imgs += [img_urls[i]]
    return show_imgs

        



class MyFormHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<html><body><form action="/alco-detector" method="POST">'
                   '<input type="text" name="message">'
                   '<input type="submit" value="photolink">'
                   '</form></body></html>')

    def post(self):
        self.set_header("Content-Type", "text/html")
        msg = self.get_body_argument("message")
        user_id = msg
        photos, dates = get_user_photos(user_id)
        print len(photos), 'photos'
        photos = photos[:100]
        alcourls = get_alcourls_by_urls(photos)
        for img_url in alcourls:
            self.write("""<br><img src="{0}"/>""".format(img_url))


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/alco-detector", MyFormHandler),
        ]
        tornado.web.Application.__init__(self, handlers)


def main():
    app = Application()
    loop = IOLoop.instance()
    app.listen(8110)
    loop.start()

if __name__=='__main__':
    main()



