# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 14:48:07 2022

@author: lowes
"""


import sys
import vtk
import os
import numpy as np
import glob
import PyQt5
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import pydicom as dcm
from pydicom.errors import InvalidDicomError
from vtk.util.numpy_support import numpy_to_vtk
from vtkmodules.vtkCommonColor import vtkNamedColors
from annotator_label import Annotator
from scipy.ndimage import gaussian_filter

class KeyHelper(QtCore.QObject):
    keyPressed = QtCore.pyqtSignal(QtCore.Qt.Key)

    def __init__(self, window):
        super().__init__(window)
        self._window = window

        self.window.installEventFilter(self)

    @property
    def window(self):
        return self._window

    def eventFilter(self, obj, event):
        if obj is self.window and event.type() == PyQt5.QtCore.QEvent.KeyPress:
            self.keyPressed.emit(event.key())
        return super().eventFilter(obj, event)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, filelist, label_path, save_path, parent=None):
        super(MainWindow,self).__init__(parent)
        self.setObjectName("MainWindow")
        volShape = [960,960]
        self.frame = QtWidgets.QFrame()
        self.hl = QtWidgets.QHBoxLayout()
        
        
        self.annotator = Annotator.fromFileList(filelist, label_path, save_path)
        self.widget = QtWidgets.QWidget()
        self.createButtons()
        
        self.split = QtWidgets.QSplitter(PyQt5.QtCore.Qt.Vertical)
        self.split.addWidget(self.widget)
        self.split.addWidget(self.annotator)
        
        # self.split.setSizes(volShape)
        
        self.image_viewer = None
        self.slice_text_mapper = None
        
            
        
        self.hl.addWidget(self.split)
        self.frame.setLayout(self.hl)
        self.setCentralWidget(self.frame)
        self.showMaximized()
        self.show()

    def createButtons(self):
        
        self.colors = np.array([
            [0, 0, 0], # background, transparency is always drawn with black
            [255, 0, 0], # label 1
            [0, 191, 0], # label 2
            [0, 0, 255], # etc
            [255, 127, 0],
            [0, 255, 191],
            [127, 0, 255],
            [191, 255, 0],
            [0, 127, 255],
            [255, 64, 191]])
        
        button1 = QtWidgets.QPushButton(self.widget)
        button1.setText("Reset Image")
        button1.move(100,32)
        button1.clicked.connect(self.resetImageButton)
        button1.setStyleSheet("background-color:rgb(255,255,255);"+
                            "border-style: outset;"+
                            "border-width: 2px;"+
                            "border-radius: 10px;"+
                            "border-color: gray;"+
                            "font: bold 10px;"+
                            "min-width: 6em;"+
                            "padding: 5px;"
                            )
         
        button2 = QtWidgets.QPushButton(self.widget)
        button2.setText("Save and Next")
        button2.move(200,32)
        button2.clicked.connect(self.annotatorSave)
        button2.setStyleSheet("background-color:rgb(255,255,255);"+
                            "border-style: outset;"+
                            "border-width: 2px;"+
                            "border-radius: 10px;"+
                            "border-color: gray;"+
                            "font: bold 10px;"+
                            "min-width: 6em;"+
                            "padding: 5px;"
                            )
        button3 = QtWidgets.QPushButton(self.widget)
        button3.setText("Undo")
        button3.move(300,32)
        button3.clicked.connect(self.annotatorUndo)
        button3.setStyleSheet("background-color:rgb(255,255,255);"+
                            "border-style: outset;"+
                            "border-width: 2px;"+
                            "border-radius: 10px;"+
                            "border-color: gray;"+
                            "font: bold 10px;"+
                            "min-width: 6em;"+
                            "padding: 5px;"
                            )
        button4 = QtWidgets.QPushButton(self.widget)
        button4.setText("Show Help")
        button4.move(400,32)
        button4.clicked.connect(self.annotatorHelp)
        button4.setStyleSheet("background-color:rgb(255,255,255);"+
                            "border-style: outset;"+
                            "border-width: 2px;"+
                            "border-radius: 10px;"+
                            "border-color: gray;"+
                            "font: bold 10px;"+
                            "min-width: 6em;"+
                            "padding: 5px;"
                            )
        
        label1 = QtWidgets.QPushButton(self.widget)
        label1.setText("Label1")
        label1.move(1500,32)
        label1.clicked.connect(self.changeToLabel1)
        r,g,b = self.colors[1]
        label1.setStyleSheet(f"background-color:rgb({r},{g},{b});"+
                            "border-style: outset;"+
                            "border-width: 2px;"+
                            "border-radius: 10px;"+
                            "border-color: beige;"+
                            "font: bold 10px;"+
                            "min-width: 6em;"+
                            "padding: 5px;"
                            )
        
        label2 = QtWidgets.QPushButton(self.widget)
        label2.setText("Label2")
        label2.move(1600,32)
        label2.clicked.connect(self.changeToLabel2)
        r,g,b = self.colors[2]
        label2.setStyleSheet(f"background-color:rgb({r},{g},{b});"+
                            "border-style: outset;"+
                            "border-width: 2px;"+
                            "border-radius: 10px;"+
                            "border-color: beige;"+
                            "font: bold 10px;"+
                            "min-width: 6em;"+
                            "padding: 5px;"
                            )
        
        label3 = QtWidgets.QPushButton(self.widget)
        label3.setText("Label3")
        label3.move(1700,32)
        label3.clicked.connect(self.changeToLabel3)
        r,g,b = self.colors[3]
        label3.setStyleSheet(f"background-color:rgb({r},{g},{b});"+
                            "border-style: outset;"+
                            "border-width: 2px;"+
                            "border-radius: 10px;"+
                            "border-color: beige;"+
                            "font: bold 10px;"+
                            "min-width: 6em;"+
                            "padding: 5px;"
                            )
        label0 = QtWidgets.QPushButton(self.widget)
        label0.setText("Erasor")
        label0.move(1800,32)
        label0.clicked.connect(self.changeToLabel0)
        r,g,b = self.colors[3]
        label0.setStyleSheet("background-color:rgb(200,200,200);"+
                            "border-style: outset;"+
                            "border-width: 2px;"+
                            "border-radius: 10px;"+
                            "border-color: beige;"+
                            "font: bold 10px;"+
                            "min-width: 6em;"+
                            "padding: 5px;"
                            )
        self.widget.setGeometry(50,50,320,200)
        self.widget.setWindowTitle("PyQt5 Button Click Example")
    
    
    def closeEvent(self, QCloseEvent):
        super().closeEvent(QCloseEvent)
        QtWidgets.QApplication.quit()
 

    # def mouseReleaseEvent(self, event):
    #     self.volFrame.mouseReleaseEvent1(event)
   
    def handle_key_pressed(self, event):
        # print("Key event")
        # print(event)
        self.annotator.keyPressEvent1(event)
        
    def resetImageButton(self):
        self.annotator.reset_current_image()
    def annotatorUndo(self):
        self.annotator.keyPressEvent1(PyQt5.QtCore.Qt.Key_Z)
    def annotatorSave(self):
        self.annotator.keyPressEvent1(PyQt5.QtCore.Qt.Key_I)
    def annotatorHelp(self):
        self.annotator.keyPressEvent1(PyQt5.QtCore.Qt.Key_H)
        
        
    def changeToLabel0(self):
        self.setLabel(0)
    def changeToLabel1(self):
        self.setLabel(1)
    def changeToLabel2(self):
        self.setLabel(2)
    def changeToLabel3(self):
        self.setLabel(3)
    def setLabel(self,i):
        pyqt_i = i+48
        self.annotator.keyPressEvent1(pyqt_i) 
        
def button1_clicked():
   print("Button 1 clicked")

def button2_clicked():
   print("Button 2 clicked")  
    
if __name__ == "__main__":
    app = QtWidgets.QApplication([])


    path = "C:/Users/lowes/OneDrive/Skrivebord/DTU/8_semester/General_Interactive_Segmentation"
    filelist = np.array(glob.glob(os.path.join(path,'benchmark/dataset/img',"*.jpg")))
                         
    np.random.seed(69)
    datasplit=[0.8,0.1,0.1]
    N = len(filelist)

    idx_perm = np.random.permutation(N)
    i1 = int(N*datasplit[0])
    i2 = int(N*(datasplit[0]+datasplit[1]))
    # dataset_split[key]["train"] = idx_perm[:i1]
    # dataset_split[key]["vali"] = idx_perm[i1:i2]
    # dataset_split[key]["test"] = idx_perm[i2:]
    files = filelist[idx_perm[i2:]].tolist()

    label_path = ""#os.path.join(path, "CHAOS/labels")
                         
    save_path = os.path.join(path, "pascal_annotated_data")

    window = MainWindow(files, label_path, save_path)
    
    window.show()
    helper = KeyHelper(window.windowHandle())
    helper.keyPressed.connect(window.handle_key_pressed)
    app.exec()
