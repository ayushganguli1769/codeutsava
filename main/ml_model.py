####### Importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import os 
import math
#import seaborn as sns
import pickle
#from sklearn.preprocessing import StandardScaler
#from sklearn.svm import SVC
#from sklearn.utils import shuffle
#import tensorflow_addons as tfa
#import gc
#loading model here
###### Defining Architecture

#with tpu_strategy.scope():



#### Defining Hyperparameters
num_layers = 2
d_model = 128
num_heads = 8
dff = 256
max_seq_len = 2560 #X_train.shape[1]
pe_input = 2560
rate = 0.3
num_features = 1

###### Defining Layers
Input_layer = tf.keras.layers.Input(shape=(max_seq_len,num_features))

##### Convolutional Filters

### Layer-1
conv1 = tf.keras.layers.Conv1D(32,15,padding='same',activation='relu')
conv11 = tf.keras.layers.Conv1D(32,15,padding='same',activation='relu')
conv12 = tf.keras.layers.Conv1D(32,15,padding='same',activation='relu')
conv13 = tf.keras.layers.Conv1D(32,15,padding='same',activation='relu')

### Layer-2
conv2 = tf.keras.layers.Conv1D(64,15,padding='same',activation='relu')
conv21 = tf.keras.layers.Conv1D(64,15,padding='same',activation='relu')
conv22 = tf.keras.layers.Conv1D(64,15,padding='same',activation='relu')
conv23 = tf.keras.layers.Conv1D(64,15,padding='same',activation='relu')

### Layer-3
conv3 = tf.keras.layers.Conv1D(128,15,padding='same',activation='relu')
conv31 = tf.keras.layers.Conv1D(128,15,padding='same',activation='relu')
conv32 = tf.keras.layers.Conv1D(128,15,padding='same',activation='relu')
conv33 = tf.keras.layers.Conv1D(128,15,padding='same',activation='relu')

#### Channel Attention Module
#cam_module = CAM_Module(128,1)

##### Transfromer Layer
#transformer = Transformer(num_layers,d_model,num_heads,dff,pe_input,rate)

##### Output Layer
gap_layer = tf.keras.layers.GlobalAveragePooling1D()

###### Defining Architecture
##### Input Layer
Inputs = Input_layer

##### Network
#### Layer-1
conv1_up = conv1(Inputs)
conv_11 = conv11(conv1_up) 
conv_12 = conv12(conv_11)
conv_13 = conv13(conv_12)
conv_13 = tf.keras.layers.Add()([conv_13,conv_11])

#### Layer-2
conv2_up = conv2(conv_13)
conv_21 = conv21(conv2_up)
conv_22 = conv22(conv_21)
conv_23 = conv23(conv_22)
conv_23 = tf.keras.layers.Add()([conv_23,conv_21])

#### Layer-3
conv3_up = conv3(conv_23)
conv_31 = conv31(conv3_up)
conv_32 = conv32(conv_31)
conv_33 = conv33(conv_32)
conv_33 = tf.keras.layers.Add()([conv_33,conv_31])

##### Transformer
#embeddings =  transformer(inp=conv_33,enc_padding_mask=None)

##### CAM Module
#cam_op = cam_module(conv_33)
#cam_op = tf.keras.layers.Add()([cam_op,embeddings])

##### Output Layers
#### Initial Layers
gap_op = gap_layer(conv_33)
dense1 = tf.keras.layers.Dense(256,activation='relu')(gap_op)
dropout1 = tf.keras.layers.Dropout(0.3)(dense1)
dense2 = tf.keras.layers.Dense(256,activation='relu')(dropout1)
dense3 = tf.keras.layers.Dense(3,activation='softmax')(dense2)

##### Compiling Architecture            
model = tf.keras.models.Model(inputs=Inputs,outputs=dense3)
model.load_weights('MHM_Stress_WESAD.h5')#check if works
model.compile(optimizer=tf.keras.optimizers.Adam(lr=1e-4),loss='sparse_categorical_crossentropy',metrics=['accuracy']) 

#### Main Driver Code
#x is an array of 2560 float, ecg reading
#x = # Dimensions: (2560,1) Numpy Array
def main_model_stress_function(x):#x is input ecg signal arr of lenght 2560
    #x = np.arange(2560) 
    x = x/np.max(x)

    x = np.reshape(x,(1,2560,1))

    y_preds = model.predict(x)
    y_rohan = np.argmax(y_preds,axis=1)
    y_rohan#return to rohan final
    #print(y_rohan)
    #model.predict(x)
    print(y_rohan[0])
    return y_rohan[0]