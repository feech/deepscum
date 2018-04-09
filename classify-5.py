
# import pandas as pd
import numpy as np
import keras.layers.core as core
import keras.layers.convolutional as conv
from keras.layers import Conv2D, MaxPooling2D
import keras.models as models
import keras.utils.np_utils as kutils

from scipy import misc
import os
# from  distutils import filelist 

from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img


from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
import keras.layers.convolutional as conv
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense



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

cnn_rd.summary()
cnn_rd.compile(optimizer='adadelta', loss='mean_squared_error', metrics=['mae'])
# cnn_rd.compile(optimizer='rmsprop', loss='mean_squared_error', metrics=['accuracy'])
# cnn_rd.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
# cnn_rd.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])


# cnn_rd.fit(trainX, trainY, batch_size=40, epochs=30, verbose=1)

rr = cnn_rd.fit_generator(
    sis,
    steps_per_epoch=100,
    epochs=5,
    validation_data=sisv,
    validation_steps=10,
    verbose=2
    )

from datetime import date

os.chdir('C:/Users/Kirill/Documents/prj/deepscum')
cnn_rd.save_weights('5obj-detection-%s.h5'%(datetime.datetime.now().strftime('%Y%m%d-%H%M')
))
cnn_rd.load_weights('obj-detection-180409-5-obj.h5')

yPred = cnn_rd.predict(a)
yPred = cnn_rd.predict(imgs)

res = cnn_rd.evaluate_generator( sisv, steps=3)

if __name__ == '__main__':
