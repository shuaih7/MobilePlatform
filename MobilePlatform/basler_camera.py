#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.17.2020
Updated on 03.17.2020

Author: 212780558
'''

import os, sys, cv2
from pypylon import pylon
from pypylon_opencv_viewer import BaslerOpenCVViewer

class Basler:
    VIEWER_CONFIG_RGB_MATRIX = {
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
        
        "default_user_set": "UserSet3",
    }

    def __init__(self):
        # Pypylon connect camera by serial number
        self.serial_number = '22936597' # This needs to be modified
        self.info = None
        self.camera = None
        self.viewer = None
        self.config = self.VIEWER_CONFIG_RGB_MATRIX
        

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
            #self.viewer.set_configuration(self.VIEWER_CONFIG_RGB_MATRIX)

    def config_resolution(self, resolution):
        width, height = resolution

        for item in self.VIEWER_CONFIG_RGB_MATRIX['features']:
            if item['name'] == 'Height':
                item['value'] = height
            elif item['name'] == 'Width':
                item['value'] = width
                
        self.viewer.set_configuration(self.VIEWER_CONFIG_RGB_MATRIX)

    def start_grabbing(self):
        pass        


    def get_image(self):
        if self.camera is not None: return  self.viewer.get_image()
        else: return 


if __name__ == '__main__':
    cam = Basler() # Test whether the device can be detected
    cam.start_grabbing()


