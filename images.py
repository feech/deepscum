# get uniq screenshots 
#

import argparse 
import os

from scipy import misc
import math
import numpy
import subprocess
import time
import redis
import io

# os.chdir('C:/Users/Kirill/Documents/prj/deepscum')


def imageDif(f1, f2):
    th=5
    f1.shape=-1
    f2.shape=-1
    count = numpy.sum(numpy.greater(numpy.abs(f1-f2), th))
    return count, count*1.0/len(f1)

def isDif(f1, f2):
    f3=numpy.abs(f1-f2)
    f3.shape=-1
    idx = math.floor(f3.shape[0]*0.95)
    return f3[numpy.argpartition(f3, idx)[idx]]>0

# write to redis

# surveys
# surveys:images

# survey:id:date
# survey:id:url
# survey:id:user
# survey:id:image:id
# survey:id:image:id:date
# survey:id:image:id:number
# survey:id:image:id:class
# survey:id:image:id:validated
# survey:id:image:id:gzdata
# survey:id:image:id:input:[{x:,y:,component}, {l:,t:,w:,h:,component}]
# survey:id:image:id:object:{type, rect, waytoget}

# import redis
# r = redis.StrictRedis(host='192.168.5.136', port=32768, db=0)
# x = r.get('foo')


if __name__ == '__main__':

    last_face = None
    server = '192.168.5.136:1'
    password = 'ltkfqlt1'
    # parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('--index', type=int,
    #                     help='index for the first image')

    # args = parser.parse_args()
    # print(args.accumulate(args.integers))
    imageNumber =  0

    r = redis.StrictRedis(host='localhost', port=32768, db=0)
    survey_id = r.incr('surveys')
    r.set('survey:%d:date'%survey_id, time.asctime())

    # 0 - no changes
    # 1 - changes detected
    # 2.. waiting stable image
    state = None

    while True:
        
        time.sleep(1)
        screenName = 'survey-screen-%d.png'%imageNumber

        subprocess.run(['vncdo', '-s', server, '-p', password, 'capture', screenName], check=True)
        print(screenName)
        png_in_mem = open(screenName, 'rb').read()
        png_in_mem_file = io.BytesIO(png_in_mem)
        face = misc.imread(png_in_mem_file)

        if last_face is None:
            last_face = face

            image_id = r.incr('surveys:images')
            r.set('survey:%d:image:%d:date'%(survey_id, image_id), time.asctime())
            r.set('survey:%d:image:%d:data'%(survey_id, image_id), png_in_mem)

            imageNumber=1
            state = 0
            continue

        c, p = imageDif(last_face, face)
        print('difference %d - %f'%(c,p))
        #if isDif(last_face, face):
        if p > 0.05: 
            print('change is detected')
            last_face = face
            state = 1

        else:
            if state == 0:
                print('change isn\'t detected')
            else:
                state+=1
                print('wait stable image %d'%state)

            if state > 5:
                print('stable image')
                image_id = r.incr('surveys:images')
                r.set('survey:%d:image:%d:date'%(survey_id, image_id), time.asctime())
                r.set('survey:%d:image:%d:data'%(survey_id, image_id), png_in_mem)
                imageNumber+=1

                state = 0
            
            # count, rate = imageDif(last_face, face)


            # if rate > 0.01:

    

    # face = misc.face()
    # misc.imsave('data/screen.png', face) # First we need to create the PNG file

    # face = misc.imread('data/screen.png')
    # face1 = misc.imread('data/screen.jpg')
    # face1 = misc.imread('data/screen1.png')
    


