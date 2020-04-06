#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.17.2020
Updated on 03.17.2020

Author: 212780558
'''

import sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    import HMI
    MainWindow = HMI.MainWindow()
    MainWindow.showMaximized()
    sys.exit(app.exec_())
