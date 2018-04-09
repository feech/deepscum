from scipy import misc
import math
import numpy
import subprocess
import time
import redis
import json
import io
import os
from PIL import Image, ImageDraw
import random
from functools import reduce
from scipy.misc import imsave

from predict_proc import class_array 

# if __name__ == '__main__':
os.chdir('C:/Users/Kirill/Documents/prj/deepscum')


# r = redis.StrictRedis(host='192.168.1.9', port=6379, db=0)
r = redis.StrictRedis(host='192.168.1.17', port=32768, db=0)


# update all known objects - set it if id doesn't exist
def assign_object_ids(r):
    objects = int(r.get('objects'))
    for i in r.scan_iter('survey:*:image:*:input'):
        inp = r.get(i)

        try:
            inp = json.loads(inp)
        except :
            # print(i, inp)
            continue

        updated = []
        for o in inp:
            if o.get('id') is None:
                o['id']=r.incr(b'objects')
            updated+=[o]

        r.set(i, json.dumps(updated))
    print('added %d objects'%(int(r.get(b'objects'))-objects))        



# extract samles

inp= r.get(next(r.scan_iter('survey:*:image:544:input')))
inp = json.loads(inp)

img= r.get(next(r.scan_iter('survey:*:image:544:data')))
img = Image.open(io.BytesIO(img))

# url
# get rect 0,0,w,100 - show url
# get rect w-60,0,60,h - if scroll exists -> show it else none. check there is no other objects here
# random rect 
def toi(o):
    return {'l':int(o['l']),
     't':int(o['t']),
     'w':int(o['w']),
     'h':int(o['h']),
     'x':int(o['x']),
     'y':int(o['y']),
     }

# segment intersection a-left end, a1-right end
def intersection_i(a, a1, b, b1):
    if a>b:
        a,a1,b,b1= b, b1, a, a1
    if a1<b:
        return None
    return b, min(a1,b1)

# segment intersection a-left, a1 -lenght of the segment
def intersection_w(a, a1, b, b1):
    if a>b:
        a,a1,b,b1= b, b1, a, a1
    if a+a1<b:
        return None
    return b,   min(b1, a+a1-b)

# intersection of rects. rect as l,t,w,h
def intersection(r1, r2):
    x,y=intersection_w(r1['l'], r1['w'], r2['l'], r2['w']), intersection_w(r1['t'], r1['h'], r2['t'], r2['h'])
    if x and y:
        return {'l':x[0],
        't': y[0],
        'w':x[1],
        'h':y[1]
        }
    return None

# r as l,t,w,h
def point_in_rect(x, y, r):
    return r['l']<x<r['l']+r['w'] and r['t']<y<r['t']+r['h']

def vertex_in_region(region, r):
    return (1 if point_in_rect(r['l']       , r['t']       , region) else 0) + \
           (1 if point_in_rect(r['l']+r['w'], r['t']       , region) else 0) + \
           (1 if point_in_rect(r['l']+r['w'], r['t']+r['h'], region) else 0) + \
           (1 if point_in_rect(r['l']       , r['t']+r['h'], region) else 0)

def s(o):
    if o is None:
        return 0
    return o['w']*o['h']    

rect={'l':0, 't':100, 'w':200, 'h': 230}

H,W = 768, 1024
h, w = 100, 100



def gen_rect():
    l = int(random.random()*(W- w-60))
    t = int(random.random()*(H- h - 100))+100
    return {'l':l, 't':t, 'w':w, 'h': h}

# find elements in the rect
# split by columns
# return target vector
def get_result(rect, inp):
    # select objects
    objects = []
    for i in inp:
        i1=toi(i)
        i2=intersection(rect,i1)
        if i2 is None:
            continue
        # if s(i2)>0:
            # print(i, i2, s(i2)/s(i1))
        if s(i2)/s(i1)>0.5 or point_in_rect(i1['x'], i1['y'], rect):
            objects.append(i)
            # print(i['id'])

    # split to columns
    columns = {}
    for o in objects:
        i1=toi(o)
        in_column = False
        for cc in columns:
            if cc[2]!=o['component']:
                continue
            if intersection_w(cc[0], cc[1], i1['l'], i1['w']):
                columns[cc].append(o)
                in_column =True
                break;
        if not in_column:
            columns[(i1['l'], i1['w'], o['component'])]=[o]

    # sort columns by y-coordinate
    for cc in columns:
        columns[cc] = sorted(columns[cc], key=lambda x: int(x['t']))
    # sort columns by x-coordinate
    columns = {i: columns[i] for i in sorted(columns, key=lambda x: (x[0], x[2]))}

    # build target result 
    # [probability, x/w, y/h, w/wr,h/hr, #class#,....]
    target = []
    for cc in columns:
        for o in columns[cc]:
            i1 = toi(o)
            target += [1.0, (i1['x']-rect['l'])/w, (i1['y']-rect['t'])/h, i1['w']/w, i1['h']/h]
            target += class_array(o['component'])
    return target



# nb = (l, t, l+w, t+h)
# img.crop(nb).save('saverandom.png')



from keras.utils import Sequence
import random


class SplitImageSequence(Sequence):

    def __init__(self, r=None, images=None, batch_size=32):
        self.r = r
        self.batch_size = batch_size
        # self.find_files(path)
        self.images=images
        self.empty = [0.]*16+[1.]
        self.debug = {}

    def __len__(self):
        return 1000000

    def __getitem__(self, idx):
        x, y = [], []
        id = random.choice(self.images)
        try:
            idi= next(r.scan_iter('survey:*:image:%s:input'%id))
            inp = r.get(idi)
            inp = json.loads(inp)
            idd = next(r.scan_iter('survey:*:image:%s:data'%id))
            img = Image.open(io.BytesIO(r.get(idd)))
            # allow_empty = False
            nonEmpty = 0
            iters=0
            while len(x)<self.batch_size:
                iters +=1
                rect = gen_rect()
                y1 = get_result(rect, inp)
                
                if len(y1)>0:
                    nonEmpty+=1


                if nonEmpty<6 and len(y1)==0 and iters< 2000:
                    continue

                if len(y1)==0:
                    nonEmpty=0 
                # allow_empty = not allow_empty

                assert len(y1)//17 < 6, 'too many objects in the rect %s in %s: %s'%(str(rect),id, str(y1))
                y += [y1+self.empty *(5-len(y1)//17)]
                nb = (rect['l'], rect['t'], rect['l']+rect['w'], rect['t']+rect['h'])
                x += [np.array(img.crop(nb))*(1./255)]
                # self.debug = [id, idi, inp, idd, rect]
        except Exception as x:
            print('on %s'%id)
            print(x)
            assert False
        return np.array(x), np.array(y)

sis= SplitImageSequence(r, images=['548', '565', '544', 
    '550', '552', '554', '558', '560', '563', '565'])
sisv= SplitImageSequence(r, images=['547', '559', '566'])
# for _ in range(50):
a,b = sisv.__getitem__(0)
a,b = sis.__getitem__(0)
    # a[0].save('sng.png')
    # if sum([b[0][a] for a in [16,33,50,67,84]])<5:
    #     break


# 
def save_ar_as_png(img_ar):
    imsave('test.png', img_ar*255.)





# load image from redis
def load_img(id):
    idd = next(r.scan_iter('survey:*:image:%s:data'%id))
    return Image.open(io.BytesIO(r.get(idd)))



def omit_less_significant_objects(vp):
    # skip less significant objects


def area(ar):
    # area for objectb
    # ar: [class, prob, (point), (size), idx]
    # return rect - (l, t, w, h)
    l,t = ar[2][0]-ar[3][0]//2, ar[2][1]-ar[3][1]//2
    return (l, t, l+ar[3][0], t+ar[3][1])


vpa = sorted([area(i) for i in vp], key=lambda x: x[0])

def draw_proof(imgt, vp):
    draw = ImageDraw.Draw(imgt)
    colors= {'radio': 'red', 'checkbox': 'blue'}
    
    for o in vp:
    # a = area(o)
        (x,y),(w,h)=o[2],o[3]
        color = colors.get(o[0], 'green')

        if x and y:
            draw.rectangle([x-w//2, y-h//2, x+w//2, y+h//2], outline=color)
            draw.line((x-5, y-5, x+5, y+5), fill=color)
            draw.line((x-5, y+5, x+5, y-5), fill=color)
        # if l and t:
            # draw.rectangle([l,t,l+w, t+h], outline='blue')
    del draw
    imsave('imgt.png', imgt)




sis= SplitImageSequence(r, images=['548', '565', '544', 
    '550', '552', '554', '558', '560', '563', '565',
    '539', '538', '568'])
sisv= SplitImageSequence(r, images=['547', '559', '566'])
# for _ in range(50):
a,b = sisv.__getitem__(0)
a,b = sis.__getitem__(0)


def prof(id):
    # id='570'
    img= r.get(next(r.scan_iter('survey:*:image:%s:data'%id)))
    img = Image.open(io.BytesIO(img))
    imgs=split_img_to_100x100(img)
    yPred = cnn_rd.predict(imgs)
    vp=select_valid_predictions(yPred)
    draw_proof(img, vp)


