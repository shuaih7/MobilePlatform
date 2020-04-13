#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.17.2020
Updated on 04.17.2020

Author: 212780558
'''

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget
from PyQt5.uic import loadUi


class AdminWidget(QTabWidget):
    def __init__(self):
        super(AdminWidget, self).__init__()
        loadUi("AdminWidget.ui", self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
