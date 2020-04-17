#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 03.17.2020
Updated on 04.15.2020

Author: 212780558
"""

import os, sys
import json, time, glob
from pypylon import genicam
from basler_camera import Basler
from PassDialog import PassDialog
from Workers import pylonWorker, bleWorker

from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QEvent, QSize, QRegExp
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QMessageBox


ADDRESS = "98:F4:AB:14:3E:7A"
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

        # TODO: rearrange the names ...
        self.image_name = None # Pure image name without path
        self.full_name  = None # Used to save the markings 
        self.parent_path = os.path.join(os.getcwd(), "data") # Parent path for all of the images & notation files
        self.wo_path = None
        self.image_save_path = None
        self.cur_operation = None

        self.img_index = 0
        self.operator_name = None

        self.label.setAttribute(Qt.WA_AcceptTouchEvents) # Enable the Touch event of the MarkLabel
        self.scrollArea.setVisible(True)

        self.label.winSize = [self.scrollArea.width(), self.scrollArea.height()]
        self.label.installEventFilter(self)
        self.label.grabGesture(Qt.PinchGesture)
        self.setMarkBtnEnabled(False)

        self.ble = bleWorker(ADDRESS, CMD_UUID, STA_UUID)
        self.bleIsConnected = False
        self.bleCheck()
        
        self.status_label.update()
        self.passDialog = PassDialog()
        self.setValidator()

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
        if self.bleIsConnected:
            print("BLE is connected.")
            self.status_label.bleConnected = True
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

    def setMarkBtnEnabled(self, enabled):
        self.btn_undo.setEnabled(enabled)
        self.textEdit.setEnabled(enabled)

    def live(self):
        if not self.checkInputs(): return
        if self.islive: self.capture()
        else:
            self.islive = True
            self.jsonOperation("dump") # Dump the markings and the comments
            self.label.mode = None     # Set the label mode to None
            self.resetMarkings()
            
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
        if self.bleIsConnected: self.ble.write(b"\x03\x04\x0A\x41")
        self.islive = False
        self.btn_cap.setText('Live')
        self.able_to_store = True
        self.img_index += 1

    def save(self):
        #TODO: Use another thread to save the full image
        if self.islive or self.label.pixmap is None: return
        if self.able_to_store:
            self.image_name = 'image_' + str(self.img_index) + '.png'
            self.full_name = os.path.join(self.image_save_path, self.image_name)
            self.image_list.addItem(self.image_name)
            self.label.pixmap.save(self.full_name, "PNG", 100)
            self.able_to_store = False
            self.label.mode = 'text' # After image saving, the marking buttons are enabled

    def delete(self):
        if self.islive: return
        cur_index = self.image_list.currentRow()
        self.image_list.takeItem(cur_index)

        if self.image_name is None: return
        cur_file = os.path.join(self.image_save_path, self.image_name)
        temp_name, _ = os.path.splitext(cur_file)
        js_file = temp_name + ".json" # Get the corresponding json file
        if os.path.isfile(cur_file): os.remove(cur_file)
        if os.path.isfile(js_file): os.remove(js_file)
        
        self.image_list.setCurrentRow(cur_index)
        cur_item = self.image_list.currentItem()
        if cur_item is None:
            self.image_name = None
            self.full_name = None
            self.label.pixmap = None
            return
        else:
            self.image_name = cur_item.text()
            
        self.full_name = os.path.join(self.image_save_path, self.image_name)

        if not os.path.isfile(self.full_name):
            self.image_name = None
            self.full_name = None
            self.label.pixmap = None
            return
        self.label.pixmap = QPixmap(self.full_name)
        self.jsonOperation("load")
        self.label.update()
        
    def open(self):
        if self.islive: self.live()
        select_wo_path = QFileDialog.getExistingDirectory()
        
        flag = True # Flag for checking whether the folder is the work order parent folder
        if not os.path.exists(os.path.join(select_wo_path, "QUEUE")):    flag = False
        elif not os.path.exists(os.path.join(select_wo_path, "1070X")):  flag = False
        elif not os.path.exists(os.path.join(select_wo_path, "1060X")):  flag = False
        elif not os.path.exists(os.path.join(select_wo_path, "1030X")):  flag = False
        elif not os.path.exists(os.path.join(select_wo_path, "CC-118")): flag = False
        elif not os.path.exists(os.path.join(select_wo_path, "DRY")):    flag = False
        
        if flag: 
            self.locateWorkOrderPath(select_wo_path=select_wo_path)
            self.resetInputs()
        else:
            reply = QMessageBox.critical(self, "Path Error", "The path select is not the work order parent folder.", QMessageBox.Yes)

    def exit(self):
        self.close()

    def adminSet(self):
        self.passDialog.show()

    def op_queue(self, isReset=True):     
        if self.cur_operation is not None: self.cur_operation.setChecked(False)
        self.cur_operation = self.btn_queue
        self.cur_operation.setChecked(True)
        
        if self.wo_path is None: return
        self.image_save_path = os.path.join(self.wo_path, "QUEUE")
        self.setImageList()
        if isReset: self.resetInputs()

    def op_1070x(self, isReset=True):
        if self.cur_operation is not None: self.cur_operation.setChecked(False)
        self.cur_operation = self.btn_1070x
        self.cur_operation.setChecked(True)
        
        if self.wo_path is None: return
        self.image_save_path = os.path.join(self.wo_path, "1070X")
        self.setImageList()
        if isReset: self.resetInputs()

    def op_1060x(self, isReset=True):
        if self.cur_operation is not None: self.cur_operation.setChecked(False)
        self.cur_operation = self.btn_1060x
        self.cur_operation.setChecked(True)
        
        if self.wo_path is None: return
        self.image_save_path = os.path.join(self.wo_path, "1060X")
        self.setImageList()
        if isReset: self.resetInputs()

    def op_1030x(self, isReset=True):
        if self.cur_operation is not None: self.cur_operation.setChecked(False)
        self.cur_operation = self.btn_1030x
        self.cur_operation.setChecked(True)
        
        if self.wo_path is None: return
        self.image_save_path = os.path.join(self.wo_path, "1030X")
        self.setImageList()
        if isReset: self.resetInputs()

    def op_cc(self, isReset=True):
        if self.cur_operation is not None: self.cur_operation.setChecked(False)
        self.cur_operation = self.btn_cc
        self.cur_operation.setChecked(True)
        
        if self.wo_path is None: return
        self.image_save_path = os.path.join(self.wo_path, "CC-118")
        self.setImageList()
        if isReset: self.resetInputs()

    def op_dry(self, isReset=True):
        if self.cur_operation is not None: self.cur_operation.setChecked(False)
        self.cur_operation = self.btn_dry
        self.cur_operation.setChecked(True)
        
        if self.wo_path is None: return
        self.image_save_path = os.path.join(self.wo_path, "DRY")
        self.setImageList()
        if isReset: self.resetInputs()

    def setImageList(self):
        self.image_list.clear() # Clear all the current items before processing
        img_file_list = glob.glob(self.image_save_path + r"/*.png")
        #print("The current path is", self.image_save_path)
        for img_file in img_file_list:
            _, fname = os.path.split(img_file)
            self.image_list.addItem(fname)
    
    def listSelect(self):
        if self.islive: return
        if self.label.mode is None: self.label.mode = 'text'
        self.jsonOperation("dump") # Dump the markings and the comments
        self.resetMarkings() # Clear all of the previous markings
        self.image_name = self.image_list.currentItem().text()
        self.full_name = os.path.join(self.image_save_path, self.image_name)
        
        if not os.path.isfile(self.full_name):
            self.image_name = None
            self.full_name = None
            self.label.pixmap = None
            return
        self.jsonOperation("load") # Load the markings and the comments
        self.label.pixmap = QPixmap(self.full_name)
        self.label.update()

    def setTextMode(self):
        if self.islive or self.label.mode is None: return
        self.btn_undo.setEnabled(False)
        self.textEdit.setEnabled(True)
        self.label.mode = 'text'

    def setDrawMode(self):
        if self.islive or self.label.mode is None: return
        self.btn_undo.setEnabled(True)
        self.textEdit.setEnabled(False)
        self.label.mode = 'draw'

    def resetMarkings(self):
        self.textEdit.setPlainText("")
        self.label.points = []
        self.label.mark_index = []

    def undo(self):
        self.label.undo()
        
    def setValidator(self):
        reg_ex_wo = QRegExp("^.{6}$")
        wo_validator = QtGui.QRegExpValidator(reg_ex_wo, self.line_wo)
        reg_ex_pn = QRegExp("^.{10}$")
        pn_validator = QtGui.QRegExpValidator(reg_ex_pn, self.line_pn)
        reg_ex_sn = QRegExp("^.{8}$")
        sn_validator = QtGui.QRegExpValidator(reg_ex_sn, self.line_sn)
        
        self.line_wo.setValidator(wo_validator)
        self.line_pn.setValidator(pn_validator)
        self.line_sn.setValidator(sn_validator)
        
    def getWorkOrder(self):
        if self.line_wo.hasAcceptableInput():
            self.work_order = str(self.line_wo.text())
            self.line_pn.setFocus()
            self.locateWorkOrderPath()
    
    def getPartNumber(self):
        if self.line_pn.hasAcceptableInput():
            self.part_number = str(self.line_pn.text())
            self.line_sn.setFocus()
        
    def getSerialNumber(self):
        if self.line_sn.hasAcceptableInput():
            self.serial_number = str(self.line_sn.text())
            self.line_name.setFocus()
        
    def getOperatorName(self):
        self.operator_name = str(self.line_name.currentText())
        
    def getProcess(self):
        self.process = str(self.line_process.currentText())
        if self.process == "QUEUE":    self.op_queue(isReset=False)
        elif self.process == "1070X":  self.op_1070x(isReset=False)
        elif self.process == "1060X":  self.op_1060x(isReset=False)
        elif self.process == "1030X":  self.op_1030x(isReset=False)
        elif self.process == "CC-118": self.op_cc(isReset=False)
        elif self.process == "DRY":    self.op_dry(isReset=False)
        
    def locateWorkOrderPath(self, select_wo_path=None):
        if select_wo_path is None:
            self.wo_path = os.path.join(self.parent_path, self.work_order)
            if not os.path.exists(self.wo_path): os.mkdir(self.wo_path) # Assume the name format is acceptable
        else:
            self.wo_path = select_wo_path

        dir_queue = os.path.join(self.wo_path, "QUEUE")
        dir_1070x = os.path.join(self.wo_path, "1070X")
        dir_1060x = os.path.join(self.wo_path, "1060X")
        dir_1030x = os.path.join(self.wo_path, "1030X")
        dir_cc    = os.path.join(self.wo_path, "CC-118")
        dir_dry   = os.path.join(self.wo_path, "DRY")

        if not os.path.exists(dir_queue): os.mkdir(dir_queue)
        if not os.path.exists(dir_1070x): os.mkdir(dir_1070x)
        if not os.path.exists(dir_1060x): os.mkdir(dir_1060x)
        if not os.path.exists(dir_1030x): os.mkdir(dir_1030x)
        if not os.path.exists(dir_cc):    os.mkdir(dir_cc)
        if not os.path.exists(dir_dry):   os.mkdir(dir_dry)

        if self.cur_operation is None: 
            self.cur_operation = self.btn_queue
            self.cur_operation.setChecked(True)
            self.image_save_path = dir_queue # Image save path initialization
        elif self.cur_operation == self.btn_queue: self.image_save_path = dir_queue
        elif self.cur_operation == self.btn_1070x: self.image_save_path = dir_1070x
        elif self.cur_operation == self.btn_1060x: self.image_save_path = dir_1060x
        elif self.cur_operation == self.btn_1030x: self.image_save_path = dir_1030x
        elif self.cur_operation == self.btn_cc:    self.image_save_path = dir_cc
        elif self.cur_operation == self.btn_dry:   self.image_save_path = dir_dry
        self.setImageList() 
       
    """
    Check whether the top inputs "work order", "part numnber", "serial number", "operator name", "process" has been satisfied.
    ---
    :return: The input status -> Inputs are accepted or not.
    """
    def checkInputs(self) -> bool:
        error_msg = None
        if not self.line_wo.hasAcceptableInput() and error_msg is None: error_msg = r"Unaccepted work order."
        if not self.line_pn.hasAcceptableInput() and error_msg is None: error_msg = r"Unaccepted part number."
        if not self.line_sn.hasAcceptableInput() and error_msg is None: error_msg = r"Unaccepted serial number."
        if self.line_name.currentIndex() == 0 and error_msg is None:    error_msg = r"Please specify the operator."
        if self.line_process.currentIndex() == 0 and error_msg is None: error_msg = r"Please specify the process."
        
        if error_msg is not None:
            reply = QMessageBox.critical(
                self,
                "Input Error",
                error_msg,
                QMessageBox.Yes)
            return False
        else: return True

    def resetInputs(self):
        self.line_wo.clear()
        self.line_pn.clear()
        self.line_sn.clear()
        self.line_name.setCurrentIndex(0)
        self.line_process.setCurrentIndex(0)

    def jsonOperation(self, mode="load"):
        if (self.full_name is None) or (self.islive) or (self.label.mode is None): return

        temp_name, _ = os.path.splitext(self.full_name)
        json_file = temp_name + ".json"

        if mode == "load":
            if not os.path.isfile(json_file): return
            with open (json_file, "r") as f:
                js_obj = json.load(f)
                self.textEdit.setPlainText(js_obj["comments"])
                self.label.points = js_obj["points"]
                self.label.mark_index = js_obj["mark_index"]
                self.label.update()

        elif mode == "dump":
            js_obj = {
                    "comments":   self.textEdit.toPlainText(),
                    "points":     self.label.points,
                    "mark_index": self.label.mark_index
                }
            with open (json_file, "w") as f:
                json.dump(js_obj, f, indent=None)

    """
    def test(self):
        if self.basler is None or self.basler.configuration is None or self.islive: return
        config = self.basler.configuration
        exp_time = 0
        for feature in config["features"]:
            if feature["name"] == "ExposureTime":
                feature["value"] = feature["value"] + 10000
                if feature["value"] >= feature["max"]: feature["value"] = feature["min"]
                exp_time = feature["value"]
        #print(config)
        #self.basler.camera.ExposureAuto.SetValue("Off")
        #self.basler.camera.ExposureTime.SetValue(exp_time)
        #self.basler.camera.AcquisitionFrameRateEnabled.SetValue(True)
        #self.basler.camera.AcquisitionFrameRate.SetValue(40.0)
        print("The current frame rate is", self.basler.camera.ResultingFrameRate.GetValue())
    """

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
        if not self.islive and self.label.mode is not None:
            self.jsonOperation("dump") # Dump the markings and the comments
            
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
