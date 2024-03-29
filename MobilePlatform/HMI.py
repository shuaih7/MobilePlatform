#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on 03.17.2020
Updated on 04.21.2020

Author: 212780558
"""

import os, sys
import json, time, glob
from pypylon import genicam

abs_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(abs_path)

try: 
    from .basler_camera import Basler
    from .PassDialog import PassDialog
    from .Workers import pylonWorker, bleWorker, saveWorker, cameraMonitor, bleMonitor
except Exception as expt: 
    from basler_camera import Basler
    from PassDialog import PassDialog
    from Workers import pylonWorker, bleWorker, saveWorker, cameraMonitor, bleMonitor

from PyQt5.uic import loadUi
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QEvent, QSize, QRegExp
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QMessageBox


ADDRESS  = "98:F4:AB:18:CF:16"
CMD_UUID = "73c1298a-0452-4637-89df-816e211a71db"
STA_UUID = "352c2cb8-e15e-49ff-b0fe-3a1ed971dc1e"


class MainWindow(QMainWindow):
    videoStart = pyqtSignal(bool) # Signal to communicate with the video thread
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi(os.path.join(os.path.abspath(os.path.dirname(__file__)), "HMI.ui"), self)

        ######--- Device Settings ---######
        self.basler = None      
        self.islive = False
        self.able_to_store = False
        self.camIsConnected = False
        self.videoThread = None  
        self.camMonitorThread = None
        self.setBtnEnabled(False)
        
        self.bleIsConnected = False
        self.ble = bleWorker(ADDRESS, CMD_UUID, STA_UUID)
        self.bleMonitorThread = None
        self.deviceReinitialization()

        # TODO: rearrange the names ...
        self.image_name = None # Pure image name without path
        self.full_name  = None # Used to save the markings 
        self.parent_path = r"D:" #os.path.join(os.getcwd(), "data") # Parent path for all of the images & notation files
        self.wo_path = None
        self.image_save_path = None
        self.cur_operation = None
        self.operator_name = None
        self.setTextMode()

        self.label.setAttribute(Qt.WA_AcceptTouchEvents) # Enable the Touch event of the MarkLabel
        self.scrollArea.setVisible(True)

        self.label.winSize = [self.scrollArea.width(), self.scrollArea.height()]
        self.label.installEventFilter(self)
        self.label.grabGesture(Qt.PinchGesture)
        self.setMarkBtnEnabled(False)

        self.saveThread = None
        self.status_label.update()
        self.passDialog = PassDialog()
        self.passDialog.adminWidget.camConfigRequest.connect(self.camConfigReceiver)
        self.passDialog.adminWidget.bleSettingRequest.connect(self.updateBleSettings)
        self.passDialog.adminWidget.opListUpdateRequest.connect(self.updateOperatorList)
        self.config_matrix = None
        self.loadConfigurations()
        self.setValidator()

    def deviceReinitialization(self):
        self.cameraReinitialization()
        self.bleReinitialization()
            
    def cameraReinitialization(self):
        if self.camIsConnected: return
        self.basler = Basler()
        self.videoThread = pylonWorker(self.basler.camera, self.label)
        self.videoStart.connect(self.videoThread.videoStatusReceiver)
        
        if self.basler.camera is not None: 
            self.camIsConnected = True
            self.setBtnEnabled(True)
            self.status_label.updateConnectStatus(cam_status=True)
            self.camMonitorThread = cameraMonitor(self.basler.camera)
            self.camMonitorThread.cameraStatus.connect(self.camStatusReceiver)
            self.camMonitorThread.start()
        else:
            reply = QMessageBox.warning(
            self,
            "Failed to connect the pylon camera",
            "Do you want to have another try?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.cameraReinitialization()
    
    def bleReinitialization(self):
        if self.bleIsConnected: return
        if self.ble.connect(): 
            self.bleIsConnected = True
            self.status_label.updateConnectStatus(ble_status=True)
            self.bleMonitorThread = bleMonitor(self.ble)
            self.bleMonitorThread.bleStatus.connect(self.bleStatusReceiver)
            self.bleMonitorThread.start()
        else:
            reply = QMessageBox.warning(
            self,
            "Failed to connect the BLE device",
            "Do you want to have another try?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.bleReinitialization()

    @pyqtSlot(bool)
    def camStatusReceiver(self, cam_status):
        self.camIsConnected = cam_status
        self.status_label.updateConnectStatus(cam_status=cam_status)
        if self.islive: 
            self.islive = False
            self.btn_cap.setText('Live')
        self.setBtnEnabled(False)
        self.resetInputs()
        
    @pyqtSlot(bool)
    def bleStatusReceiver(self, ble_status):
        self.bleIsConnected = ble_status
        self.status_label.updateConnectStatus(ble_status=ble_status)
        
    @pyqtSlot(str)
    def camConfigReceiver(self, config_file):
        if not self.camIsConnected: return
        self.basler.load_configuration(cfg_file=config_file)
        
    def loadConfigurations(self):
        config_file = os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config"), "config.json")
        with open (config_file, "r") as f: self.config_matrix = json.load(f)

        operator_names = self.config_matrix["Names"]
        operator_levels = self.config_matrix["Levels"]
        self.line_name.addItem("--Operator --")
        for name in operator_names: self.line_name.addItem(name)
        self.passDialog.adminWidget.initConfigurations(self.config_matrix)
        
    @pyqtSlot(bool)
    def updateOperatorList(self, updateRequested):
        operator_names = []
        operator_levels = []
        self.line_name.clear()
        self.line_name.addItem("-- Operator --")
            
        for i in range(self.passDialog.adminWidget.op_list.count()):
            name = self.passDialog.adminWidget.op_list.item(i).text()
            level = self.passDialog.adminWidget.level_list.item(i).text()
            if name == "User Name":
                self.passDialog.adminWidget.op_list.takeItem(i)
                self.passDialog.adminWidget.level_list.takeItem(i)
            else:
                self.line_name.addItem(name)
                operator_names.append(name)
                operator_levels.append(level)
            
        if self.config_matrix is not None: # Update the config matrix
            self.config_matrix["Names"] = operator_names
            self.config_matrix["Levels"] = operator_levels 
        self.resetInputs()
            
    @pyqtSlot(bool)
    def updateBleSettings(self, updateRequested):
        self.config_matrix["BleBrightness"] = self.passDialog.adminWidget.bright_slider.value()
        self.config_matrix["BleOnDelay"] = int(self.passDialog.adminWidget.line_ondelay.text())
        self.config_matrix["BleOffDelay"] = int(self.passDialog.adminWidget.line_offdelay.text())

    def setBtnEnabled(self, enabled):
        self.btn_cap.setEnabled(enabled)
        # self.btn_save.setEnabled(enabled)

    def setMarkBtnEnabled(self, enabled):
        self.btn_undo.setEnabled(enabled)
        self.textEdit.setEnabled(enabled)

    def live(self):
        if not self.checkInputs(): return
        if self.islive: self.capture()
        else:
            self.islive = True
            try: self.ble.write(bytearray([1, self.config_matrix["BleBrightness"]]))
            except Exception as expt: print(expt)
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
        """
        if self.config_matrix is not None and self.bleIsConnected: 
            ble_cmd = bytearray([3, self.config_matrix["BleOnDelay"]//20, 
                                 self.config_matrix["BleOffDelay"]//20, self.config_matrix["BleBrightness"]])
            self.ble.write(ble_cmd)
        """
        #time.sleep(0.25) # Wait until the LED is ready 0.1s is an empirical number
        self.videoStart.emit(False)
        self.islive = False
        self.btn_cap.setText('Live')
        self.able_to_store = True
        try: self.ble.write(b"\x02")
        except Exception as expt: print(expt)

    def save(self):
        if self.islive or self.label.pixmap is None: return
        if self.able_to_store:
            localtime = time.localtime(time.time())
            time_string = str(localtime.tm_year)+"-"+str(localtime.tm_mon)+"-"+str(localtime.tm_mday)+"-"+str(localtime.tm_hour)+str(localtime.tm_min)+str(localtime.tm_sec)
            self.image_name = self.part_number+"-"+self.process+"_"+time_string+".bmp"
            self.full_name = os.path.join(self.image_save_path, self.image_name)
            self.able_to_store = False
            self.saveThread = saveWorker(self.full_name, self.label)
            self.saveThread.saveFinished.connect(self.saveStatusReceiver)
            self.saveThread.start()

    @pyqtSlot(str)
    def saveStatusReceiver(self, image_name):
        self.image_list.addItem(image_name)
        self.image_list.setCurrentRow(self.image_list.count()-1)
        self.label.mode = 'text' # After image saving, the marking buttons are enabled

    def delete(self):
        if self.islive: return

        reply = QMessageBox.question(
            self,
            "Delete Confirm",
            "Are you sure to delete this file?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if reply == QMessageBox.No: return
        
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
        img_file_list = glob.glob(self.image_save_path + r"/*.bmp")
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

        if reply == QMessageBox.Yes: 
            if self.config_matrix is not None:
                config_file = os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config"), "config.json")
                with open (config_file, "w") as f: json.dump(self.config_matrix, f, indent=4)
            ev.accept()
        else: ev.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
