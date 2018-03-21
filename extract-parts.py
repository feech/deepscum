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

# if __name__ == '__main__':
os.chdir('C:/Users/Kirill/Documents/prj/deepscum')


# r = redis.StrictRedis(host='192.168.1.9', port=6379, db=0)
r = redis.StrictRedis(host='192.168.5.136', port=32768, db=0)


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




radio_sizes = []
m = {'radio': 0, 'checkbox': 0, 'show more': 0}
counter=0
for i in r.scan_iter('survey:*:image:*:input'):
    counter +=1
    inp = r.get(i)
    if len(inp)==0:
        continue
    try:
        inp = json.loads(inp)
        # continue
    # break

    # print(inp)
        for o in inp:
            if o.get('component') != 'radio':
                continue

            if o.get('w') or o.get('h') is None:
                radio_sizes += [(int(o.get('w')), int(o.get('h')))]

            # print(o)  
            # if o.get('x') is not None:
            #     m[o.get('component')] += 1
    except :
        # print(i, inp)
        counter +=0

# for a,b in m.items():
#     print(a, b['w'], b['h'])


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
'text input': (100,100),
}


os.chdir('C:/Users/Kirill/Documents/prj/deepscum')


base = 'data2/extract/'
for i in bounds:
    os.makedirs(base+i, exist_ok=True)
    os.makedirs(base+'f'+i, exist_ok=True)

for i in r.scan_iter('survey:*:image:*:input'):
    image_key=i.replace(b'input', b'data')
    inp = r.get(i)
    image_idx=i.split(b':')[3].decode()

    try:
        inp = json.loads(inp)
    except :
        # print(i, inp)
        continue

    image_in_mem = r.get(image_key)
    if image_in_mem is None:
        continue


    for o in inp:
        out_nmbr = o.get('id')
        if o.get('component') is None:
            print('component None', i)

        bo=bounds[o['component']]
        w = bo[0]
        h = bo[1]

        # l=int(o.get('l')) if o.get('l') else None
        # t=int(o.get('t')) if o.get('t') else None
        # w=int(o.get('w'))
        # h=int(o.get('h'))
        x=int(o.get('x')) if o.get('x') else None
        y=int(o.get('y')) if o.get('y') else None


        if x is None or y is None:
            continue

        nb = [x-w//2, y-h//2]
        nb +=[nb[0]+w, nb[1]+h]

        
        # im_pos_in_origin= (l, t, w, h)
        # center_in_origin = (im_pos_in_origin[0]+im_pos_in_origin[2]//2, im_pos_in_origin[1]+im_pos_in_origin[3]//2)
        # bounds_in_crop = (im_pos_in_origin[0]-nb[0], im_pos_in_origin[1]-nb[1],
        #                 im_pos_in_origin[0]-nb[0]+im_pos_in_origin[2], im_pos_in_origin[1]-nb[1]+im_pos_in_origin[3])

        fname = '%s%s/%s-%d.png'%(base,o['component'], image_idx, out_nmbr)
        face = Image.open(io.BytesIO(image_in_mem))
        draw = ImageDraw.Draw(face)
        if x and y:
            draw.rectangle([x-w//2, y-h//2, x+w//2, y+h//2], outline='red')
            draw.line((x-5, y-5, x+5, y+5), fill='red')
            draw.line((x-5, y+5, x+5, y-5), fill='red')
        # if l and t:
            # draw.rectangle([l,t,l+w, t+h], outline='blue')
        del draw
        face.crop(nb).save(fname)

        l = int(random.random()*(1024- w))
        t = int(random.random()*(768- h))
        nb = (l, t, l+w, t+h)

        fname = '%sf%s/%s-%d.png'%(base,o['component'], image_idx, out_nmbr)
        face = Image.open(io.BytesIO(image_in_mem))
        face.crop(nb).save(fname)





# extract samles
# 548, 565


for i in r.scan_iter('survey:*:image:565:input'):
    inp = r.get(i)
    inp = json.loads(inp)

img=None
for i in r.scan_iter('survey:*:image:565:data'):
    img = Image.open(io.BytesIO(r.get(i)))

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
h, w = 550, 550
l = int(random.random()*(W- w-60))
t = int(random.random()*(H- h - 100))+100
rect = {'l':l, 't':t, 'w':w, 'h': h}


def get_result(inp):
    # select objects
    objects = []
    for i in inp:
        i1=toi(i)
        i2=intersection(rect,i1)
        # if s(i2)>0:
            # print(i, i2, s(i2)/s(i1))
        if s(i2)>0.5 and vertex_in_region(rect, i1)>=3:
            objects.append(i)

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

    # buiild target result 
    # [[probability, x/w, y/h, w/wr,h/hr, #class#],....]
    target = []
    for cc in columns:
        for o in columns[cc]:
            i1 = toi(o)
            target += [s(intersection(rect,i1))/s(i1), (i1['x']-rect['l'])/w, (i1['y']-rect['t'])/h, i1['w']/w, i1['h']/h]
            target += class_array(o['component'])
    return target

def class_array(s):
    classes = ['text input', 'checkbox', 'radio', 'next button', 'scrolling', 'url', 'show more', 'back button', 'check text', 'select', 'select-list']
    res = [0.]*(len(classes)+1)
    try:
        res[classes.index(s)]=1.
    except ValueError:
        res[-1]=1.
    return res


nb = (l, t, l+w, t+h)
img.crop(nb).save('saverandom.png')


