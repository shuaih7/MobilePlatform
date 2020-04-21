#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.04.2020
Updated on 04.21.2020

Author: 212780558
'''

import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtWidgets import QLabel


class StatusLabel(QLabel):
    def __init__(self, parent=None):
        super(StatusLabel, self).__init__(parent)
        self.camIsConnected = False
        self.bleIsConnected = False
        self.diameter = int(0.8 * min(self.width(), self.height()))
        self.status_color = Qt.red
        
    def updateConnectStatus(self, cam_status=None, ble_status=None):
        if cam_status is not None: self.camIsConnected = cam_status
        if ble_status is not None: self.bleIsConnected = ble_status
        if self.camIsConnected and self.bleIsConnected: self.status_color = Qt.green
        else: self.status_color = Qt.red
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.status_color, Qt.SolidPattern))
        painter.drawEllipse(self.width()*0.5, self.height()*0.35, self.diameter, self.diameter)
                     
            

