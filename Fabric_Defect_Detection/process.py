import os, sys
from utils import *

if __name__ == "__main__":
    """
    image_path = r"E:\Projects\Fabric_Defect_Detection\model_proto\image\over"
    label_path = r"E:\Projects\Fabric_Defect_Detection\model_proto\mask"
    save_path  = r"E:\Projects\Fabric_Defect_Detection\model_proto\mask\over"
    
    sort_dataset(image_path, label_path, save_path, op="move")
    """
    
    image_path = r"E:\Projects\Fabric_Defect_Detection\model_proto\original_data\image\normal"
    label_path = r"E:\Projects\Fabric_Defect_Detection\model_proto\original_data\mask\normal"
    image_train_path = r"E:\Projects\Fabric_Defect_Detection\model_proto\dataset\x_train"
    label_train_path = r"E:\Projects\Fabric_Defect_Detection\model_proto\dataset\y_train"
    image_valid_path = r"E:\Projects\Fabric_Defect_Detection\model_proto\dataset\x_valid"
    label_valid_path = r"E:\Projects\Fabric_Defect_Detection\model_proto\dataset\y_valid"
    
    split_train_val(image_path, label_path, image_train_path, label_train_path, image_valid_path, label_valid_path, percent=0.815, op="copy")
    