from keras.applications.vgg19 import VGG19
from keras.preprocessing import image
from keras.applications.vgg19 import preprocess_input
from keras.models import Model
import numpy as np

import os

os.chdir('C:/Users/Kirill/Documents/prj/deepscum')

base_model = VGG19(weights='imagenet')


o = np.ones((5,3))
o = o*2

o[1,1:]/=3