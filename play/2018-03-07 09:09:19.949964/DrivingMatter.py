import pandas as pd
import numpy as np
np.random.seed(2)
from scipy import misc
import sys
import os
import cv2
from sklearn.metrics import confusion_matrix

import keras
from keras.models import Sequential
from keras.optimizers import RMSprop
from keras.layers import Dense, Dropout, Flatten, Activation
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
K.set_image_dim_ordering('th')

from keras.utils import to_categorical

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.neural_network import MLPClassifier

import matplotlib
import matplotlib.pyplot as plt

from skimage import exposure
import numpy as np

df = pd.read_csv("dataset.csv", usecols=[1, 2])
df = np.array(df)

import random
resized_img = 10

def read_img(url):
    image   = cv2.imread(url ,0)
    return image

X = []
y = []

for data in df:
    target = data[1]
    images = read_img(data[0])

    X.append(images)
    y.append(target)

while True:
    for i in range(len(X)):
        image = misc.imresize(X[i], resized_img)
        target = y[i]

        cv2.imshow("Image", image)
        cv2.waitKey(1)  # CV2 Devil - Don't dare to remove

        print type(X[i])
        print X[i].shape
        print image.shape
        print target
