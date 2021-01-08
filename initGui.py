from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QMainWindow, QErrorMessage, QMessageBox, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTime, QThread
from PyQt5.QtWidgets import QWidget

#from initFormConfig import FormProc
from mainForm import *
from formLogin import *
from initGuiLogin import *

import numpy as np
import cv2 as cv
import sys






class App(QWidget):

    res_x = 854
    res_y = 480
    
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

    #def __init__(self):
    #    super().__init__()

        self.uiConfig = Ui_formConfig()
        self.uiConfig.setupUi(self)

        # LOGIN ##
          
        
        
        ### Thread OpenCV
        #self.uiInitGui.thread = VideoThread()
        # connect its signal to the update_image slot
        #self.uiInitGui.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        #self.uiInitGui.thread.start()
    
    
if __name__=="__main__":

    app = QApplication(sys.argv)   
    
    

    if windowLogin.isLogged():
        print('main isLogged true')

        uiConfig = FormProc()
        formInitGui = App()
        uiConfig.setupUi(formInitGui)    
        formInitGui.show()
 

    sys.exit(app.exec_())