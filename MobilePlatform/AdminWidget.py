#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 03.17.2020
Updated on 04.19.2020

Author: 212780558
"""

import os, sys
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTabWidget, QFileDialog

class AdminWidget(QTabWidget):
    camConfigRequest = pyqtSignal(str)
    opListUpdateRequest = pyqtSignal(bool)
    bleSettingRequest = pyqtSignal(bool)
    
    def __init__(self):
        super(AdminWidget, self).__init__()
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "AdminWidget.ui"), self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.config_matrix = None
        self.line_ondelay.setValidator(QIntValidator(0,9999))
        self.line_offdelay.setValidator(QIntValidator(0,9999))
        
    def initConfigurations(self, config_matrix):
        self.config_matrix = config_matrix
        op_names = config_matrix["Names"]
        op_levels = config_matrix["Levels"]
        
        for name, level in zip(op_names, op_levels):
            self.op_list.addItem(name)
            self.level_list.addItem(level)

            item = self.level_list.item(self.level_list.count()-1)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable) # Set the level list not selectable

            item = self.op_list.item(self.op_list.count()-1)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        
        ble_brightness = config_matrix["BleBrightness"]
        ble_ondelay = config_matrix["BleOnDelay"]
        ble_offdelay = config_matrix["BleOffDelay"]
        self.bright_slider.setValue(ble_brightness)
        self.line_ondelay.setText(str(ble_ondelay))
        self.line_offdelay.setText(str(ble_offdelay))

    def addUser(self):
        self.op_list.addItem("User Name")
        item = self.op_list.item(self.op_list.count()-1)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.op_list.editItem(item)
        self.level_list.addItem("User")
    
    def delUser(self):
        cur_index = self.op_list.currentRow()
        if self.level_list.item(cur_index).text() == "Administrator": return
        self.op_list.takeItem(cur_index)
        self.level_list.takeItem(cur_index)
        self.op_list.setCurrentRow(cur_index)
        cur_item = self.op_list.currentItem()
        if cur_item is None: self.op_list.setCurrentRow(self.op_list.count()-1)
        
    def configCamera(self):
        config_file = QFileDialog.getOpenFileName(self, "pylon feature stream", os.getcwd(), "fps files (*.fps)")
        if config_file is not None: self.camConfigRequest.emit(config_file[0])
        
    def configBleBrightness(self):
        bleBrightnessValue = self.bright_slider.value()
        self.bleSettingRequest.emit(bleBrightnessValue)
        
    def configBleOnDelay(self):
        bleOnDelayValue = int(self.line_ondelay.text())
        if bleOnDelayValue > 255*20: 
            bleOnDelayValue = 255*20
            self.line_ondelay.setText(str(255*20))
        
    def configBleOffDelay(self):
        bleOffDelayValue = int(self.line_offdelay.text())
        if bleOffDelayValue > 255*20: 
            bleOffDelayValue = 255*20
            self.line_offdelay.setText(str(255*20))
        
    def closeEvent(self, ev):
        self.opListUpdateRequest.emit(True)
        self.bleSettingRequest.emit(True)

        
