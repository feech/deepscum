import argparse 
import os

from scipy import misc
import math
import numpy
import subprocess
import time
import gzip
import redis
import io

os.chdir('C:/Users/Kirill/Documents/prj/deepscum')

# f= open('file.png', 'rb')
# fs = f.read()
# likefile = io.BytesIO(fs)
# face1 = misc.imread(likefile)


# output = StringIO.StringIO()
# output.write('First line.\n')


# face = misc.face()
r = redis.StrictRedis(host='192.168.1.17', port=32768, db=0)# a = misc.imsave('data/screen.png', face) # First we need to create the PNG file
# r = redis.StrictRedis(host='localhost', port=32768, db=0)# a = misc.imsave('data/screen.png', face) # First we need to create the PNG file

face = misc.imread('data/screen.png')
# face = misc.imread('data/survey-screen-0.png')
# face1 = misc.imread('data/screen.jpg')
# face1 = misc.imread('data/screen1.png')

survey_id = r.incr('surveys')
r.set('survey:%d:date'%survey_id, time.asctime())


for i in range(0,8):
    f= open('data/shop0223/survey-screen-%d.png'%i, 'rb')
    fs = f.read()
    image_id = r.incr('surveys:images')
    # r.set('survey:%d:image:%d:date'%(survey_id, image_id), time.asctime())
    r.set('survey:%d:image:%d:data'%(survey_id, image_id), fs)



for i in range(0,46):
    print('>>survey-screen-%d.png'%i)
    face = misc.imread('data/lott/survey-screen-%d.png'%i)
    image_id = r.incr('surveys:images')
    r.set('survey:%d:image:%d:date'%(survey_id, image_id), time.asctime())
    r.set('survey:%d:image:%d:gzdata'%(survey_id, image_id), gzip.compress(face))
    print('<<survey-screen-%d.png'%i)


cursor =0           
while True:
    cursor, li = r.scan(cursor, 'survey:1:*:gzdata')
    print('cursor %d-%d'%(cursor, len(li)))
    if cursor == 0:
        break

    if len(li) == 0:
        continue

    for i in li:
        print(i)
print('stop')
