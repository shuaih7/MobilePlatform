#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.17.2020
Updated on 04.15.2020

Author: 212780558
'''

import os, sys
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QTabWidget, QFileDialog


class AdminWidget(QTabWidget):
    def __init__(self):
        super(AdminWidget, self).__init__()
        loadUi("AdminWidget.ui", self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
    def configCamera(self):
        print("This button has been triggered.")
        config_file = QFileDialog.getOpenFileName(self, "pylon feature stream", os.getcwd(), "fps files (*.fps)")
        print(config_file)
        print(type(config_file[0]))
