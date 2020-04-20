#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.17.2020
Updated on 04.13.2020

Author: 212780558
'''

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
try: from .AdminWidget import AdminWidget
except Exception as expt: from AdminWidget import AdminWidget


class PassDialog(QDialog):
    def __init__(self):
        super(PassDialog, self).__init__()
        loadUi("PassDialog.ui", self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.password = "123456"
        self.adminWidget = AdminWidget()
        self.passEdit.setEchoMode(2)

    def next(self):
        self.remind_label.clear()
        cur_pass = self.passEdit.text()
        if cur_pass == self.password:
            self.passEdit.clear()
            self.close()
            self.adminWidget.show()
        else:
            self.passEdit.clear()
            self.remind_label.setText("The password is incorrect, please try it again.")

    def cancel(self):
        self.close()
            
