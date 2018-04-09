# import pandas as pd
import numpy as np
import keras.layers.core as core
import keras.layers.convolutional as conv
from keras.layers import Conv2D, MaxPooling2D
import keras.models as models
import keras.utils.np_utils as kutils

from scipy import misc
# import os
# from  distutils import filelist 

from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img


# os.chdir('C:/Users/Kirill/Documents/prj/deepscum')


# trainX = np.array(trainX)
# trainX = trainX.reshape(trainX.shape[0],55,66,1)
# trainX = trainX.astype(float)
# # trainX /= 255
# trainY = np.array(trainY)
# trainY = trainY[:,5:]
# ====================================================
ui_data_gen = ImageDataGenerator(
        # width_shift_range=0.2,
        # height_shift_range=0.2,
        rescale=1./255,
        # shear_range=0.2,
        # zoom_range=0.2,
        fill_mode='nearest')
ui_generator = ui_data_gen.flow_from_directory(
    'data/train-ui/train',
    target_size=(55,66),
    batch_size=32,
    class_mode='binary')
uiv_data_gen = ImageDataGenerator(
        rescale=1./255)
uiv_generator = uiv_data_gen.flow_from_directory(
    'data/train-ui/valid',
    target_size=(55,66),
    batch_size=32,
    class_mode='binary')
# ====================================================

cnn = models.Sequential()
cnn.add(conv.Convolution2D(64, (3, 3),  activation="relu", input_shape=(55, 66, 3), padding='same'))
cnn.add(conv.MaxPooling2D(strides=(2,2)))

cnn.add(conv.Convolution2D(64, (3, 3), activation="relu", padding='same'))
cnn.add(conv.MaxPooling2D(strides=(2,2)))

cnn.add(conv.Convolution2D(256, (3, 3), activation="relu", padding='same'))
cnn.add(conv.MaxPooling2D(strides=(2,2)))

cnn.add(core.Flatten())
# cnn.add(core.Dropout(0.2))
cnn.add(core.Dense(256, activation="relu")) # 4096
# cnn.add(core.Dense(1, activation="softmax"))
# cnn.add(core.Dropout(0.5))
cnn.add(core.Dense(6, activation="sigmoid"))
# cnn.add(core.Activation('sigmoid'))

cnn.summary()
cnn.compile(optimizer='sgd', loss='mean_squared_error', metrics=['accuracy'])
# cnn.compile(optimizer='rmsprop', loss='mean_squared_error', metrics=['accuracy'])
# cnn.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
# cnn.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])


# cnn.fit(trainX, trainY, batch_size=40, epochs=30, verbose=1)

rr = cnn.fit_generator(
    a,
    steps_per_epoch=20,
    epochs=1,
    validation_data=av,
    validation_steps=5,
    verbose=1
    )

cnn.save_weights('obj-detection-180314.h5')
cnn.load_weights('obj-detection-180314.h5')




rimage = np.array([misc.imread('data/train-ui/train/checkbox/'+i) for i in os.listdir('data/train-ui/train/checkbox')])


rimage = np.array([
misc.imread('data2/extract/checkbox/142-248.png', flatten=False),
misc.imread('data2/extract/checkbox/120-25.png', flatten=False),
misc.imread('data2/extract/fcheckbox/142-248.png', flatten=False),
misc.imread('data2/extract/radio/137-61.png', flatten=False),
misc.imread('data2/extract/radio/137-61-1.png', flatten=False),
misc.imread('data2/extract/fradio/137-61.png', flatten=False)
])*1./256

yPred = cnn.predict(rimage)

# ===================================

# datagen = ImageDataGenerator(
#         rotation_range=40,
#         width_shift_range=0.2,
#         height_shift_range=0.2,
#         rescale=1./255,
#         shear_range=0.2,
#         zoom_range=0.2,
#         horizontal_flip=True,
#         fill_mode='nearest')

# datagen = ImageDataGenerator(
#         rotation_range=40,
#         width_shift_range=0.2,
#         height_shift_range=0.2,
#         shear_range=0.2,
#         zoom_range=0.2,
#         horizontal_flip=True,
#         fill_mode='nearest')

# im_1 = img_to_array(load_img('data/randomradio3.png'))

########################################################
########################################################
########################################################
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
import keras.layers.convolutional as conv
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense

model = Sequential()
model.add(Conv2D(32, (3, 3), input_shape=(100, 100, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))


model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))
model.summary()

model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

batch_size = 16

# this is the augmentation configuration we will use for training
train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)
# this is a generator that will read pictures found in
# subfolers of 'data/train', and indefinitely generate
# batches of augmented image data
train_generator = train_datagen.flow_from_directory(
        'data/train',  # this is the target directory
        target_size=(150, 150),  # all images will be resized to 150x150
        batch_size=batch_size,
        class_mode='binary')  # since we use binary_crossentropy loss, we need binary labels

test_datagen = ImageDataGenerator(rescale=1./255)
validation_generator = test_datagen.flow_from_directory(
        'data/validation',
        target_size=(150, 150),
        batch_size=batch_size,
        class_mode='binary')


model.fit_generator(
        train_generator,
        steps_per_epoch=2000 // batch_size,
        epochs=10, verbose=2,
        validation_data=validation_generator,
        validation_steps=800 // batch_size)
cnn_rd.fit(a, [1,0]*16)

model.save_weights('catdog-e10.h5')
model.load_weights('catdog-e10.h5')

res = model.evaluate_generator( validation_generator, steps=800)



inp = np.array([
    0,0,0,0,0,0,1,1,1,1,1,
    0,0,0,0,0,0,1,1,1,1,1,
    0,0,0,0,0,0,1,1,1,1,1,
    0,0,0,0,0,0,1,1,1,1,1,
    0,0,0,0,0,0,1,1,1,1,1,
    0,0,0,0,0,0,1,1,1,1,1,
    0,0,0,0,0,0,1,1,1,1,1,
    0,0,0,0,0,0,1,1,1,1,1,
    0,0,0,0,0,0,1,1,1,1,1,
    0,0,0,0,0,0,1,1,1,1,1,
    0,0,0,0,0,0,1,1,1,1,1
    ]).reshape(11,11)

mo = Sequential()
model.add(Conv2D(32, (3, 3), input_shape=(11, 11)))




##############################################################
##############################################################
##############################################################
