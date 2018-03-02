from scipy import misc
import math
import numpy
import subprocess
import time
import redis
import json
import io
import os
from PIL import Image
import random

if __name__ == '__main__':

m = {}
r = redis.StrictRedis(host='192.168.5.136', port=32768, db=0)

for i in r.scan_iter('survey:*:image:*:input'):
    inp = r.get(i)
    try:
        inp = json.loads(inp)
    except :
        # print(i, inp)
        continue

    # print(inp)
    for o in inp:
        # print(o)  
        old = m.get(o['component'])
        if old is None:
            o['keyw']= i
            o['keyh'] = i
            m[o['component']]=o
        else:
            if int(old['w']) < int(o['w']):
                old['keyw']=i
                old['w']=o['w']

            if int(old['h']) < int(o['h']):
                old['keyh'] = i
                old['h'] = o['h']

for a,b in m.items():
    print(a, b['w'], b['h'])


bounds = {
    
'radio': ( 66, 55),
'checkbox': ( 66, 55),

'next button': ( 340, 85),
'show more': ( 340, 85),
'back button': ( 340, 85),
'check text': (  383, 25),

'scrolling': ( 30, 550),
'select': (264, 44),
'select-list': (265, 275),
}


os.chdir('C:/Users/Kirill/Documents/prj/deepscum')

for i in bounds:
    os.makedirs('data/extract/'+i, exist_ok=True)
    os.makedirs('data/extract/f'+i, exist_ok=True)

for i in r.scan_iter('survey:*:image:*:input'):
    image_key=i.replace(b'input', b'data')
    inp = r.get(i)
    image_idx=i.split(b':')[3]

    try:
        inp = json.loads(inp)
    except :
        # print(i, inp)
        continue

    image_in_mem = r.get(image_key)
    if image_in_mem is None:
        continue


    for o in inp:
        # if o['component']=='show more':
        #     continue
        bo=bounds[o['component']]
        l=o['l']
        t=o['t']
        w=int(o['w'])
        h=int(o['h'])
        x=o['x']
        y=o['y']

        l = int(l) if l else int(x)- (w+1)//2
        t = int(t) if t else int(y)- (h+1)//2

        
        im_pos_in_origin= (l, t, w, h)
        center_in_origin = (im_pos_in_origin[0]+im_pos_in_origin[2]//2, im_pos_in_origin[1]+im_pos_in_origin[3]//2)
        bo=bounds[o['component']]
        nb = (center_in_origin[0]-bo[0]//2, center_in_origin[1]-bo[1]//2, center_in_origin[0]-bo[0]//2+bo[0], center_in_origin[1]-bo[1]//2+bo[1])
        # bounds_in_crop = (im_pos_in_origin[0]-nb[0], im_pos_in_origin[1]-nb[1],
        #                 im_pos_in_origin[0]-nb[0]+im_pos_in_origin[2], im_pos_in_origin[1]-nb[1]+im_pos_in_origin[3])

        fname = 'data/extract/%s/%s-%d-%d-%d-%d.png'%(o['component'], image_idx.decode(), 
            bo[0]//2,bo[1]//2,im_pos_in_origin[2],im_pos_in_origin[3])
        face = Image.open(io.BytesIO(image_in_mem))
        face.crop(nb).save(fname)

        # im_pos_in_origin= (int(random.random()*(1024- im_pos_in_origin[2])),
        #     int(random.random()*(768- im_pos_in_origin[3])),
        #     im_pos_in_origin[2], im_pos_in_origin[3])

        # center_in_origin = (im_pos_in_origin[0]+im_pos_in_origin[2]//2, im_pos_in_origin[1]+im_pos_in_origin[3]//2)
        x = int(random.random()*(1024- bo[0]))
        y = int(random.random()*(768- bo[1]))
        nb = (x, y, x+bo[0], y+bo[1])
        # bounds_in_crop = (3,4,
        #                 3+im_pos_in_origin[2], 4+im_pos_in_origin[3])

        fname = 'data/extract/f%s/%s-%d-%d-%d-%d.png'%(o['component'], image_idx.decode(), 
            bo[0]//2,bo[1]//2,im_pos_in_origin[2],im_pos_in_origin[3])
        face = Image.open(io.BytesIO(image_in_mem))
        face.crop(nb).save(fname)