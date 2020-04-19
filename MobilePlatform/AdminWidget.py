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
    opListUpdateRequest = pyqtSignal(list)
    bleSettingRequest = pyqtSignal(int)
    
    def __init__(self):
        super(AdminWidget, self).__init__()
        loadUi("AdminWidget.ui", self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.config_matrix = None
        self.line_ondelay.setValidator(QIntValidator(0,999))
        self.line_offdelay.setValidator(QIntValidator(0,999))
        
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
                
    def updateOperatorList(self):
        operator_info = [[],[]]
        for i in range(self.op_list.count()-1):
            operator_info[0].append(self.op_list.item(i).text())
            operator_info[1].append(self.level_list.item(i).text())
        self.opListUpdateRequest.emit(operator_info)
                   
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
        pass
        
    def configBleOnDelay(self):
        bleOnDelayValue = int(self.line_ondelay.text())
        bleOnDelayValue = min(bleOnDelayValue, 100)
        index = 1000 + bleOnDelayValue
        self.bleSettingRequest.emit(index)
        
    def configBleOffDelay(self):
        bleOffDelayValue = int(self.line_offdelay.text())
        bleOffDelayValue = min(bleOffDelayValue, 100)
        index = 2000 + bleOffDelayValue
        self.bleSettingRequest.emit(index)

        
