#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 01.04.2020
Updated on 03.20.2020

Author: 212780558
'''

import os
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QRect, QLineF
from PyQt5.QtGui import QPixmap, QPainter, QPen

class MarkLabel(QLabel):
    def __init__(self, parent=None):
        super(MarkLabel, self).__init__(parent)
        self.scale = 1.0
        self.scale_min = 0.3        # Minimum value of the scale factor
        self.scale_max = 3.0        # Maximum value of the scale factor
        self.pixmap = None
        self.scaled_pixmap = None
        self.offx = 0
        self.offy = 0

        self.resizeNeeded = True    # Need to resize the widget in order to fit the pixmap
        self.mode = 'text'
        self.comments = ' '
        self.points = []            # Stores all of the marked points
        self.mark_index = []        # Index of the points for each marking
        self.cur_mark_index = 0     # Current point index
        self.isLoadMode = False     # Manage the markings
        self.winGeo = QRect(0, 0, 1200, 900)  # Scroll area size of [width, height]
        self.setScaledContents(True)

    def setScaleFactor(self, units):
        factor = self.scale * units
        if factor > self.scale_max: factor = self.scale_max
        elif factor < self.scale_min: factor = self.scale_min
        self.scale = factor

    def undo(self):
        if len(self.mark_index) > 1:
            last = self.mark_index[-2]
            self.points = self.points[:last+1]
            del self.mark_index[-1]
            self.update()
        elif len(self.mark_index) == 1:
            self.points = []
            self.mark_index = []
            self.update()
        else: return

    def mousePressEvent(self, event):
        if self.mode == 'text': return
        if len(self.mark_index):
            self.cur_mark_index = self.mark_index[-1] + 1
        self.points.append([event.x()/self.scale, event.y()/self.scale])

    def mouseReleaseEvent(self, event):
        if self.mode == 'text': return
        self.mark_index.append(self.cur_mark_index)
        self.cur_mark_index = 0

    def mouseMoveEvent(self, event):
        if self.mode == 'text': return
        self.cur_mark_index += 1
        self.points.append([event.x()/self.scale, event.y()/self.scale])
        self.update()

    def wheelEvent(self, event):
        # This event has been implemented in the MainWindow
        pass

    # Transform the image top-left locatiuon
    # Basic assumption: each image comming from the camera have the same size
    def transformation(self):
        if not self.resizeNeeded: return
        self.scale = self.scaled_pixmap.width() / self.pixmap.width()
        w, h = self.scaled_pixmap.width(), self.scaled_pixmap.height()
        aw, ah = self.winGeo.width(), self.winGeo.height()
        self.offx = (aw - w) / 2 if aw > w else 0
        self.offy = (ah - h) / 2 if ah > h else 0

        self.resize(self.scaled_pixmap.size())
        self.move(self.offx, self.offy)
        self.resizeNeeded = False

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.pixmap is not None:
            # TODO: make the received images auto fit the window
            
            self.scaled_pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.transformation()  # Update the image showing offset
            painter.drawPixmap(0, 0, self.scaled_pixmap)

            if self.mode == 'draw':
                painter.setPen(QPen(Qt.green, 5, Qt.SolidLine))
                scale = self.scale
                for i in range(len(self.points) - 1):
                    if (i not in self.mark_index) or len(self.mark_index)==0:
                        line = QLineF(self.points[i][0]*scale, self.points[i][1]*scale, self.points[i+1][0]*scale, self.points[i+1][1]*scale)
                        painter.drawLine(line)
            

                        
            
            
            

