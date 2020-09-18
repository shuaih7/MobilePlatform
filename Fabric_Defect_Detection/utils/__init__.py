import os, sys, cv2, shutil, random
import glob as gb
import numpy as np


def sort_dataset(image_path, label_path, save_path, image_suf=".PNG", label_suf=".PNG", op="copy"):
    # Sort the label files corresponding to the input image
    images = gb.glob(image_path + r"/*"+image_suf)
    #labels = gb.glob(label_path + r"/*"+label_suf)
    
    if not os.path.exists(save_path): os.mkdir(save_path)
    
    for img in images:
        _, fullname = os.path.split(img)
        filename, _ = os.path.splitext(fullname)
        
        label = os.path.join(label_path, filename+"_json_mask"+label_suf)
        if os.path.isfile(label): 
            if op=="copy":   shutil.copy(label, os.path.join(save_path, filename+label_suf))
            elif op=="move": shutil.move(label, os.path.join(save_path, filename+label_suf))
            else: print("Operation "+op+" not valid!")
        else: print("File "+label+" not found!")
        
    print("Done")
        

def split_train_val(image_path, label_path, 
                    image_train_path, label_train_path, image_valid_path, label_valid_path,
                    image_suf=".png", label_suf=".png", percent=0.8, op="copy"):
                    
    # Split the whole dataset into training & validation sets
    
    image_list = gb.glob(image_path + r"/*"+image_suf)
    label_list = gb.glob(label_path + r"/*"+label_suf)
    
    percent = max(0.5, min(1.0, percent)) # percent is in the range of (0.5, 1)
    num = min(len(image_list), len(label_list))
    cutoff = int(percent*float(num))
    random.shuffle(image_list)
    
    for n, img in enumerate(image_list):
        _, fullname = os.path.split(img)
        filename, _ = os.path.splitext(fullname)
    
        label = os.path.join(label_path, filename+label_suf)
        if os.path.isfile(label): 
            if op=="copy":   
                if n <= cutoff:
                    shutil.copy(img, os.path.join(image_train_path, fullname))
                    shutil.copy(label, os.path.join(label_train_path, filename+label_suf))
                else: 
                    shutil.copy(img, os.path.join(image_valid_path, fullname))
                    shutil.copy(label, os.path.join(label_valid_path, filename+label_suf))
            elif op=="move": 
                if n <= cutoff:
                    shutil.move(img, os.path.join(image_train_path, fullname))
                    shutil.move(label, os.path.join(label_train_path, filename+label_suf))
                else: 
                    shutil.move(img, os.path.join(image_valid_path, fullname))
                    shutil.move(label, os.path.join(label_valid_path, filename+label_suf))
            else: print("Operation "+op+" not valid!")
        else: print("File "+label+" not found!")
    
    print("Done")
            