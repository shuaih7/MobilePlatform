#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.17.2020
Updated on 03.17.2020

Author: 212780558
'''

import os, sys, cv2, json
from pypylon import pylon
from pypylon_opencv_viewer import BaslerOpenCVViewer


### Demo of the configuration matrix
VIEWER_CONFIG_RGB_MATRIX = {
    "serial_number": "22936597",
    "features": [
        {
            "name": "Height",
            "type": "int",
            "value": 1080,
            "unit": "px",
            "step": 2,
        },
        {
            "name": "Width",
            "type": "int",
            "value": 1920,
            "unit": "px",
            "step": 2,
        },
        {
            "name": "CenterX",
            "type": "bool",
        },
        {
            "name": "CenterY",
            "type": "bool",

        },
        {
            "name": "OffsetX",
            "type": "int",
            "dependency": {"CenterX": False},
            "unit": "px",
            "step": 2,
        },
        {
            "name": "OffsetY",
            "type": "int",
            "dependency": {"CenterY": False},
            "unit": "px",
            "step": 2,
        },
        {
            "name": "AcquisitionFrameRateEnable",
            "type": "bool",
        },
        {
            "name": "ExposureTime",
            "type": "int",
            "dependency": {"ExposureAuto": "Off"},
            "unit": "μs",
            "step": 100,
            "max": 35000,
            "min": 500,
        },
        {
            "name": "ExposureAuto",
            "type": "choice_text",
            "options": ["Off", "Once", "Continuous"],
            "style": {"button_width": "90px"}
        },
        {
            "name": "BalanceWhiteAuto",
            "type": "choice_text",
            "options": ["Off", "Once", "Continuous"],
            "style": {"button_width": "90px"}
        },
    ],
        
    "default_user_set": "UserSet1",
}


class Basler:

    def __init__(self):
        # Pypylon connect camera by serial number
        self.serial_number = "0000000" # Initialize the serial number
        self.info = None
        self.camera = None
        self.viewer = None
        self.configuration = None
        self.config_path = os.path.join(os.getcwd(), "config")
        if not os.path.exists(self.config_path): os.mkdir(self.config_path)
        self.load_configuration() # Load the configuration matrix to self.configuration
        self.update_device()

    def update_device(self):
        for dev in pylon.TlFactory.GetInstance().EnumerateDevices():
            if dev.GetSerialNumber() == self.serial_number:
                self.info = dev
                print("{} found!".format(self.serial_number))
                break
        else:
            print("Camera with {} serial number not found!".format(self.serial_number))

        if self.info is not None:
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(self.info))
            self.camera.Open()
            self.viewer = BaslerOpenCVViewer(self.camera)
            self.config_camera(self.configuration) # Load the camera configurations

    """
    # This is a sample configure function
    def config_resolution(self, resolution):
        width, height = resolution

        for item in self.VIEWER_CONFIG_RGB_MATRIX['features']:
            if item['name'] == 'Height':
                item['value'] = height
            elif item['name'] == 'Width':
                item['value'] = width
                
        self.viewer.set_configuration(self.VIEWER_CONFIG_RGB_MATRIX)
    """
    
    """
    Load the configurations from json file and config the basics
    """
    def load_configuration(self):
        config_file = os.path.join(self.config_path, "config.json")
        if not os.path.isfile(config_file): print("Could not find the config file.")
        else:
            with open (config_file, "r") as f: 
                self.configuration = json.load(f)
                try: self.serial_number = self.configuration["serial_number"]
                except KeyError: print("Could not find the key \"serial_number\".")
    
    """
    Configure the camera from the the domestic or imported configuration matrix
    ------
    :param configuration: imported configuration matrix
    """
    def config_camera(self, configuration=None):
        if configuration is None and self.configuration is None: return
        if configuration is None and self.configuration is not None: 
            configuration = self.configuration
        print("\nCamera configured.")
        self.viewer.set_configuration(configuration)

    def start_grabbing(self):
        pass        

    def get_image(self):
        if self.camera is not None: return  self.viewer.get_image()
        else: return 


if __name__ == '__main__':
    # Dump the json configuration matrix to json file
    config_path = os.path.join(os.getcwd(), "config")
    json_file = os.path.join(config_path, "config.json")
    with open (json_file, "w") as f:
       json.dump(VIEWER_CONFIG_RGB_MATRIX, f, indent=4)
       print("Done")
    

