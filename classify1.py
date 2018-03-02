# import pandas as pd
import numpy as np
import keras.layers.core as core
import keras.layers.convolutional as conv
from keras.layers import Conv2D, MaxPooling2D
import keras.models as models
import keras.utils.np_utils as kutils

from scipy import misc
import os
from  distutils import filelist 

from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img


# from sklearn import utils #.shuffle

os.chdir('C:/Users/Kirill/Documents/prj/deepscum')

# trainX = []
# trainY = []

# for i in os.listdir('data/radio'):
#     fn = i
#     bo = fn.split('.')[0].split('-')[1:5]

#     image = misc.imread('data/radio/'+i, flatten=True)

#     trainX = trainX + [image]
#     trainY = trainY + [[1, bo[0], bo[1], bo[2], bo[3], 1, 0, 0]]

# for i in os.listdir('data/checkbox'):
#     fn = i
#     bo = fn.split('.')[0].split('-')[1:5]

#     image = misc.imread('data/checkbox/'+i, flatten=True)

#     trainX = trainX + [image]
#     trainY = trainY + [[1, bo[0], bo[1], bo[2], bo[3], 0, 1, 0]]


# for i in os.listdir('data/fradio'):
#     fn = i
#     bo = fn.split('.')[0].split('-')[1:5]

#     image = misc.imread('data/fradio/'+i, flatten=True)

#     trainX = trainX + [image]
#     trainY = trainY + [[0, bo[0], bo[1], bo[2], bo[3], 0, 0, 1]]

# for i in os.listdir('data/fcheckbox'):
#     fn = i
#     bo = fn.split('.')[0].split('-')[1:5]

#     image = misc.imread('data/fcheckbox/'+i, flatten=True)

#     trainX = trainX + [image]
#     trainY = trainY + [[0, bo[0], bo[1], bo[2], bo[3], 0, 0, 1]]



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
nb_filters_1 = 32 # 64
nb_filters_2 = 64 # 128
nb_filters_3 = 128 # 256
nb_filters_4 = 256
nb_conv = 3

cnn = models.Sequential()
cnn.add(conv.Convolution2D(32, (3, 3),  activation="relu", input_shape=(55, 66, 3), padding='same'))
cnn.add(conv.MaxPooling2D(strides=(2,2)))

cnn.add(conv.Convolution2D(32, (3, 3), activation="relu", padding='same'))
cnn.add(conv.MaxPooling2D(strides=(2,2)))

cnn.add(conv.Convolution2D(64, (3, 3), activation="relu", padding='same'))
cnn.add(conv.MaxPooling2D(strides=(2,2)))

cnn.add(core.Flatten())
# cnn.add(core.Dropout(0.2))
cnn.add(core.Dense(128, activation="relu")) # 4096
# cnn.add(core.Dense(1, activation="softmax"))
cnn.add(core.Dropout(0.5))
cnn.add(core.Dense(1, activation="sigmoid"))
# cnn.add(core.Activation('sigmoid'))

cnn.summary()
cnn.compile(optimizer='sgd', loss='binary_crossentropy', metrics=['accuracy'])
# cnn.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
# cnn.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])


# cnn.fit(trainX, trainY, batch_size=40, epochs=30, verbose=1)

rr = cnn.fit_generator(
    ui_generator,
    steps_per_epoch=20,
    epochs=10,
    validation_data=uiv_generator,
    validation_steps=50,
    verbose=2
    )

cnn.save_weights('ui-e40.h5')
cnn.load_weights('ui-e40.h5')

next = uiv_generator.next()
for a, b in uiv_generator.next:
a,b  = next
print([i for i in zip(b, cnn.predict(a))])
    break



i = 0
for batch in ui_data_gen.flow_from_directory(
    'data/train-ui/train',
    target_size=(55,66),
    batch_size=32,
    class_mode='binary',
    save_to_dir='previewXXX'):
    print(len(batch))
    i += 1
    if i > 2:
        break



rimage = np.array([misc.imread('data/train-ui/train/checkbox/'+i) for i in os.listdir('data/train-ui/train/checkbox')])


cnn.evaluate(trainX, trainY)


testX = test.reshape(test.shape[0], 28, 28, 1)
testX = testX.astype(float)
testX /= 255.0

yPred = cnn.predict_classes([trainX[1:3]])
yPred = cnn.predict([trainX[-3:]])


cnn.save_weights('180227-100e.h5')
cnn.load_weights('180227-100e.h5')


rimage = np.array([misc.imread('data/randomradio.png', flatten=False)])
rimage = np.array([
misc.imread('data/randomradio.png', flatten=False),
misc.imread('data/randomradio1.png', flatten=False),
misc.imread('data/randomradio3.png', flatten=False)])


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


from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense

model = Sequential()
model.add(Conv2D(32, (3, 3), input_shape=(150, 150, 3)))
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