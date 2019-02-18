#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import keras
from keras import Model
from keras.models import Sequential
from keras.layers import Conv2D, Dense, MaxPooling2D, Flatten, Dropout, Input, Lambda
from keras import backend as K
from keras.callbacks import TensorBoard
import os
    

class TimeMark:
    def __init__(self):
        self._mark = None
    
    def update(self):
        from time import strftime, localtime
        self._mark = strftime("%Y-%m-%d_%H-%M-%S", localtime())
        return self._mark
    
    def get(self):
        return self._mark        
    
    def __call__(self):
        return self._mark

    
try:
    last_train_start
except:
    last_train_start = TimeMark()  
    

def get_model_paths(mark):
    model_dir = "model"
    
    struct_filename = "model_{}.json".format(mark)
    struct_filepath = os.path.join(model_dir, struct_filename)
    
    weights_filename = "model_{}.hdh5".format(mark)
    weights_filepath = os.path.join(model_dir, weights_filename)
    
    return struct_filepath, weights_filepath

    
def save_model(model, mark=None):
    
    if mark is None:
        from time import strftime, gmtime, localtime
        slice_time = strftime("%Y-%m-%d_%H-%M-%S", localtime())
        mark = slice_time
        
    struct_filepath, weights_filepath = get_model_paths(mark)

    ## serialize model to json
    with open(struct_filepath, "w") as json_file:
        model_json = model.to_json()
        json_file.write(model_json)
        print("Model struct has been stored on {}".format(struct_filepath))

    ## serialize weights to HDF5
    model.save_weights(weights_filepath)
    print("Model weights has been stored on {}".format(weights_filepath))
    
    
def load_model(mark):
    from keras.models import model_from_json
    
    struct_filepath, weights_filepath = get_model_paths(mark)
    
    ## Loads model struct
    json_file = open(struct_filepath, 'r')
    model_json = json_file.read()
    json_file.close()
    
    loaded_model = model_from_json(model_json)
    
    ## Loads weights into the model
    loaded_model.load_weights(weights_filepath)
    
    return loaded_model