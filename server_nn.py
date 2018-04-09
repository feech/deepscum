from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from http.server import SimpleHTTPRequestHandler
import json
import redis
import keras.models as models
import keras.layers.convolutional as conv
from keras.layers import Conv2D, MaxPooling2D
import numpy as np
import keras.layers.core as core
from PIL import Image, ImageDraw
import io
from functools import reduce

H,W = 768, 1024
h, w = 100, 100

cnn_rd = None
r=None

class NN_Handler(BaseHTTPRequestHandler):
    # def __init__(self):
    #     self.commands=['GET']
    def do_GET(self):
        # take image from redis
        # split, predict
        # send json-back
        print(self.path)
        im_id = self.path.split('/')[-1]
        # imgt = load_img(im_id)
        imgi= r.get(next(r.scan_iter('survey:*:image:%s:data'%im_id)))
        imgt = Image.open(io.BytesIO(imgi))
        X = split_img_to_100x100(imgt)
        yPred = cnn_rd.predict(X)
        vp = select_valid_predictions(yPred)

        input = [{'l':i[0], 't':i[1], 'w':o[3][0], 'h':o[3][1], 'x':o[2][0], 'y':o[2][1], 'component':o[0]} for i,o in [(area(o), o) for o in vp]]
        result = {'date': 'xz',
            'id': im_id,
            'survey': "",
            'input': input}


        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8')) 

def getModel():
    cnn_rd = models.Sequential()
    cnn_rd.add(conv.Convolution2D(64, (3, 3),  activation="relu", input_shape=(100, 100, 3), padding='same'))
    cnn_rd.add(conv.MaxPooling2D(strides=(2,2)))

    cnn_rd.add(conv.Convolution2D(64, (3, 3), activation="relu", padding='same'))
    cnn_rd.add(conv.MaxPooling2D(strides=(2,2)))

    cnn_rd.add(conv.Convolution2D(256, (3, 3), activation="relu", padding='same'))
    cnn_rd.add(conv.MaxPooling2D(strides=(2,2)))

    cnn_rd.add(core.Flatten())
    # cnn_rd.add(core.Dropout(0.2))
    cnn_rd.add(core.Dense(1024, activation="relu")) # 4096
    # cnn_rd.add(core.Dense(1, activation="softmax"))
    # cnn_rd.add(core.Dropout(0.5))
    cnn_rd.add(core.Dense(85, activation="sigmoid"))
    # cnn_rd.add(core.Activation('sigmoid'))
    return cnn_rd



def get_classes():
    return ['text input', 'checkbox', 'radio', 'next button', 'scrolling', 'url', 'show more', 'back button', 'check text', 'select', 'select-list', None]

def class_array(s):
    classes = get_classes()
    res = [0.]*(len(classes))
    try:
        res[classes.index(s)]=1.
    except ValueError:
        res[-1]=1.
    return res


def split_img_to_100x100(img):
    # split full image to pieces 
    # return array of 100x100 images
    # uses external defined w,h 

    imgs = []
    for x in range(0,1023,86):
        for y in range(0,767, 83):
            nb= (x,y, x+w, y+h)
            imgs += [np.array(img.crop(nb))*(1./255.)]
    return np.array(imgs)

def i_to_lt(i):
    return (i//10)*86, (i%10)*83

# ar - array of classes
def extract_class(ar):
    # 1. -- <required> if prob of the object detected less 0.5 - return None
    # 2. if there are some objects with obj-prob more 0.4 - return None
    if reduce(lambda s, i: s+1 if i>0.4 else s, ar, 0)>1:
        return None, ar[-1]
    return max(zip(get_classes(), ar), key=lambda x: x[1])

def extract_position(ar, dim):
    # ar: [prob, x%, y%, w%, h%]
    # return (x,y), (w,h)
    return (round(ar[1]*dim[0]), round(ar[2]*dim[1])), (round(ar[3]*dim[0]), round(ar[4]*dim[1]))

def extract(ar, img_ar_shape=(h, w)):
    # return [(class, prob, (x,y), (w,h))]
    result = []
    for i in range(0,84,17):
        cl, prob = extract_class(ar[i+5:i+17]) if ar[i]>0.5 else (None, ar[i+16])
        point, size = extract_position(ar[i:i+5], img_ar_shape) if cl else (None, None)
        result += [(cl, round(100.*prob), point, size)]
    return result

def select_valid_predictions(yPred):
    # select all-significant objects
    # return [(class, prob, (x,y), (w,h))]
    valid_predictions = []
    for i, e in enumerate(yPred):
        l,t = i_to_lt(i)
        for o in extract(e):
            if o[0] is None or o[1]<50:
                continue
            valid_predictions += [(o[0], o[1], (o[2][0]+l, o[2][1]+t), o[3], i)]
    return sorted(valid_predictions, key=lambda x: -x[1])

def area(ar):
    # area for objectb
    # ar: [class, prob, (point), (size), idx]
    # return rect - (l, t, w, h)
    l,t = ar[2][0]-ar[3][0]//2, ar[2][1]-ar[3][1]//2
    return (l, t, l+ar[3][0], t+ar[3][1])


if __name__ == '__main__':
    r = redis.StrictRedis(host='192.168.1.17', port=32768, db=0)
    cnn_rd = getModel()
    cnn_rd.load_weights('obj-detection-180409-5-obj.h5')
    http = HTTPServer(('localhost', 5343), NN_Handler)
    http.serve_forever()
    # http.handle_request()

# http = HTTPServer(('localhost', 5342), NN_Handler)
# for i in range(2):
#     print('iteration %d'%i)
#     http.handle_request()


