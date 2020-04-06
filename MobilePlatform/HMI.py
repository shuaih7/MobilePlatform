#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 03.17.2020
Updated on 03.30.2020

Author: 212780558
'''

import os, sys, time, glob
from pypylon import genicam
from basler_camera import Basler
from Workers import pylonWorker, bleWorker

from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QEvent, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox


ADDRESS = "98:F4:AB:16:85:A6"
CMD_UUID = "73c1298a-0452-4637-89df-816e211a71db"
STA_UUID = "352c2cb8-e15e-49ff-b0fe-3a1ed971dc1e"


class MainWindow(QMainWindow):
    videoStart = pyqtSignal(bool) # Signal to communicate with the video thread
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi("HMI.ui", self)

        ######--- Basic Parameters ---######
        self.basler = None        
        self.islive = False
        self.able_to_store = False
        self.videoThread = None
        self.pylonIsConnected = False
        self.cameraCheck(True)
        self.setTextMode()
        
        self.image_name = None
        self.image_save_parent = os.path.join(os.getcwd(), "data")
        self.image_save_path = self.image_save_parent
        self.cur_operation = None
        self.imageFolderCheck()

        self.img_index = 0
        self.operator = None
        self.operator_name = None
        self.get_operator_name()  # Get the current operator's name

        self.label.setAttribute(Qt.WA_AcceptTouchEvents) # Enable the Touch event of the MarkLabel
        self.scrollArea.setVisible(True)

        self.label.winSize = [self.scrollArea.width(), self.scrollArea.height()]
        self.label.installEventFilter(self)
        self.label.grabGesture(Qt.PinchGesture)

        self.ble = bleWorker(ADDRESS, CMD_UUID, STA_UUID)
        self.bleIsConnected = False
        self.bleCheck()
        

    @pyqtSlot(bool)
    def cameraCheck(self, signal=True):
        if self.pylonIsConnected:
            try: basler = Basler() # Update the current status every time the slot function is called
            except genicam.RuntimeException: return # In case the command is mistakenly clicked twice
            
            if basler.camera is not None: return # Assuming that if the camera exists, it is correctly connected
            else: self.basler = basler
        else: self.basler = Basler()
        self.islive = False
        
        if self.basler.camera is not None: # The basler camera is found
            self.videoThread = pylonWorker(self.basler.camera, self.label)
            self.videoStart.connect(self.videoThread.videoStatusReceiver)
            self.videoThread.pylonConnectRequest.connect(self.cameraCheck)
            self.setBtnEnabled(True)
            self.pylonIsConnected = True
        else:
            reply = QMessageBox.information(
            self,
            "Failed to connect the camera",
            "Do you want to have another try?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes)

            self.pylonIsConnected = False
            if reply == QMessageBox.Yes:
                self.cameraCheck()
            else:
                self.setBtnEnabled(False)

    def bleCheck(self):
        self.bleIsConnected = self.ble.connect()
        if self.bleIsConnected: print("BLE is connected.")
        else:
            reply = QMessageBox.information(
            self,
            "Failed to connect the BLE",
            "Do you want to have another try?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes)

            self.bleIsConnected = False
            if reply == QMessageBox.Yes:
                self.bleCheck()

    def setBtnEnabled(self, enabled):
        self.btn_cap.setEnabled(enabled)
        self.btn_save.setEnabled(enabled)
        self.btn_del.setEnabled(enabled)
        self.btn_text.setEnabled(enabled)

    def live(self):
        if self.islive: self.capture()
        else:
            self.islive = True
            self.btn_cap.setText('Capture')
            self.scrollArea.setWidgetResizable(True)
            self.label.resize(self.scrollArea.size())
            self.scrollAreaWidgetContents.resize(self.label.size())
            self.label.resizeNeeded = True
            self.scrollArea.setWidgetResizable(False)
            self.videoStart.emit(True) # Signal sending to the working thread
            self.videoThread.start()

    def capture(self): # Will be triggered only if the live function is called
        self.videoStart.emit(False)
        self.image_name = 'image_' + str(self.img_index) + '.png'
        self.islive = False
        self.btn_cap.setText('Live')
        self.able_to_store = True
        self.img_index += 1

    def save(self):
        #TODO: Use another thread to save the full image
        if self.islive or self.label.pixmap is None: return
        if self.able_to_store:
            save_name = os.path.join(self.image_save_path, self.image_name)
            self.image_list.addItem(self.image_name)
            self.label.pixmap.save(save_name, "PNG", 100)
            self.able_to_store = False

    def delete(self):
        if self.islive: return
        cur_index = self.image_list.currentRow()
        self.image_list.takeItem(cur_index)

        if self.image_name is None: return
        cur_file = os.path.join(self.image_save_path, self.image_name)
        if os.path.isfile(cur_file): os.remove(cur_file)
        
        self.image_list.setCurrentRow(cur_index)
        cur_item = self.image_list.currentItem()
        if cur_item is None:
            self.image_name = None
            self.label.pixmap = None
            return
        else:
            self.image_name = cur_item.text()
            
        img_file = os.path.join(self.image_save_path, self.image_name)

        if not os.path.isfile(img_file):
            self.image_name = None
            self.label.pixmap = None
            return
        self.label.pixmap = QPixmap(img_file)
        self.label.update()

    # Check if the image folders exist or not
    # Note: The checkable and auto-exclusive properties are set n the QtDesigner GUI
    def imageFolderCheck(self):
        self.cur_operation = self.btn_queue

        dir_queue = os.path.join(self.image_save_path, "QUEUE")
        dir_1070x = os.path.join(self.image_save_path, "1070X")
        dir_1060x = os.path.join(self.image_save_path, "1060X")
        dir_1030x = os.path.join(self.image_save_path, "1030X")
        dir_cc    = os.path.join(self.image_save_path, "CC-118")
        dir_dry   = os.path.join(self.image_save_path, "DRY")

        if not os.path.exists(dir_queue): os.mkdir(dir_queue)
        if not os.path.exists(dir_1070x): os.mkdir(dir_1070x)
        if not os.path.exists(dir_1060x): os.mkdir(dir_1060x)
        if not os.path.exists(dir_1030x): os.mkdir(dir_1030x)
        if not os.path.exists(dir_cc):    os.mkdir(dir_cc)
        if not os.path.exists(dir_dry):   os.mkdir(dir_dry)

        self.image_save_path = dir_queue # Image save path initialization
        self.setImageList()

    def op_queue(self):
        self.image_save_path = os.path.join(self.image_save_parent, "QUEUE")
        self.cur_operation = self.btn_queue
        self.setImageList()

    def op_1070x(self):
        self.image_save_path = os.path.join(self.image_save_parent, "1070X")
        self.cur_operation = self.btn_1070x
        self.setImageList()

    def op_1060x(self):
        self.image_save_path = os.path.join(self.image_save_parent, "1060X")
        self.cur_operation = self.btn_1060x
        self.setImageList()

    def op_1030x(self):
        self.image_save_path = os.path.join(self.image_save_parent, "1030X")
        self.cur_operation = self.btn_1030x
        self.setImageList()

    def op_cc(self):
        self.image_save_path = os.path.join(self.image_save_parent, "CC-118")
        self.cur_operation = self.btn_cc
        self.setImageList()

    def op_dry(self):
        self.image_save_path = os.path.join(self.image_save_parent, "DRY")
        self.cur_operation = self.btn_dry
        self.setImageList()

    def setImageList(self):
        self.image_list.clear() # Clear all the current items before processing
        img_file_list = glob.glob(self.image_save_path + r"/*.png")
        #print("The current path is", self.image_save_path)
        for img_file in img_file_list:
            _, fname = os.path.split(img_file)
            self.image_list.addItem(fname)
    
    def list_select(self):
        if self.islive: return
        #print("The current row is", self.image_list.currentRow())
        self.image_name = self.image_list.currentItem().text()
        img_file = os.path.join(self.image_save_path, self.image_name)
        
        if not os.path.isfile(img_file):
            self.image_name = None
            self.label.pixmap = None
            return
        self.jsonOperation(img_file)
        self.label.pixmap = QPixmap(img_file)
        self.label.update()

    def setTextMode(self):
        self.btn_undo.setEnabled(False)
        self.textEdit.setEnabled(True)
        self.label.mode = 'text'

    def setDrawMode(self):
        self.btn_undo.setEnabled(True)
        self.textEdit.setEnabled(False)
        self.label.mode = 'draw'

    def undo(self):
        self.label.undo()
        
    def get_operator_name(self):
        operator_name = str(self.line_names.currentText())
        self.operator_name = operator_name

    def jsonOperation(self, img_file):
        temp_name, _ = os.path.splitext(img_file)
        json_file = temp_name + ".json"
        

    def report(self):
        pass

    def scrollRequest(self, delta, orientation):
        units = -delta * 0.1
        if orientation == Qt.Horizontal:
            bar = self.scrollArea.horizontalScrollBar()
            bar.setValue(bar.value() + bar.singleStep()*units)
        elif orientation == Qt.Vertical:
            bar = self.scrollArea.verticalScrollBar()
            bar.setValue(bar.value() + bar.singleStep()*units)

    def zoomRequest(self, delta, pos):
        label_width_old = self.label.width()
        units = 1.1
        if delta < 0: units = 0.9

        self.label.setScaleFactor(units) # Set up self.label.scale
        self.label.resizeNeeded = True
        self.label.resize(self.label.scale * self.label.pixmap.size())
        self.scrollAreaWidgetContents.resize(self.label.size())

        label_width_new = self.label.width()
        if label_width_new != label_width_old:
            x_shift = round(pos.x() * units) - pos.x()
            y_shift = round(pos.y() * units) - pos.y()

        self.scrollArea.horizontalScrollBar().setValue(
            self.scrollArea.horizontalScrollBar().value() + x_shift)
        self.scrollArea.verticalScrollBar().setValue(
            self.scrollArea.verticalScrollBar().value() + y_shift)
        
        
    def eventFilter(self, obj, ev):
        #self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        # TODO: Adding the gesture recognition here ...

        if self.islive: return False

        # Wheel event: zooming and scrolling
        if (ev.type() == QEvent.Wheel) and (obj == self.label):
            mods = ev.modifiers()
            delta = ev.angleDelta()
            if Qt.ControlModifier == int(mods):
                # With Ctrl/Command key - Zoom
                self.zoomRequest(delta.y(), ev.pos())
                ev.accept()
            else:
                # Scroll
                self.scrollRequest(delta.x(), Qt.Horizontal)
                self.scrollRequest(delta.y(), Qt.Vertical)
            return True
        
        elif (ev.type() == QEvent.Gesture) and (obj == self.label):
            g = ev.gesture(Qt.PinchGesture)
            #if g is not None: print(g.scaleFactor()) # The PinchGesture is able to be detected.
            return True
        else:
            return False
        
        return self.label.eventFilter(obj, ev)
            

    def resizeEvent(self, ev):
        # Note 1: While launching the GUI, this function will automatically be called\
        # Note 2: While resizing, the scroll area as well as the contents are resized following the mainwindow
        self.scrollArea.setWidgetResizable(True)
        self.label.resizeNeeded = True
        self.label.resize(self.scrollAreaWidgetContents.size())
        self.label.winGeo = self.scrollArea.geometry()
        self.scrollArea.setWidgetResizable(False)

    def closeEvent(self, ev):
        reply = QMessageBox.question(
            self,
            "Quit Confirm",
            "Are you sure to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes: ev.accept()
        else: ev.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
