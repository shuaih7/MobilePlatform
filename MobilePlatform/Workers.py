#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.17.2020
Updated on 03.17.2020

Author: 212780558
'''

import time
import asyncio
import functools
import numpy as np
from bleak import BleakClient
from pypylon import pylon, genicam
import os, sys, json, time, cv2

from PyQt5.Qt import QMutex
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QTimer


'''
SOP: Open the default camera using opencv
'''
class videoWorker(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, camera, parent=None):
        super(videoWorker, self).__init__(parent)
        self.cam = camera
        self.isCap = True

    def run(self):
        while self.isCap:
            frame = self.cam.get_image()
            
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch*w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            self.changePixmap.emit(convertToQtFormat)
            time.sleep(0.05)  # Note: This is the temperory method


class pylonWorker(QThread):
    pylonConnectRequest = pyqtSignal(bool)

    def __init__(self, camera, label, parent=None):
        super(pylonWorker, self).__init__(parent)
        self.videoStart = False
        self._camera = camera
        self._label = label
        self.grab_strategy=pylon.GrabStrategy_LatestImageOnly
        
        # converting to opencv bgr format
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    @pyqtSlot(bool)
    def videoStatusReceiver(self, videoStart):
        self.videoStart = videoStart

    def run(self):
        self._camera.StopGrabbing()
        try:
            self._camera.StartGrabbing(self.grab_strategy)
        except genicam.RuntimeException:
            self.pylonConnectRequest.emit(False)
        
        try:
            while(self._camera.IsGrabbing() and self.videoStart):
                grab_result = self._camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

                if grab_result.GrabSucceeded():
                    # Access the image data
                    image = self.converter.Convert(grab_result)
                    img = image.GetArray()
                    
                    rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch*w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

                    self._label.pixmap = QPixmap.fromImage(convertToQtFormat)
                    self._label.update()

                grab_result.Release()
                
        except genicam.GenericException:
            self.pylonConnectRequest.emit(True)
        finally:
            self._camera.StopGrabbing()


class bleWorker(object):
    def __init__(self, address, cmd_uuid, sta_uuid):
        self.address = address
        self.cmd_uuid = cmd_uuid
        self.sta_uuid = sta_uuid
        self.loop = asyncio.get_event_loop()
        self.client = BleakClient(self.address, loop=self.loop)

    def connect(self):
        return self.loop.run_until_complete(self.connectAsync())

    def read(self):
        return self.loop.run_until_complete(self.readAsync())

    def write(self, cmd):
        return self.loop.run_until_complete(self.writeAsync())

    def disconnect(self):
        return self.loop.run_until_complete(self.disconnectAsync())

    async def connectAsync(self):
        try:
            isConnected = await self.client.connect()
            return isConnected
        except Exception as e:
            print(e) # This may be wirtten into a log file
            return False

    async def readAsync(self):
        try:
            response = await self.client.read_gatt_char(self.sta_uuid)
            return response
        except Exception as e:
            print(e) # This may be wirtten into a log file
            return None # No response

    async def writeAsync(self, cmd):
        try:
            response = await self.client.write_gatt_char(self.sta_uuid, cmd)
            return response
        except Exception as e:
            print(e) # This may be wirtten into a log file
            return None # No response
    async def disconnectAsync(self):
        try: await self.client.connect()
        except Exception as e: print(e)
        



    
