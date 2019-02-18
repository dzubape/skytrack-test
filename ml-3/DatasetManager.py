#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, h5py
import numpy as np
from keras.preprocessing.image import array_to_img, img_to_array, load_img
from PIL import Image
import random
from matplotlib import pyplot as plt


def close_all_h5():
    '''Closes all h5py opend files'''
    import gc
    
    ## Browse through all objects
    for obj in gc.get_objects():
        try:
            ## Just h5py files
            if isinstance(obj, h5py.File):
                try:
                    obj.close()
                    print("{} has been closed".format(obj.filename))
                except:
                    ## Has been already closed
                    pass 
        except:
            pass


class DatasetManager:
    def __init__(self, storage_file_path):
        self.__storage_file_path = storage_file_path
        
        
    def __del__(self):
        self.stop_read_storage()
        
        
    def start_read_storage(self):
        if not hasattr(self, "hdh5"):
            self.__hdh5 = h5py.File(self.__storage_file_path, 'r')
            self.__cls_list = list(self.__hdh5.keys())
            self.__length = 0
            for cls_name in self.__hdh5.keys():
                self.__length += len(self.__hdh5[cls_name])
        
        
    def stop_read_storage(self):
        if hasattr(self, "hdh5") and isinstance(self.__hdh5, h5py.File):
            self.__hdh5.close()
            del self.__hdh5
        
    def build(self, ds_dir, input_shape, cls_list=None, rewrite=True):
        
        if cls_list is None:
            cls_dir_list = os.listdir(ds_dir)
            cls_list = dict(zip(cls_dir_list, cls_dir_list))
            
        self.__cls_list = list(cls_list.values())
            
        self.stop_read_storage()
        
        if not rewrite and os.path.exists(self.__storage_file_path):
            print("Nothing has been built. Storage file {} already exists.".format(self.__storage_file_path))
            return 1
        
        try:
            hdh5 = h5py.File(self.__storage_file_path, "w")
        except:
            print("Can't open storage file: {}".format(self.__storage_file_path))
            return 1
        
        for dir_name, cls_name in cls_list.items():
            print(dir_name, cls_name)
            cls_dir = os.path.join(ds_dir, dir_name)
            img_list = os.listdir(cls_dir)
            
            cls_ds = hdh5.create_dataset(cls_name, (len(img_list), *input_shape), dtype=np.uint8)
            
            for i, img_name in enumerate(img_list):
                
                #src_img = mpl.image.imread(os.path.join(cls_dir, img_name))
                src_img = load_img(os.path.join(cls_dir, img_name))
                std_img = src_img.resize((224, 224), Image.BICUBIC)
                img_array = img_to_array(std_img)
                cls_ds[i] = img_array
               
        hdh5.flush()
        hdh5.close()                
            
        return 0
    
    
    def get_img(self, img_idx, cls_name=None):
        if cls_name is None:
            assert 0 <= img_idx < self.__length

            shift = 0
            for cls_name in self.__hdh5.keys():
                ds = self.__hdh5[cls_name]
                if shift + ds.len() >= img_idx:
                    return ds[img_idx - shift]
                shift += ds.len()
        else:
            assert cls_name in self.__hdh5            
            ds = self.__hdh5[cls_name]
            
            assert 0 <= img_idx < ds.len()
            return ds[img_idx]
    
        
    def test(self):        
        self.start_read_storage()
        self.__cls_list = list(self.__hdh5.keys())
        print("class list:", self.__cls_list)
        
        plt.figure(figsize=(12, 3), dpi=96)
        
        test_count = 4
        test_discounter = test_count
        
        for i, cls_name in enumerate(self.__cls_list):
            ds = self.__hdh5[cls_name]
            random_idx = random.randint(0, len(ds))
            img = ds[random_idx]
            print("image data type:", img.dtype)
            plt.subplot(1, test_count, i + 1).imshow(img)
            test_discounter -= 1
            
        for i in range(0, 1):
            random_idx = random.randint(0, self.__length)
            img = self.get_img(random_idx)
            print("image data type:", img.dtype)
            plt.subplot(1, test_count, test_count - test_discounter + 1).imshow(img)
            test_discounter -= 1
            
        cls_idx = random.randint(0, len(self.__cls_list) - 1)
        cls_name = self.__cls_list[cls_idx]
        ds = self.__hdh5[cls_name]
        img_idx = random.randint(0, ds.len())
        img = self.get_img(img_idx, cls_name)
        plt.subplot(1, test_count, test_count - test_discounter + 1).imshow(img)
        test_discounter -= 1
        
            
        