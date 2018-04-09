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




# r = redis.StrictRedis(host='192.168.1.9', port=6379, db=0)



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

if __name__ == '__main__':
    os.chdir('C:/Users/Kirill/Documents/prj/deepscum')
    r = redis.StrictRedis(host='192.168.1.17', port=32768, db=0)
    assign_object_ids(r)