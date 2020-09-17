#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 03.17.2020
Updated on 04.15.2020

Author: 212780558
"""

import os, sys, cv2
from pypylon import pylon
from pypylon_opencv_viewer import BaslerOpenCVViewer

"""
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
"""

class Basler:

    def __init__(self):
        self.serial_number = None # Initialize the serial number
        self.info = None
        self.camera = None
        self.viewer = None
        self.configuration = None
        self.config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config")
        if not os.path.exists(self.config_path): os.mkdir(self.config_path)
        self.update_device()

    """
    Update the basler pylon device, self.camrea == None if no device was found
    """
    def update_device(self):
        devices = pylon.TlFactory.GetInstance().EnumerateDevices()
        if len(devices) > 0:
            dev = devices[0]
            self.info = dev # Assume only one camera is connected, if more than 1, only select the first one
            print("{} found!".format(dev.GetSerialNumber()))
        else:
            print("No camera was found, please check the USB connection.")

        if self.info is not None:
            try: self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(self.info))
            except Exception as expt:
                print(expt)
                self.camera = None
                self.info = None
                return
            self.camera.Open()
            self.load_configuration() # Load the default pylon configuration
            self.viewer = BaslerOpenCVViewer(self.camera)

    """
    Load the ".pfs" configuration file to config the camera
    ------
    :param cfg_file: File name of the ".fps" pylon configuration file.
    """
    def load_configuration(self, cfg_file=None):
        if cfg_file is None:
            cfg_path = self.config_path
            cfg_file = os.path.join(cfg_path, "pylon_config.fps")
        if not os.path.isfile:
            print("Could not find the pylon configuration file", cfg_file)
            return
        try: pylon.FeaturePersistence.Load(cfg_file, self.camera.GetNodeMap())
        except Exception as expt: print(expt)
        
    def start_grabbing(self):
        pass        

    def get_image(self):
        if self.camera is not None: return  self.viewer.get_image()
        else: return 


if __name__ == '__main__':
    basler = Basler()
    import time
    if basler.camera.IsPylonDeviceAttached(): print("Attached.")
    while True:
        if basler.camera.IsCameraDeviceRemoved(): 
            print("Detected removal")
            break
        else: time.sleep(0.5)
    

