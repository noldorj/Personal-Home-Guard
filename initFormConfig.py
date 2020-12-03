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
from objectTracking.pyimagesearch.centroidtracker import CentroidTracker
from camRunTime import *
from utilsCore import StatusConfig

import time
import numpy as np
import cv2 as cv
import sys
import time
import logging as log
from inferenceCore import *

from collections import deque

log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.DEBUG, stream=sys.stdout)


class FormProc(QWidget):

    
    statusConfig = StatusConfig()
    
    camRunTime = CamRunTime()

    infCam = InferenceCore()
    
    token = secrets.token_urlsafe(20)

    

    def __init__(self, parent=None):
        super(FormProc, self).__init__(parent)
        self._run_flag = True
        self.uiConfig = Ui_formConfig()
        self.uiConfig.setupUi(self)

        self.camRunTime.init()
        self.statusConfig = utils.StatusConfig()
        

        #self.camRunTime.listCamAtivas = self.statusConfig.getListCamAtivas()
        #self.camRunTime.listCamEncontradas = self.statusConfig.getListCamEncontradas()
        
        
        #slots
        self.uiConfig.btnSaveEmail.clicked.connect(self.btnSaveEmail)
        self.uiConfig.btnSaveStorage.clicked.connect(self.btnSaveStorage)

        self.uiConfig.btnAtivarCam.clicked.connect(self.btnAtivarCam)
        self.uiConfig.btnProcurarCam.clicked.connect(self.btnProcurarCam)
        self.uiConfig.btnTestarConfigCam.clicked.connect(self.btnTestarConfigCam)

        self.uiConfig.checkBoxWebCam.stateChanged.connect(self.checkBoxWebcamStateChanged)
        self.uiConfig.checkBoxDesabilitarLoginAutomatico.stateChanged.connect(self.checkBoxDesabilitarLoginAutomatico)
       
        self.uiConfig.checkBoxNoLimitsVideosAllTime.stateChanged.connect(self.checkBoxNoLimitsVideosAllTime)
        self.uiConfig.checkBoxNoLimitsVideosOnAlarmes.stateChanged.connect(self.checkBoxNoLimitsVideosOnAlarmes)

        self.uiConfig.comboRegions.activated['int'].connect(self.comboRegionsUpdate)
        self.uiConfig.comboAlarms.activated['int'].connect(self.comboAlarmsUpdate)
        self.uiConfig.btnSaveAlarm.clicked.connect(self.btnSaveAlarm)
        self.uiConfig.btnSaveRegion.clicked.connect(self.btnSaveRegion)
        self.uiConfig.btnDeleteAlarm.clicked.connect(self.btnDeleteAlarm)
        self.uiConfig.btnDeleteRegion.clicked.connect(self.btnDeleteRegion)
        self.uiConfig.btnCancelAlarm.clicked.connect(self.btnCancelAlarm)
        self.uiConfig.btnCancelRegion.clicked.connect(self.btnCancelRegion)
        self.uiConfig.btnNewRegion.clicked.connect(self.btnNewRegion)
        self.uiConfig.btnNewAlarm.clicked.connect(self.btnNewAlarm)

        
        
        # ----------- init tab configuração geral --------------- 
        self.uiConfig.btnSaveEmail.setEnabled(True)
        self.fillTabGeral()

        # ----------- init tab adicionar regioes --------------- 
        if not self.statusConfig.isRegionsEmpty():
            self.uiConfig.btnDeleteRegion.setEnabled(True)
            self.uiConfig.btnDeleteAlarm.setEnabled(True)

            for r in self.camRunTime.regions:
                self.uiConfig.comboRegions.addItem(r.get("nameRegion"))
            self.comboRegionsUpdate(self.uiConfig.comboRegions.currentIndex())
            self.comboAlarmsUpdate(self.uiConfig.comboAlarms.currentIndex())
        else:
            self.uiConfig.btnDeleteRegion.setEnabled(False)
            self.uiConfig.btnDeleteAlarm.setEnabled(False)

        self.uiConfig.btnSaveAlarm.setEnabled(True)
        self.uiConfig.btnCancelRegion.setEnabled(False)
        self.uiConfig.btnCancelAlarm.setEnabled(False)    
        self.uiConfig.btnNewAlarm.setEnabled(True)
        self.uiConfig.comboAlarms.setEnabled(True)

        

        if self.camRunTime.LOGIN_AUTOMATICO:
            log.debug('Iniciando login automatico')
            self.loginAutomatico()
            #utils.initWatchDog() 

        else:
            ## CHAMANDO TELA DE LOGIN ## 
            appLogin = QApplication(sys.argv)          
            uiLogin = Ui_formLogin()
            windowLogin = FormLogin(self.camRunTime, self.statusConfig)            
            windowLogin.setBackStatusConfigCamRunTime.connect(self.updateStatusConfigCamRunTime)                    
            #uiLogin.setupUi(windowLogin)                       
            windowLogin.show()  
            appLogin.exec_()
            
            #sys.exit(appLogin.exec_())                
            #utils.initWatchDog() 

        #implementar logica de checar licença TO-DO
        print('formConfig statusLicence: ' + str(self.camRunTime.statusLicence))
        if self.camRunTime.statusLicence: 

            print('init Thread OpenCV')        
            ### Thread OpenCV
            self.infCam.setCamRunTime(self.camRunTime)
            self.uiConfig.thread = self.infCam
            # connect its signal to the update_image slot
            self.uiConfig.thread.change_pixmap_signal.connect(self.update_image)
            # start the thread
            self.uiConfig.thread.start()

        elif self.camRunTime.rtspStatus:
            print('Erro ao conectar a câmera')
            self.uiConfig.lblCam1.setText('Câmera com erro de conexão. Procure ou configure uma nova câmera.')

                # initOpenVino()
                
            # else:
                # msg = QMessageBox()
                # msg.setIcon(QMessageBox.Information)
                # msg.setText("Camera não configurada ou com erro de configuração. Checar configurações de RTSP")
                # msg.setWindowTitle("Camera não configurada")
                # msg.exec()
                # #log.info('qmessageBox rtspStatus: {}'.format(rtspStatus))
                # callbackButtonRegioes(None, 2)
       


    def run(self):              

        print('\n run')
        #self.statusConfig = statusConfig        
        #windowConfig.show()
    
    @pyqtSlot(StatusConfig, CamRunTime)
    def updateStatusConfigCamRunTime(self, statusConfig, camRunTime):
        print('updateStatusConfigRunTime')
        self.statusConfig = statusConfig
        self.camRunTime = camRunTime
        print('updateStatusConfig statusLicence: ' + str(self.camRunTime.statusLicence))


    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        #print('update_image')
        #"""Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.uiConfig.lblCam1.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.camRunTime.RES_X, self.camRunTime.RES_Y, Qt.KeepAspectRatio)
        
        return QPixmap.fromImage(p)

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()           

    def closeEvent(self, event):
        print('closeEvent')
        self._run_flag = False        
        statusFields = True
        pausaConfig = False     
        self.uiConfig.thread.stop()
        #event.accept()

    def btnDeleteAlarm(self):
        
        self.statusConfig.deleteAlarm(self.uiConfig.comboRegions.currentText(), self.uiConfig.comboAlarms.currentText())
        self.refreshStatusConfig()
        self.comboRegionsUpdate(0)
        self.comboAlarmsUpdate(0)

    def btnDeleteRegion(self):
        self.statusConfig.deleteRegion(self.uiConfig.comboRegions.currentText())
        self.refreshStatusConfig()
        self.comboRegionsUpdate(0)
        self.comboAlarmsUpdate(0)

    def btnSaveEmail(self):
        #global self.uiConfig

        statusFields = True 
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Campo em branco")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        #checando campos em branco

        if len(self.uiConfig.txtEmailName.text()) == 0:
            msg.setText("Campo 'Nome' em branco")
            msg.exec()
            self.uiConfig.txtEmailNome.setFocus()
            statusFields = False

        elif len(self.uiConfig.txtEmailPort.text()) == 0:
            msg.setText("Campo 'Porta' em branco")
            msg.exec()
            self.uiConfig.txtEmailPort.setFocus()
            statusFields = False

        elif len(self.uiConfig.txtEmailSmtp.text()) == 0:
            msg.setText("Campo 'SMTP' em branco")
            msg.exec()
            self.uiConfig.txtEmailSmtp.setFocus()
            statusFields = False

        elif len(self.uiConfig.txtEmailUser.text()) == 0:
            msg.setText("Campo 'Usuário' em branco")
            msg.exec()
            self.uiConfig.txtEmailUser.setFocus()
            statusFields = False

        elif len(self.uiConfig.txtEmailPassword.text()) == 0:
            msg.setText("Campo 'Senha' em branco")
            msg.exec()
            self.uiConfig.txtEmailPassword.setFocus()
            statusFields = False

        elif len(self.uiConfig.txtEmailSubject.text()) == 0:
            msg.setText("Campo 'Assunto' em branco")
            msg.exec()
            self.uiConfig.txtEmailSubject.setFocus()
            statusFields = False

        elif len(self.uiConfig.txtEmailTo.text()) == 0:
            msg.setText("Campo 'Destinatários' em branco")
            msg.exec()
            self.uiConfig.txtEmailTo.setFocus()
            statusFields = False


        elif  self.uiConfig.checkBoxVideoRecordingAllTime.isChecked() and len(self.uiConfig.txtDirRecordingAllTime.text()) ==  0:
            msg.setText("Campo 'Diretório de gravação 24h' em branco")
            msg.exec()
            self.uiConfig.txtDirRecordingAllTime.setFocus()
            statusFields = False


        elif  self.uiConfig.checkBoxVideoRecordingOnAlarmes.isChecked() and len(self.uiConfig.txtDirRecordingOnAlarmes.text()) ==  0:
            msg.setText("Campo 'Diretório de gravação de Alarmes' em branco")
            msg.exec()
            self.uiConfig.txtDirRecordingOnAlarmes.setFocus()
            statusFields = False



        elif  self.uiConfig.checkBoxWebCam.isChecked() and len(self.uiConfig.txtUrlRstp.text()) > 0:
            msg.setText("Escolha somente 'Capturar da Webcam' ou 'Câmera RSTP'")
            msg.exec()
            self.uiConfig.txtUrlRstp.setFocus()
            statusFields = False


        if statusFields:
            camSource = "webcam" if self.uiConfig.checkBoxWebCam.isChecked() else self.uiConfig.txtUrlRstp.text()
            isRecordingAllTime = "True" if self.uiConfig.checkBoxVideoRecordingAllTime.isChecked() else "False"
            isRecordingOnAlarmes = "True" if self.uiConfig.checkBoxVideoRecordingOnAlarmes.isChecked() else "False"

             
            passwd = utils.encrypt(self.uiConfig.txtEmailPassword.text())

            statusConfig.addConfigGeral(self.uiConfig.txtEmailName.text(),
                                  self.uiConfig.txtEmailPort.text(),
                                  self.uiConfig.txtEmailSmtp.text(),
                                  self.uiConfig.txtEmailUser.text(),
                                  passwd,
                                  self.uiConfig.txtEmailSubject.text(),
                                  self.uiConfig.txtEmailTo.text(),
                                  isRecordingAllTime,
                                  isRecordingOnAlarmes,
                                  self.uiConfig.txtDirRecordingAllTime.text(),
                                  self.uiConfig.txtDirRecordingOnAlarmes.text(),
                                  camSource, 
                                  self.uiConfig.txtAvisoUtilizacaoHD.text())


            self.refreshStatusConfig()
            self.clearFieldsTabGeralEmail()
            self.fillTabGeral()

            self.camRunTime.init() 

    def btnCancelRegion(self):
        if len(self.camRunTime.regions) > 0:
            self.uiConfig.btnDeleteRegion.setEnabled(True)
        else:
            self.uiConfig.btnDeleteRegion.setEnabled(False)

        self.uiConfig.btnNewRegion.setEnabled(True)
        self.uiConfig.btnNewAlarm.setEnabled(True)
        #self.uiConfig.btnSaveRegion.setEnabled(False)
        self.uiConfig.btnCancelRegion.setEnabled(False)
        self.clearFieldsTabRegiao()
        self.comboRegionsUpdate(0)

        global portaoVirtualSelecionado, portaoVirtualSelecionado, cropPolygon
        self.camRunTime.portaoVirtualSelecionado = True
        self.camRunTime.portaoVirtualSelecionado = True
        self.camRunTime.ref_point_polygon.clear()
        self.camRunTime.cropPolygon = False

    def btnCancelAlarm(self):
        self.uiConfig.btnDeleteAlarm.setEnabled(True)
        self.uiConfig.btnCancelAlarm.setEnabled(False)
        self.uiConfig.btnNewAlarm.setEnabled(True)
        self.uiConfig.comboAlarms.setEnabled(True)
        self.comboRegionsUpdate(self.uiConfig.comboRegions.currentIndex())

    def btnNewRegion(self):
        #global portaoVirtualSelecionado, ref_point_polygon

        self.camRunTime.portaoVirtualSelecionado = False
        self.camRunTime.ref_point_polygon.clear()

        #clear fields
        self.clearFieldsTabRegiao()
        #self.uiConfig.comboRegions.clear()
        self.uiConfig.btnCancelRegion.setEnabled(True)
        self.uiConfig.btnDeleteRegion.setEnabled(False)
        self.uiConfig.btnSaveRegion.setEnabled(True)
        self.uiConfig.btnDeleteAlarm.setEnabled(False)
        self.uiConfig.btnCancelAlarm.setEnabled(False)
        self.uiConfig.btnSaveAlarm.setEnabled(False)

    def btnSaveRegion(self):
        statusFields = True
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Campo em branco")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        #global ref_point_polygon, portaoVirtualSelecionado, cropPolygon

        #checando campos em branco

        if len(self.uiConfig.txtRegionName.text()) == 0:
            msg.setText("Campo 'Nome da Região' em branco")
            msg.exec()
            self.uiConfig.txtRegionName.setFocus()
            statusFields = False

        elif len(self.uiConfig.txtThreshold.text()) == 0:
            msg.setText("Campo 'Acurácia' em branco")
            msg.exec()
            self.uiConfig.txtThreshold.setFocus()
            statusFields = False

        elif len(self.uiConfig.txtNameAlarm.text()) == 0:
            msg.setText("Campo 'Nome do Alarme' em branco")
            msg.exec()
            self.uiConfig.txtNameAlarm.setFocus()
            statusFields = False

        elif len(ref_point_polygon) == 0 and not self.statusConfig.checkNameRegion(self.uiConfig.txtRegionName.text()):
            msg.setText("Região não selecionada! manter tecla CTRL pressionada até selecionar todos os pontos desejados")
            msg.exec()
            self.camRunTime.portaoVirtualSelecionado = False


        points = []

        t = {'start':{'hour':self.uiConfig.timeStart.time().hour(), 'min':self.uiConfig.timeStart.time().minute()},
             'end':{'hour':self.uiConfig.timeEnd.time().hour(), 'min':self.uiConfig.timeEnd.time().minute()}}

        days = {'mon':'True' if self.uiConfig.checkMon.isChecked() else 'False',
                'tue':'True' if self.uiConfig.checkTue.isChecked() else 'False',
                'wed':'True' if self.uiConfig.checkWed.isChecked() else 'False',
                'thu':'True' if self.uiConfig.checkThur.isChecked() else 'False',
                'fri':'True' if self.uiConfig.checkFri.isChecked() else 'False',
                'sat':'True' if self.uiConfig.checkSat.isChecked() else 'False',
                'sun':'True' if self.uiConfig.checkSun.isChecked() else 'False'
               }
        newAlarm = [{"name":self.uiConfig.txtNameAlarm.displayText(), 'time':t, 'days':days, 
                     'isEmailAlert':'True' if self.uiConfig.checkEmailAlert.isChecked() else 'False',
                     'isSoundAlert':'True' if self.uiConfig.checkAlertSound.isChecked() else 'False'
                    }]

        objectType = {'person':'True' if self.uiConfig.checkPerson.isChecked() else 'False',
                      'car':'True' if self.uiConfig.checkCar.isChecked() else 'False',
                      'bike':'True' if self.uiConfig.checkBike.isChecked() else 'False',
                      'dog':'True' if self.uiConfig.checkDog.isChecked() else 'False'}


        if statusFields:

            if len(ref_point_polygon) == 0 and statusConfig.checkNameRegion(self.uiConfig.txtRegionName.text()):
                points = statusConfig.getRegion(self.uiConfig.txtRegionName.text()).get('pointsPolygon')

            else:
                points = ref_point_polygon

            statusConfig.addRegion(self.uiConfig.txtRegionName.displayText(),
                                   newAlarm, objectType, round(float(self.uiConfig.txtThreshold.displayText()),2), points )
            self.refreshStatusConfig()
            self.comboRegionsUpdate(self.uiConfig.comboRegions.currentIndex())
            self.comboAlarmsUpdate(0)
            #self.uiConfig.btnSaveRegion.setEnabled(False)
            self.uiConfig.btnCancelRegion.setEnabled(False)

            self.camRunTime.portaoVirtualSelecionado = True
            self.camRunTime.ref_point_polygon.clear()
            self.camRunTime.cropPolygon = False

    def btnSaveAlarm(self):
        statusFields = True
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Campo em branco")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        #checando campos em branco

        if len(self.uiConfig.txtNameAlarm.text()) == 0:
            msg.setText("Campo 'Nome do Alarme' em branco")
            msg.exec()
            self.uiConfig.txtNameAlarm.setFocus()
            statusFields = False

        if statusFields:

            t = {'start':{'hour':self.uiConfig.timeStart.time().hour(), 'min':self.uiConfig.timeStart.time().minute()},
                 'end':{'hour':self.uiConfig.timeEnd.time().hour(), 'min':self.uiConfig.timeEnd.time().minute()}}
            days = {'mon':'True' if self.uiConfig.checkMon.isChecked() else 'False',
                    'tue':'True' if self.uiConfig.checkTue.isChecked() else 'False',
                    'wed':'True' if self.uiConfig.checkWed.isChecked() else 'False',
                    'thu':'True' if self.uiConfig.checkThur.isChecked() else 'False',
                    'fri':'True' if self.uiConfig.checkFri.isChecked() else 'False',
                    'sat':'True' if self.uiConfig.checkSat.isChecked() else 'False',
                    'sun':'True' if self.uiConfig.checkSun.isChecked() else 'False'
                   }
            a = {"name":self.uiConfig.txtNameAlarm.displayText(), 'time':t, 'days':days, 
                         'isEmailAlert':'True' if self.uiConfig.checkEmailAlert.isChecked() else 'False',
                         'isSoundAlert':'True' if self.uiConfig.checkAlertSound.isChecked() else 'False'
                        }
            self.statusConfig.addAlarm(self.uiConfig.comboRegions.currentIndex(), a)
            self.refreshStatusConfig()

            self.comboRegionsUpdate(self.uiConfig.comboRegions.currentIndex())
            self.uiConfig.btnSaveAlarm.setEnabled(True)
            self.uiConfig.btnDeleteAlarm.setEnabled(False)
            self.uiConfig.btnCancelAlarm.setEnabled(False)
            self.uiConfig.btnNewAlarm.setEnabled(True)
            self.uiConfig.comboAlarms.setEnabled(True)

    def clearListCameras(self):
        

        self.uiConfig.comboBoxCamAtivas.clear()
        self.uiConfig.comboBoxCamEncontradas.clear()
        
        self.uiConfig.txtUserCamDisponivel.clear()
        self.uiConfig.txtPasswdCamDisponivel.clear()
        self.uiConfig.txtPortaCamDisponivel.clear()
        self.uiConfig.txtCanalCamDiponivel.clear()
        self.uiConfig.lblStatusTestarCam.clear()

    def clearFieldsTabGeralEmail(self):
        

        self.uiConfig.txtEmailName.clear()
        self.uiConfig.txtEmailPort.clear()
        self.uiConfig.txtEmailSmtp.clear()
        self.uiConfig.txtEmailSubject.clear()
        self.uiConfig.txtEmailTo.clear()
        self.uiConfig.txtEmailUser.clear()
        self.uiConfig.txtEmailPassword.clear()
        self.uiConfig.lblStatus.clear()
        self.uiConfig.lblStatusProcurarCam.clear()

    def btnAtivarCam(self):
        #global listCamAtivas, self.uiConfig, statusConfig

        log.debug('Ativando camera selecionada')
        
        if len(self.camRunTime.listCamAtivas) > 0: 
            idCombo = self.uiConfig.comboBoxCamAtivas.currentText().split(':')[0]
            idCombo = idCombo.replace('[','')
            idCombo = idCombo.replace(']','')
            log.debug('idCombo: ' + idCombo)

            i = 0 
            #zerando a camera ativada anteriormente 
            for cam in self.camRunTime.listCamAtivas:
                self.camRunTime.listCamAtivas[i]['emUso'] = 'False'
                i = i + 1

            i = 0 
            for cam in self.camRunTime.listCamAtivas:
                if cam.get('id') == idCombo:
                    self.camRunTime.listCamAtivas[i]['emUso'] = 'True'
                    log.debug('cam source: ' + cam.get('source'))
                    self.uiConfig.txtUrlRstp.setText(cam.get('source'))
                    statusConfig.setRtspConfig(cam.get('source'))
                    self.uiConfig.lblStatusProcurarCam.setText('Camera ativada')
                i = i + 1


            self.statusConfig.addListCamAtivasConfig(self.camRunTime.listCamAtivas)
            self.camRunTime.init() 


        else:
            self.uiConfig.lblStatusProcurarCam.setText('Sem câmeras ativas. Clique em "Procurar Câmeras" para uma nova varredura')

    def btnTestarConfigCam(self):

        #global listCamAtivas, listCamEncontradas, statusconfig
        log.debug('Testando configuracao de camera encontrada na rede')

        camConfigurada = None
        source = None
       
        if self.uiConfig.comboBoxCamEncontradas.currentIndex() != -1: 

            idCombo = self.uiConfig.comboBoxCamEncontradas.currentText().split(':')[0]
            idCombo = idCombo.replace('[','')
            idCombo = idCombo.replace(']','')
        
            i = 0 

            for cam in self.camRunTime.listCamEncontradas:

                if cam.get('id') == idCombo:
                    source = 'rtsp://' + self.uiConfig.txtUserCamDisponivel.text() + ':' + self.uiConfig.txtPasswdCamDisponivel.text() + '@' \
                                    + cam.get('ip') + ':' + self.uiConfig.txtPortaCamDisponivel.text() + '/' + self.uiConfig.txtCanalCamDiponivel.text()

                    camConfigurada = cam
                    break
                i = i + 1
            

            ipCam, error = utils.camSource(source)                   
            
            if error != '':                                                                    
                log.warning('Erro camSource: {}'.format(error))
                self.uiConfig.lblStatusTestarCam.setText('Configuração inválida, tente outro usuario, senha, porta ou canal')

            else:                                    
                log.info('Cam ativa encontrada')
                self.uiConfig.lblStatusTestarCam.setText('Câmera configurada corretamente. Pronto para uso')
                self.camRunTime.listCamEncontradas.pop(i)

                camConfigurada['user'] = self.uiConfig.txtUserCamDisponivel.text()
                camConfigurada['passwd'] = self.uiConfig.txtPasswdCamDisponivel.text()
                camConfigurada['channel'] = self.uiConfig.txtCanalCamDiponivel.text()
                camConfigurada['source'] = source 
                camConfigurada['emUso'] = 'False' 
                
                self.camRunTime.listCamAtivas.append(camConfigurada)

                statusConfig.addListCamAtivasConfig(self.camRunTime.listCamAtivas)
                statusConfig.addListCamEncontradasConfig(self.camRunTime.listCamEncontradas)
                
                self.camRunTime.init() 
                self.fillTabGeral()

    def btnProcurarCam(self):
        
        log.debug('Procurando cameras na rede')        

        self.clearListCameras() 
        
        self.camRunTime.listCamEncontradas.clear()
        self.camRunTime.listCamAtivas.clear()

        self.uiConfig.lblStatusProcurarCam.setText('Procurando cameras na rede... aguarde')

        self.camRunTime.listCamEncontradas, self.listCamAtivas = getListCam()

        for cam in self.listCamAtivas:
            self.uiConfig.comboBoxCamAtivas.addItem('[' + cam.get('id') + ']:' + cam.get('ip') + ' : ' + cam.get('port'))

        for cam2 in self.camRunTime.listCamEncontradas:
            self.uiConfig.comboBoxCamEncontradas.addItem('[' + cam2.get('id') + ']:' + cam2.get('ip') + ' : ' + cam2.get('port'))

        self.statusConfig.zerarListCamAtivasConfig() 
        self.statusConfig.zerarListCamEncontradasConfig()

        self.statusConfig.addListCamAtivasConfig(self.listCamAtivas)
        self.statusConfig.addListCamEncontradasConfig(self.camRunTime.listCamEncontradas)
        
        self.camRunTime.init() 
        self.fillTabGeral()

    def btnSaveStorage(self):

        global emailSentFullVideosAllTime, emailSentFullVideosOnAlarmes, emailSentDiskFull

        statusFields = True 
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Campo em branco")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        #checando campos em branco
        discoLivre = utils.getDiskUsageFreeGb()
        discoLivrePorcentagem = utils.getDiskUsageFree()

        if len(self.uiConfig.txtDefinirMaximoAllTime.text()) == 0 and not self.uiConfig.checkBoxNoLimitsVideosAllTime.isChecked():
            msg.setText("Favor preencher o campo 'Espaço máximo em GB na pasta Videos 24hs' ")
            msg.exec()
            self.uiConfig.txtDefinirMaximoAllTime.setFocus()
            statusFields = False


        if len(self.uiConfig.txtDefinirMaximoOnAlarmes.text()) == 0 and not self.uiConfig.checkBoxNoLimitsVideosOnAlarmes.isChecked():
            msg.setText("Favor preencher o campo 'Espaço máximo em GB na pasta Videos Alarmes' ")
            msg.exec()
            self.uiConfig.txtDefinirMaximoOnAlarmes.setFocus()
            statusFields = False


        if  not self.uiConfig.checkBoxNoLimitsVideosAllTime.isChecked() \
            and self.uiConfig.txtDefinirMaximoAllTime.text() != '0' \
            and len(self.uiConfig.txtDefinirMaximoAllTime.text()) != 0:

                if float(self.uiConfig.txtDefinirMaximoAllTime.text().replace(',', '.')) > discoLivre: 
                    msg.setText("Não há espaço em disco disponível, coloque um valor em GB menor que " + str(discoLivre) + ".")
                    msg.exec()
                    self.uiConfig.txtDefinirMaximoAllTime.setFocus()
                    statusFields = False


        if  not self.uiConfig.checkBoxNoLimitsVideosOnAlarmes.isChecked() \
            and len(self.uiConfig.txtDefinirMaximoOnAlarmes.text()) != 0 \
            and self.uiConfig.txtDefinirMaximoOnAlarmes.text() != '0':
            
                if float(self.uiConfig.txtDefinirMaximoOnAlarmes.text().replace(',', '.')) > discoLivre:
                    msg.setText("Não há espaço em disco disponível, coloque um valor em GB menor que " + str(discoLivre) + ".")
                    msg.exec()
                    self.uiConfig.txtDefinirMaximoOnAlarmes.setFocus()
                    statusFields = False


        log.info('txtAvisoUtilizacaoHD: {}'.format(self.uiConfig.txtAvisoUtilizacaoHD.text()))
        log.info('getDiskUsageFreeGb: {:f}'.format(utils.getDiskUsageFreeGb()))


        if len(self.uiConfig.txtAvisoUtilizacaoHD.text()) == 0:
            discoValor = discoLivrePorcentagem - 5 
            if discoValor <= 0:
                self.uiConfig.txtAvisoUtilizacaoHD.setText(str(discoLivrePorcentagem))
            else:
                self.uiConfig.txtAvisoUtilizacaoHD.setText(str(discoValor))

            msg.setText("Favor preencher o campo 'Nível mínimo de espaço em disco em porcentagem' ")
            msg.exec()
            self.uiConfig.txtAvisoUtilizacaoHD.setFocus()
            statusFields = False

        if self.uiConfig.txtAvisoUtilizacaoHD.text() != '0' and len(self.uiConfig.txtAvisoUtilizacaoHD.text()) != 0:

            if float(self.uiConfig.txtAvisoUtilizacaoHD.text().replace(',', '.')) < discoLivrePorcentagem:
                emailSentDiskFull = False 

        if self.uiConfig.txtDefinirMaximoOnAlarmes.text() != '0' and len(self.uiConfig.txtDefinirMaximoOnAlarmes.text()) != 0:

            if float(self.uiConfig.txtDefinirMaximoOnAlarmes.text().replace(',', '.')) < discoLivre:
                emailSentFullVideosOnAlarmes = False 

        if self.uiConfig.txtDefinirMaximoAllTime.text() != '0' and len(self.uiConfig.txtDefinirMaximoAllTime.text()) != 0:

            if float(self.uiConfig.txtDefinirMaximoAllTime.text().replace(',', '.')) < discoLivre:
                emailSentFullVideosAllTime = False 

        if statusFields:

            statusConfig.addStorageConfig(
                    diskMaxUsage, 
                    self.uiConfig.txtAvisoUtilizacaoHD.text().replace(',', '.'), 
                    self.uiConfig.txtDefinirMaximoOnAlarmes.text().replace(',', '.'),
                    self.uiConfig.txtDefinirMaximoAllTime.text().replace(',', '.'),
                    "True" if self.uiConfig.radioButtonDeleteOldestFiles.isChecked() else "False",
                    "True" if self.uiConfig.radioButtonStopSaveNewVideos.isChecked() else "False"
                    )
        
            refreshStatusConfig() 
            self.camRunTime.init() 

    def checkBoxDesabilitarLoginAutomatico(self, state):
        #global LOGIN_AUTOMATICO        
        
        if state == 0:
            
            log.info('Login automatico off')
            self.statusConfig.setLoginAutomatico('False')
            #LOGIN_AUTOMATICO = False


        elif (state == 1 or state == 2):
            
            log.info('Login automatico on')
            self.statusConfig.setLoginAutomatico('True')
            #LOGIN_AUTOMATICO = True    

    def checkBoxWebcamStateChanged(self, state):
        if state == 0:
           self.uiConfig.txtUrlRstp.setEnabled(True)
        # Qt.Checked 
        elif (state == 1 or state == 2):
            self.uiConfig.txtUrlRstp.clear()
            self.uiConfig.txtUrlRstp.setEnabled(False)

    def checkBoxNoLimitsVideosAllTime(self, state):
        if state == 0:
           self.uiConfig.txtDefinirMaximoAllTime.setEnabled(True)
        # Qt.Checked 
        elif (state == 1 or state == 2):
            self.uiConfig.txtDefinirMaximoAllTime.setText('0')
            self.uiConfig.txtDefinirMaximoAllTime.setEnabled(False)

    def checkBoxNoLimitsVideosOnAlarmes(self, state):
        if state == 0:
           self.uiConfig.txtDefinirMaximoOnAlarmes.setEnabled(True)
        # Qt.Checked 
        elif (state == 1 or state == 2):
            self.uiConfig.txtDefinirMaximoOnAlarmes.setText('0') #zero significa sem limites de utilizacao do disco
            self.uiConfig.txtDefinirMaximoOnAlarmes.setEnabled(False)    

    def btnNewAlarm(self):
        self.clearFieldsAlarm()
        self.uiConfig.btnSaveAlarm.setEnabled(True)
        self.uiConfig.btnDeleteAlarm.setEnabled(False)
        self.uiConfig.btnCancelAlarm.setEnabled(True)
        self.uiConfig.comboAlarms.setEnabled(False)

    def refreshStatusConfig(self):        
        self.statusConfig = utils.StatusConfig()
        regions = self.statusConfig.getRegions()
        self.emailConfig = self.statusConfig.getEmailConfig()

    def comboAlarmsUpdate(self, i):
        self.clearFieldsAlarm()

        #preenchendo lista de alarmes
        if not self.statusConfig.isAlarmEmpty(self.uiConfig.comboRegions.currentText()) and not self.statusConfig.isRegionsEmpty():

            self.uiConfig.btnDeleteAlarm.setEnabled(True)
            a = self.camRunTime.regions[self.uiConfig.comboRegions.currentIndex()].get('alarm')[i]
            self.uiConfig.checkMon.setCheckState(a.get('days').get('mon') == 'True')
            self.uiConfig.checkTue.setCheckState(a.get('days').get('tue') == 'True')
            self.uiConfig.checkWed.setCheckState(a.get('days').get('wed') == 'True')
            self.uiConfig.checkThur.setCheckState(a.get('days').get('thu') == 'True')
            self.uiConfig.checkFri.setCheckState(a.get('days').get('fri') == 'True')
            self.uiConfig.checkSat.setCheckState(a.get('days').get('sat') == 'True')
            self.uiConfig.checkSun.setCheckState(a.get('days').get('sun') == 'True')
            self.uiConfig.checkEmailAlert.setCheckState(a.get('isEmailAlert') == 'True')
            self.uiConfig.checkAlertSound.setCheckState(a.get('isSoundAlert') == 'True')
            self.uiConfig.txtNameAlarm.insert(a.get('name'))
            self.uiConfig.comboAlarms.setCurrentIndex(i)

            tStart = QTime(int(a.get('time').get('start').get('hour')), int(a.get('time').get('start').get('min')))
            self.uiConfig.timeStart.setTime(tStart)

            tEnd = QTime(int(a.get('time').get('end').get('hour')),int(a.get('time').get('end').get('min')))
            self.uiConfig.timeEnd.setTime(tEnd)

        else:
           self.uiConfig.btnDeleteAlarm.setEnabled(False)

    def comboRegionsUpdate(self, i):        

        self.clearFieldsTabRegiao()
        #r = regions[i]

        self.uiConfig.comboAlarms.clear()

        if not self.statusConfig.isRegionsEmpty():
            for r in self.camRunTime.regions:
                self.uiConfig.comboRegions.addItem(r.get("nameRegion"))

            r = self.camRunTime.regions[i]
            self.uiConfig.txtRegionName.insert(r.get('nameRegion'))
            self.uiConfig.txtThreshold.insert(str(r.get('prob_threshold')))            
            self.uiConfig.checkPerson.setCheckState(r.get('objectType').get('person')=="True")
            self.uiConfig.checkCar.setCheckState(r.get('objectType').get('car')=="True")
            self.uiConfig.checkBike.setCheckState(r.get('objectType').get('bike')=="True")
            self.uiConfig.checkDog.setCheckState(r.get('objectType').get('dog')=="True")

            if not self.statusConfig.isAlarmEmpty(i):
                #preenchendo lista de alarmes
                if not self.statusConfig.isAlarmEmpty(i):
                    for a in self.camRunTime.regions[i].get('alarm'):
                        self.uiConfig.comboAlarms.addItem(a.get('name'))                
                
            self.uiConfig.comboRegions.setCurrentIndex(i)
            self.comboAlarmsUpdate(0)
            self.uiConfig.btnDeleteRegion.setEnabled(True)
            self.uiConfig.btnCancelRegion.setEnabled(False)

    def clearFieldsAlarm(self):
        self.uiConfig.checkMon.setCheckState(False)
        self.uiConfig.checkTue.setCheckState(False)
        self.uiConfig.checkWed.setCheckState(False)
        self.uiConfig.checkThur.setCheckState(False)
        self.uiConfig.checkFri.setCheckState(False)
        self.uiConfig.checkSat.setCheckState(False)
        self.uiConfig.checkSun.setCheckState(False)
        self.uiConfig.checkEmailAlert.setCheckState(False)
        self.uiConfig.checkAlertSound.setCheckState(False)
        self.uiConfig.timeStart.clear()
        self.uiConfig.timeEnd.clear()
        self.uiConfig.txtNameAlarm.clear()

    def clearFieldsTabRegiao(self):
        self.uiConfig.txtRegionName.clear()
        self.uiConfig.txtNameAlarm.clear()
        self.uiConfig.txtThreshold.clear()
        self.uiConfig.comboAlarms.clear()
        self.uiConfig.comboRegions.clear()        
        self.uiConfig.checkPerson.setCheckState(False)
        self.uiConfig.checkBike.setCheckState(False)
        self.uiConfig.checkCar.setCheckState(False)
        self.uiConfig.checkDog.setCheckState(False)
        self.uiConfig.checkMon.setCheckState(False)
        self.uiConfig.checkTue.setCheckState(False)
        self.uiConfig.checkWed.setCheckState(False)
        self.uiConfig.checkThur.setCheckState(False)
        self.uiConfig.checkFri.setCheckState(False)
        self.uiConfig.checkSat.setCheckState(False)
        self.uiConfig.checkSun.setCheckState(False)
        self.uiConfig.timeEnd.clear()
        self.uiConfig.timeStart.clear()

    def fillTabGeral(self):
        

        self.uiConfig.txtEmailName.clear()
        self.uiConfig.txtEmailPort.clear()
        self.uiConfig.txtEmailSmtp.clear()
        self.uiConfig.txtEmailSubject.clear()
        self.uiConfig.txtEmailTo.clear()
        self.uiConfig.txtEmailUser.clear()
        self.uiConfig.txtEmailPassword.clear()
        self.uiConfig.lblStatus.clear()
        self.uiConfig.lblStatusProcurarCam.clear()
        
        self.uiConfig.comboBoxCamAtivas.clear()
        self.uiConfig.comboBoxCamEncontradas.clear()
        
        self.uiConfig.txtUserCamDisponivel.clear()
        self.uiConfig.txtPasswdCamDisponivel.clear()
        self.uiConfig.txtPortaCamDisponivel.clear()
        self.uiConfig.txtCanalCamDiponivel.clear()
        self.uiConfig.lblStatusTestarCam.clear()

        self.refreshStatusConfig()

        self.uiConfig.checkBoxDesabilitarLoginAutomatico.setCheckState( True if self.statusConfig.getLoginAutomatico() == "True" else False )


        self.uiConfig.checkBoxVideoRecordingOnAlarmes.setCheckState( True if self.statusConfig.data.get("isRecordingOnAlarmes") == "True" else False )

        self.uiConfig.checkBoxVideoRecordingAllTime.setCheckState( True if self.statusConfig.data.get("isRecordingAllTime") == "True" else False )

        if self.statusConfig.data.get("camSource") == "webcam":
            self.uiConfig.txtUrlRstp.clear()
        else:
            self.uiConfig.txtUrlRstp.setText(self.statusConfig.data.get("camSource"))

        self.uiConfig.txtDirRecordingAllTime.setText(self.statusConfig.data.get("dirVideosAllTime"))
        self.uiConfig.txtDirRecordingOnAlarmes.setText(self.statusConfig.data.get("dirVideosOnAlarmes"))
        self.uiConfig.txtAvisoUtilizacaoHD.setText(self.statusConfig.data["storageConfig"].get("diskMinUsage"))
        self.uiConfig.txtEmailName.setText(self.statusConfig.data["emailConfig"].get('name'))
        self.uiConfig.txtEmailPort.setText(self.statusConfig.data["emailConfig"].get('port'))
        self.uiConfig.txtEmailSmtp.setText(self.statusConfig.data["emailConfig"].get('smtp'))
        self.uiConfig.txtEmailUser.setText(self.statusConfig.data["emailConfig"].get('user'))

        passwdEmail = utils.decrypt(self.statusConfig.data["emailConfig"].get('password')) 

        self.uiConfig.txtEmailPassword.setText(passwdEmail)
        
        if passwdEmail == 'error':
            self.uiConfig.lblStatus.setText('Cheque se sua senha do email está cadastrada corretamente')
            self.uiConfig.txtEmailPassword.setFocus()
        
        self.uiConfig.txtEmailSubject.setText(self.statusConfig.data["emailConfig"].get('subject'))
        self.uiConfig.txtEmailTo.setText(self.statusConfig.data["emailConfig"].get('to'))

        #carregar cams previamente escaneadas na rede

        for cam in self.camRunTime.listCamAtivas:
            if cam.get('emUso') == 'True':
                self.uiConfig.comboBoxCamAtivas.addItem('[' + cam.get('id') + ']:' + cam.get('ip') + ' : ' + cam.get('port') + ' [em uso]')
            else:
                self.uiConfig.comboBoxCamAtivas.addItem('[' + cam.get('id') + ']:' + cam.get('ip') + ' : ' + cam.get('port'))

        for cam in self.camRunTime.listCamEncontradas:
            self.uiConfig.comboBoxCamEncontradas.addItem('[' + cam.get('id') + ']:' + cam.get('ip') + ' : ' + cam.get('port'))
        
        
        #configuracoes de armazenamento
        if self.camRunTime.spaceMaxDirVideosAllTime == 0:
            
            self.uiConfig.txtDefinirMaximoAllTime.setText('0')
            self.uiConfig.txtDefinirMaximoAllTime.setEnabled(False)
            self.uiConfig.checkBoxNoLimitsVideosAllTime.setChecked(True)

        else: 
            self.uiConfig.txtDefinirMaximoAllTime.setText(str(self.camRunTime.spaceMaxDirVideosAllTime))
            self.uiConfig.txtDefinirMaximoAllTime.setEnabled(True)
        
        if self.camRunTime.spaceMaxDirVideosOnAlarme == 0: 

            self.uiConfig.txtDefinirMaximoOnAlarmes.setText('0')
            self.uiConfig.txtDefinirMaximoOnAlarmes.setEnabled(False)
            self.uiConfig.checkBoxNoLimitsVideosOnAlarmes.setChecked(True)
        else:
            self.uiConfig.txtDefinirMaximoOnAlarmes.setEnabled(True)
            self.uiConfig.txtDefinirMaximoOnAlarmes.setText(str(self.camRunTime.spaceMaxDirVideosOnAlarme))
            self.uiConfig.checkBoxNoLimitsVideosOnAlarmes.setChecked(False)
        
        
        self.uiConfig.radioButtonStopSaveNewVideos.setChecked(self.camRunTime.stopSaveNewVideos)
        self.uiConfig.radioButtonDeleteOldestFiles.setChecked(self.camRunTime.eraseOldestFiles)
        self.uiConfig.progressBarDisponivelHD.setValue(utils.getDiskUsageFree())
        self.uiConfig.txtAvailableHD.setText('{:03.2f}'.format((utils.getDiskUsageFreeGb())))
        self.uiConfig.txtDirUsedVideosAllTime.setText('{:03.2f}'.format(utils.getDirUsedSpace(self.statusConfig.data["dirVideosAllTime"])))
        self.uiConfig.txtDirUsedVideosOnAlarmes.setText('{:03.2f}'.format(utils.getDirUsedSpace(self.statusConfig.data["dirVideosOnAlarmes"])))

        self.uiConfig.txtDiasEstimado.setText('{:d}'.format((utils.getNumDaysRecording())) + ' dias' )        

    def loginAutomatico(self):

            #global init_video, statusLicence, uiLogin, conexao, login 

            log.debug('Checando conexão com a Internet')
            #uiLogin.lblStatus.setText("Checando conexão com a Internet")

            self.camRunTime.conexao = utils.checkInternetAccess()
            #conexao = True

            if self.camRunTime.conexao:    
            
                log.debug('Checando licença no servidor - Por favor aguarde')
                
                email = self.statusConfig.dataLogin['user']
                passwd = utils.decrypt(self.statusConfig.dataLogin['passwd'])
                
                self.camRunTime.login = {'user':utils.encrypt(email), 'passwd':utils.encrypt(passwd), 'token':utils.encrypt(self.token)}
                
                self.camRunTime.statusLicence, self.camRunTime.error  = checkLoginPv(self.camRunTime.login) 
                #statusLicence = True ## testando apenas IJF
                
                if self.camRunTime.statusLicence:
                    
                    log.debug("Usuario logado")
                    self.camRunTime.init_video = True 
                    #windowLogin.close()
                
                else:

                    #se o servidor estiver fora do ar - libera acesso ao sistema 
                    if self.camRunTime.error == "conexao":
                        log.warning("Erro de conexão com o servidor")

                        self.camRunTime.init_video = True
                        self.camRunTime.statusLicence = True
                        log.warning("Liberando acesso")
                        #windowLogin.close()

                    elif self.camRunTime.error == "login":

                        self.camRunTime.init_video = False
                        log.warning("Usuario invalido")
                        #uiLogin.lblStatus.setText("Usuário ou senha inválida. Tente novamente")

            else:

                log.info("Erro de conexao com a Internet")
                #uiLogin.lblStatus.setText("Cheque sua conexão com a Internet por favor e tente mais tarde")



if __name__=="__main__":

    app = QApplication(sys.argv)          

    
    #print('main isLogged true')

    uiConfig = FormProc()
    #formInitConfig = App()
    #uiConfig.__init__(formInitConfig)
    #uiConfig.setupUi(formInitConfig)
    uiConfig.show()
    #formInitConfig.show()        
 
    sys.exit(app.exec_())