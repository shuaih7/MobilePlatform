#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.04.2020
Updated on 04.13.2020

Author: 212780558
'''

import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtWidgets import QLabel


class StatusLabel(QLabel):
    def __init__(self, parent=None):
        super(StatusLabel, self).__init__(parent)
        self.camConnected = False
        self.bleConnected = False
        

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.camConnected and self.bleConnected: painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
        else: painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        width, height = self.width(), self.height()
        diameter = int(0.5 * min(width, height))
        painter.drawEllipse(width*0.5, height*0.45, diameter, diameter)
            

                        
            
            
            

