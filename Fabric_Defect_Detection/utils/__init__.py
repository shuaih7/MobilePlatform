import os, sys, cv2, shutil
import glob as gb
import numpy as np

def sort_dataset(image_path, label_path, save_path, image_suf=".png", label_suf=".png"， op="copy"):
    # Sort the label files corresponding to the input image
    images = gb.glob(image_path + r"/*"+image_suf)
    #labels = gb.glob(label_path + r"/*"+label_suf)
    
    if not os.path.exists(save_path): os.mkdir(save_path)
    
    for img in images:
        _, fullname = os.path.split(img)
        filename, _ = os.path.splitext(fullname)
        
        label = label_path + filename + label_suf
        if os.path.isfile(label): 
            if op=="copy":   shutil.copy(label, save_path+filename+label_suf)
            elif op=="move": shutil.move(label, save_path+filename+label_suf)
        else: print("File "+label+" not found!")
            