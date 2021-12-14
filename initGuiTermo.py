from PyQt5.QtWidgets import QWidget, QDialog 
from PyQt5 import QtCore 
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
import utilsCore as utils
from utilsCore import StatusConfig
import logging as log
import secrets
import psutil
from formTermos import *
import sys

if sys.platform == 'linux':
    OS_PLATFORM = 'linux'
else:
    OS_PLATFORM = 'windows'
    import winshell
    from win32com.client import Dispatch


class FormTermo(QDialog):

    statusConfig = StatusConfig()        
    
    updateStatusLogin = pyqtSignal(bool)

    def __init__(self, parent=None ):
        log.info('initFormTermo:: __init__')

        super(FormTermo, self).__init__(parent)
        #Dialog = QtWidgets.QDialog()
        self.uiTermo = Ui_DialogTermosUso()
        self.uiTermo.setupUi(self)
        
        self.uiTermo.btnOk.clicked.connect(self.btnOk)        
        self.uiTermo.checkBoxAceite.stateChanged.connect(self.checkBoxAceite)
        self.uiTermo.checkBoxNaoAceite.stateChanged.connect(self.checkBoxNaoAceite)             

       
    
    def checkBoxAceite(self, state):         
        
        if state == 0:            
            log.info('checkBoxAceite:: False')
            self.statusConfig.setPrimeiroUso('True')                       

        elif (state == 1 or state == 2):
            
            log.info('checkBoxAceite:: True')
            self.statusConfig.setPrimeiroUso('False') 
            self.uiTermo.checkBoxNaoAceite.setChecked(False)
            
    
    def checkBoxNaoAceite(self, state):         
        
        if state == 0:            
            log.info('checkBoxNaoAceite:: False')
            #self.statusConfig.setPrimeiroUso('False')                       

        elif (state == 1 or state == 2):
        
            log.info('checkBoxNaoAceite:: True')
            self.statusConfig.setPrimeiroUso('True') 
            self.uiTermo.checkBoxAceite.setChecked(False)
    
        
    def btnOk(self):        
        log.info('initFormTermo:: btnOk')                       
        self.close()

    def closeEvent(self, event):      
        log.info('close formLogin')
        self.close()

