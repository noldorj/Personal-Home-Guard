from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QMainWindow, QErrorMessage, QMessageBox, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTime, QThread
from PyQt5.QtWidgets import QWidget

#from initFormConfig import FormProc
from mainForm import *
from formLogin import *
from formTermos import *
from initGuiLogin import *
from initGuiTermo import *
from objectTracking.pyimagesearch.centroidtracker import CentroidTracker
from camRunTime import *
from utilsCore import StatusConfig
from inferenceCore import *
from Utils_tracking import sendMailAlert
from Utils_tracking import sendMail
from Utils_tracking import saveImageBox
from checkStorage import CheckStorage
from rtsp_discover.rtsp_discover import CamFinder

import time
import numpy as np
import cv2 as cv
import sys
import time
import logging as log
import getpass

import firebase_admin
from firebase_admin import credentials

firebase_app_pv = None

from collections import deque

token = secrets.token_urlsafe(20)

loginStatus = False

cloudEnable = True


log.root.setLevel(log.INFO)
log.basicConfig()

for handler in log.root.handlers[:]:
    log.root.removeHandler(handler)

#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.DEBUG, stream=sys.stdout)
log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, handlers=[log.FileHandler('config/pv.log', 'w', 'utf-8')])
log.getLogger('socketio').setLevel(log.ERROR)
log.getLogger('engineio').setLevel(log.ERROR)

#print('camRunTime ID Global: {}'.format(camRunTimeGlobal.camRunTimeId))



@QtCore.pyqtSlot(bool)
def updateStatusLogin(status):
    global loginStatus, statusConfig, camRunTime
    loginStatus = status
    #print('updateStatusLogin status: {}'.format(loginStatus))



class MouseTracker(QtCore.QObject):
    positionChanged = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)

    @property
    def widget(self):
        return self._widget

    def eventFilter(self, o, e):
        #print('eventFilter')
        if o is self.widget and e.type() == QtCore.QEvent.MouseButtonRelease:
            self.positionChanged.emit(e.pos())
        
        return super().eventFilter(o, e)



class FormProc(QWidget):
       
    statusConfig = StatusConfig()
    
    camRunTime = CamRunTime()

    infCam = InferenceCore()
    
        

    def __init__(self, parent=None):
        super(FormProc, self).__init__(parent)
        self._run_flag = True
        self.uiConfig = Ui_formConfig()
        self.uiConfig.setupUi(self)
        
        #print('else iniciando formConfig')
        
        self.camRunTime.token = token 
        print('initFormConfig __init__')
        self.statusConfig = utils.StatusConfig()
        
        self.statusConfig.readConfigLogin()
        
        self.statusConfig.setFirebaseApp(firebase_app_pv)
        
        if self.statusConfig.getPrimeiroUso() == 'True':        
            windowTermo = FormTermo()                                    
            windowTermo.exec_()
            
            self.statusConfig = utils.StatusConfig()
                        
            if self.statusConfig.getPrimeiroUso() == 'True':
                self._run_flag = False 
                sys.exit()            
        
        
        
        
        if self.statusConfig.getLoginAutomatico() == 'True':
            log.info('Iniciando login automatico')            
            self.loginAutomatico()
            
            
        else:
        
            ## CHAMANDO TELA DE LOGIN ## 
            
            windowLogin = FormLogin(self.camRunTime, self.statusConfig)                        
            windowLogin.updateStatusLogin.connect(updateStatusLogin)               
            windowLogin.exec_()

        #implementar logica de checar licença TO-DO
        
        log.info(' ')
        log.info('initFormConfig:: statusLicence: ' + str(self.camRunTime.statusLicence))
        log.info('initFormConfig:: errorRtsp: ' + str(self.camRunTime.errorRtsp))
        log.info('initFormConfig:: loginStatus: ' + str(loginStatus))        
        log.info(' ')
        
        #if self.camRunTime.statusLicence and not self.camRunTime.errorRtsp: 
        if not loginStatus:
            log.info('initFormConfig loginStatus saindo...')
            utils.stopWatchDog() 
            self._run_flag = False 
            sys.exit()            
            
        else: 
            
            self.camRunTime.init()
            self.infCam.setCamRunTime(self.camRunTime)
            self.checkStorage()
            
            self.statusConfig.setDateSessionInit()
            
            #slots            
            tracker = MouseTracker(self.uiConfig.lblCam1)
            tracker.positionChanged.connect(self.on_positionChanged)       
                       
            
            
            self.uiConfig.btnSaveEmail.clicked.connect(self.btnSaveEmail)
            self.uiConfig.btnSaveConfigGravacao.clicked.connect(self.btnSaveConfigGravacao)            
            #self.uiConfig.btnNovaCamRemota.clicked.connect(self.btnNovaCamRemota)
            
            
            self.uiConfig.btnRodarNuvem.clicked.connect(self.btnRodarNuvem)
            
            self.uiConfig.btnSaveStorage.clicked.connect(self.btnSaveStorage)
            

            self.uiConfig.btnAtivarCam.clicked.connect(self.btnAtivarCam)
            self.uiConfig.btnProcurarCam.clicked.connect(self.btnProcurarCam)
            self.uiConfig.btnTestarConfigCam.clicked.connect(self.btnTestarConfigCam)

            self.uiConfig.checkBoxWebCam.stateChanged.connect(self.checkBoxWebcamStateChanged)
            
            self.uiConfig.checkBoxDesabilitarLoginAutomatico.stateChanged.connect(self.checkBoxDesabilitarLoginAutomatico)
            self.uiConfig.checkTodosDias.stateChanged.connect(self.checkBoxTodosDiasStateChanged)
           
            self.uiConfig.checkBoxNoLimitsVideosAllTime.stateChanged.connect(self.checkBoxNoLimitsVideosAllTime)
            self.uiConfig.checkBoxNoLimitsVideosOnAlarmes.stateChanged.connect(self.checkBoxNoLimitsVideosOnAlarmes)
            self.uiConfig.checkBoxDesativarAlarmes.stateChanged.connect(self.checkBoxDesativarAlarmes)

            self.uiConfig.comboRegions.activated['int'].connect(self.comboRegionsUpdate)
            self.uiConfig.comboAlarms.activated['int'].connect(self.comboAlarmsUpdate)
            self.uiConfig.comboBoxCamAtivas.activated['int'].connect(self.comboBoxCamAtivasStateChanged)

            self.uiConfig.comboBoxCamEncontradas.activated['int'].connect(self.comboBoxCamEncontradasStateChanged)
            self.uiConfig.btnSaveAlarm.clicked.connect(self.btnSaveAlarm)
            self.uiConfig.btnSaveRegion.clicked.connect(self.btnSaveRegion)
            self.uiConfig.btnDeleteAlarm.clicked.connect(self.btnDeleteAlarm)
            self.uiConfig.btnDeleteRegion.clicked.connect(self.btnDeleteRegion)
            self.uiConfig.btnCancelAlarm.clicked.connect(self.btnCancelAlarm)
            self.uiConfig.btnCancelRegion.clicked.connect(self.btnCancelRegion)
            self.uiConfig.btnNewRegion.clicked.connect(self.btnNewRegion)
            self.uiConfig.btnInitAddRegiao.clicked.connect(self.btnNewRegion)
            self.uiConfig.btnNewAlarm.clicked.connect(self.btnNewAlarm)
            #self.uiConfig.btnInitSair.clicked.connect(self.closeEvent)
            self.uiConfig.btnAlterarNomeCamAtiva.clicked.connect(self.btnSalvarNomeCamAtiva)
            self.uiConfig.btnRemoverCamAtiva.clicked.connect(self.btnRemoverCamAtiva)
            self.uiConfig.btnRemoverCamEncontrada.clicked.connect(self.btnRemoverCamEncontrada)
            self.uiConfig.btnNovaCam.clicked.connect(self.btnNovaCam)
            
            self.uiConfig.progressBarProcurarCam.hide()
            
            self.uiConfig.lblCam1.setMinimumSize(self.camRunTime.RES_X, self.camRunTime.RES_Y) 
            self.uiConfig.lblCam1.resize(self.camRunTime.RES_X, self.camRunTime.RES_Y) 

            
            
            # ----------- init tab configuração geral --------------- 
            self.uiConfig.btnSaveEmail.setEnabled(True)
            self.fillTabGeral()

            # ----------- init tab adicionar regioes --------------- 
            if not self.statusConfig.isRegionsEmpty():
                self.uiConfig.btnDeleteRegion.setEnabled(True)
                self.uiConfig.btnDeleteAlarm.setEnabled(True)

                for r in self.camRunTime.regions:
                    self.uiConfig.comboRegions.addItem(r.get("nameRegion"))
                self.comboRegionsUpdate(0)
                self.comboAlarmsUpdate(0)
            else:
                self.uiConfig.btnDeleteRegion.setEnabled(False)
                self.uiConfig.btnDeleteAlarm.setEnabled(False)

            self.uiConfig.btnSaveAlarm.setEnabled(True)
            self.uiConfig.btnCancelRegion.setEnabled(False)
            self.uiConfig.btnCancelAlarm.setEnabled(False)    
            self.uiConfig.btnNewAlarm.setEnabled(True)
            self.uiConfig.comboAlarms.setEnabled(True)

            self.uiConfig.lblInitUsername.setText(self.statusConfig.dataLogin['user'])
            self.uiConfig.lblInitStatus.setText('Executando')

            
            if (not self.camRunTime.errorRtsp) and (not self.camRunTime.errorWebcam): 

                log.info('initFormConfig:: init Thread OpenCV')        
                ### Thread OpenCV
                self.infCam.setCamRunTime(self.camRunTime)
                self.uiConfig.thread = self.infCam
                # connect its signal to the update_image slot
                self.uiConfig.thread.change_pixmap_signal.connect(self.update_image)
                self.uiConfig.thread.warningSessionLoss.connect(self.warningSessionLoss)
                self.uiConfig.thread.warningSessionLossFirst.connect(self.warningSessionLossFirst)
                self.uiConfig.thread.webCamWarning.connect(self.webCamWarning)
                self.uiConfig.thread.camEmptyWarning.connect(self.camEmptyWarning)
                #self.uiConfig.thread.change_pixmap_signal.connect(self.checkStorage)
                #self.uiConfig.thread.storageFull.connect(self.storageFull)
                
                # start the thread
                self.uiConfig.thread.start()
                
                ## Thread CheckStorage
                self.threadStorage = QtCore.QThread()
                self.threadStorage = CheckStorage(self.camRunTime)
                self.threadStorage.updateStorageInfo.connect(self.checkStorage)
                self.threadStorage.warningHDCheio.connect(self.warningHDCheio)
                self.threadStorage.start()
                                                            
                #utils.initWatchDog()                

            else: 
                
                #log.info('::initFormConfig erroRtsp')
                
                if self.camRunTime.errorWebcam:
                    log.info('initFormConfig:: Erro ao conectar Webcam')
                    self.uiConfig.lblCam1.setText('Webcam com erro de conexão ! Cheque seu computador por favor ! ')              
                    self.uiConfig.lblInitStatus.setText('Webcam com erro de conexão ! Por favor, cheque a configuração da Webcam e reinicie o Portão Virtual ! ')              
                
                elif self.camRunTime.camEmpty:
                    log.info('initFormConfig:: Camera não configurada')
                    self.uiConfig.lblCam1.setText('Configura sua câmera ou webcam para iniciar o Portão Virtual !')              
                    self.uiConfig.lblInitStatus.setText('Configura sua câmera ou webcam para iniciar o Portão Virtual !')              
                
                elif self.camRunTime.errorRtsp:                    
                    
                    log.info('initFormConfig:: Erro ao conectar a câmera')
                    self.uiConfig.lblCam1.setText('Câmera com erro de conexão. O sistema está checando se a câmera mudou de IP')              
                    self.uiConfig.lblInitStatus.setText('Câmera com erro de conexão. O sistema está checando se a câmera mudou de IP')              

                    self.threadRtspStatus = QThread()
                    self.threadRtspStatus = CamFinder(True)
                    self.threadRtspStatus.updateProgress.connect(self.updateProcurarCam)            
                    self.threadRtspStatus.start()        


    def run(self):              
        log.info('run')
        #self.statusConfig = statusConfig        
        #windowConfig.show()
    
    @QtCore.pyqtSlot()
    def camEmptyWarning(self):
        self.uiConfig.lblCam1.setText('Configura sua câmera ou webcam para iniciar o Portão Virtual !')
        self.uiConfig.lblInitStatus.setText('Configura sua câmera ou webcam para iniciar o Portão Virtual !')
    
    @QtCore.pyqtSlot()
    def warningHDCheio(self):
        log.info('warningHDCheio::')
        self.uiConfig.lblCam1.setText('Seu HD está cheio ! Libere mais espaço antes de configurar e começar a utilizar o Portão Virtual!')
        self.uiConfig.lblInitStatus.setText('Seu HD está cheio ! Libere mais espaço antes de configurar e começar a utilizar o Portão Virtual!')
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("HD sem espaço !")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setText("Seu HD está cheio ! Libere mais espaço antes de configurar e começar a utilizar o Portão Virtual!")
        msg.exec()
    
    
    @QtCore.pyqtSlot()
    def webCamWarning(self):
        self.uiConfig.lblCam1.setText('Por favor, cheque a configuração da sua Webcam e reinicie o Portão Virtual')
        self.uiConfig.lblInitStatus.setText('Por favor, cheque a configuração da sua Webcam e reinicie o Portão Virtual')
    
    @QtCore.pyqtSlot(QtCore.QPoint)
    def on_positionChanged(self, pos):
        delta = QtCore.QPoint(30, -15)                
        if self.camRunTime.cropPolygon == True:
            self.infCam.setPointSelection(pos.x(), pos.y())
            
            
    
    @pyqtSlot(StatusConfig, CamRunTime)
    def updateStatusConfigCamRunTime(self, statusConfig, camRunTime):
        #print('updateStatusConfigRunTime')
        self.statusConfig = statusConfig
        self.camRunTime = camRunTime
        


    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):        
        qt_img = self.convert_cv_qt(cv_img)
        self.uiConfig.lblCam1.setPixmap(qt_img)
    
    #def mouseMoveEvent(self, event):
    #    print('Mouse coords: ( %d : %d )' % (event.x(), event.y()))
    
    '''Reload the mouse click event (click) '''
    # def mousePressEvent(self, event):
    
        # if self.camRunTime.cropPolygon == True:
            # if event.buttons () == QtCore.Qt.LeftButton: # left button pressed
                # self.infCam.setPointSelection(event.x(), event.y())
                # #self.setText ("Click the left mouse button for the event: define it yourself")
                # #Print("Click the left mouse button") # response test statement
    
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.camRunTime.RES_X, self.camRunTime.RES_Y, Qt.IgnoreAspectRatio)
        #p = convert_to_Qt_format.scaled(self.uiConfig.lblCam1.frameGeometry().width(), self.uiConfig.lblCam1.frameGeometry().height(), Qt.IgnoreAspectRatio)
        
        return QPixmap.fromImage(p)

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        #self.wait()           

    def closeEvent(self, event):                
        log.info('closeEvent')
        utils.stopWatchDog()
        self._run_flag = False                       
        
    
   #---------------- gui -------------------
    def callbackButton1min(self, ret):   
        self.camRunTime.tSoundLimit = tSoundLimit + 60
        Self.camRunTime.tSoundStart = time.time()

    def callbackButton30min(self, ret):
        #global tSoundLimit, tSoundStart
        self.camRunTime.tSoundLimit = tSoundLimit + 1800
        self.camRunTime.tSoundStart = time.time()

    def callbackButtonResumeSound(self, ret):    
        self.camRunTime.tSoundLimit = 0
        self.camRunTime.tSoundStart = 0
        self.camRunTime.tSoundEnd = 0
        self.camRunTime.tSound = 0
        self.camRunTime.stopSound = False

    # def btnInitSair(self):                 
        # self._run_flag = False   
        # sys.exit()
    
    def btnDeleteAlarm(self):
        
        log.info('btnDeleteAlarm:: i: {}'.format(self.uiConfig.comboRegions.currentIndex()))
        
        if self.uiConfig.comboRegions.currentIndex() is not -1:
        
            if len(self.camRunTime.regions[self.uiConfig.comboRegions.currentIndex()].get('alarm')) <= 1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Região sem alarmes !")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg.setText("Toda região precisa ter pelo menos um alarme associado ! Não será possível deletar este alarme")
                msg.exec()
                
            else:    
                self.statusConfig.deleteAlarm(self.uiConfig.comboRegions.currentText(), self.uiConfig.comboAlarms.currentText())
                self.refreshStatusConfig()
                self.fillTabGeral()
                self.comboRegionsUpdate(self.uiConfig.comboRegions.currentIndex())
                #self.comboAlarmsUpdate(0)
        

    def btnDeleteRegion(self):
        log.info('btnDeleteRegion:: pressed')
        self.statusConfig.deleteRegion(self.uiConfig.comboRegions.currentText())        
        self.camRunTime.regions = self.statusConfig.getRegions()
        self.refreshStatusConfig()
        self.comboRegionsUpdate(0)
        self.comboAlarmsUpdate(0)
        
    def btnRodarNuvem(self):
    
        print('btnRodarNuvem::')
        
        camRemota = self.statusConfig.getCamEmUsoConfig()
        #testando IP Cam Remota
        
        ipCam, error = utils.camSource(camRemota)
        
        msg = QMessageBox()        
        
        if error == 'rtsp':
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Câmera remota com problema!")
            msg.setStandardButtons(QMessageBox.Ok)
            text = "Cheque se a porta" + camRemota["port"] + 'do seu roteador está liberada!'
            msg.setText(text)
            msg.exec()
            text = 'RTSP: ' + camRemota.source
            self.uiConfig.lblStatusCamRemota.setText(text)
            
        else:
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Rodando na Nuvem")
            msg.setStandardButtons(QMessageBox.Ok)        
            msg.setText("Portão Virtual rodando na Nuvem! Pode fechar este programa normalmente e desligar seu PC!")
            msg.exec()       
            self.statusConfig.setNuvemConfig("True")
            self.camRunTime.init()
            self.refreshStatusConfig()
            
            #desabilitar processamento local
        
        
    
    def btnNovaCamRemota(self):
    
        log.info('btnNovaCamRemota::')
        
        #pegar configuração da camera atual e colocar IP e preencher formulario
        
        camRemota = self.statusConfig.getCamEmUsoConfig()
        if self.camRunTime.ipExterno != '':
            camRemota["ip"] = self.camRunTime.ipExterno
        
        #initprint('ipExterno: {}'.format(self.camRunTime.ipExterno))
        
        #testando IP Externo 
        
        ipCam, error = utils.camSource(camRemota)
        
        msg = QMessageBox()        
        
        if error == 'rtsp':
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Câmera remota com problema!")
            msg.setStandardButtons(QMessageBox.Ok)
            text = "Cheque se a porta" + camRemota["port"] + 'do seu roteador está liberada!'
            msg.setText(text)
            msg.exec()
            text = 'RTSP: ' + camRemota.source
            self.uiConfig.lblStatusCamRemota.setText(text)
            
        else:
            
            #novo id 
            idMaior = 0
            for cam in self.camRunTime.listCamAtivas:
                if int(cam.get('id')) > idMaior:
                    idMaior = int(cam.get('id'))
                    
            for cam in self.camRunTime.listCamEncontradas:
                if int(cam.get('id')) > idMaior:
                    idMaior = int(cam.get('id'))
            
            idMaior = idMaior + 1
            
            nome = camRemota["nome"] + '_REMOTA'
            camRemota["nome"] = nome
            camRemota["emUso"] = "False"
            
            self.camRunTime.listCamAtivas.append(camRemota)
            self.camRunTime.statusConfig.addListCamAtivasConfig(self.camRunTime.listCamAtivas)
            self.fillTabGeral()
            
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Câmera remota funcionando!")
            msg.setStandardButtons(QMessageBox.Ok)        
            msg.setText("Câmera remota funcionando corretamente! - Ative ela caso queira rodar o PV na Nuvem")
            msg.exec()       
            
        
        #endCamRemota = self.uiConfig.txtUrlRstp.text()
    
    def btnSaveConfigGravacao(self):
        log.info('btnSaveConfigGravacao::')
        #global self.uiConfig

        statusFields = True 
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Campo em branco")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        #checando campos em branco
        if self.uiConfig.checkBoxVideoRecordingAllTime.isChecked() and len(self.uiConfig.txtDirRecordingAllTime.text()) ==  0:
            msg.setText("Campo 'Diretório de gravação 24h' em branco")
            msg.exec()
            self.uiConfig.txtDirRecordingAllTime.setFocus()
            statusFields = False

        elif self.uiConfig.checkBoxVideoRecordingOnAlarmes.isChecked() and len(self.uiConfig.txtDirRecordingOnAlarmes.text()) ==  0:
            msg.setText("Campo 'Diretório de gravação de Alarmes' em branco")
            msg.exec()
            self.uiConfig.txtDirRecordingOnAlarmes.setFocus()
            statusFields = False

        elif self.uiConfig.checkBoxWebCam.isChecked() and len(self.uiConfig.txtUrlRstp.text()) > 0:
            msg.setText("Escolha somente 'Capturar da Webcam' ou 'Câmera RSTP'")
            msg.exec()
            self.uiConfig.txtUrlRstp.setFocus()
            self.camRunTime.statusFields = False
            
        if statusFields:
            self.camRunTime.camSource = "webcam" if self.uiConfig.checkBoxWebCam.isChecked() else self.uiConfig.txtUrlRstp.text()
            self.camRunTime.isRecordingAllTime = "True" if self.uiConfig.checkBoxVideoRecordingAllTime.isChecked() else "False"
            self.camRunTime.isRecordingOnAlarmes = "True" if self.uiConfig.checkBoxVideoRecordingOnAlarmes.isChecked() else "False"
            
            
            self.statusConfig.setConfigGravacao(self.camRunTime.isRecordingAllTime,
                                  self.camRunTime.isRecordingOnAlarmes,
                                  self.uiConfig.txtDirRecordingAllTime.text(),
                                  self.uiConfig.txtDirRecordingOnAlarmes.text(),
                                  self.camRunTime.camSource,
                                  self.uiConfig.txtAvisoUtilizacaoHD.text())
            
            
            self.camRunTime.init()
            
            self.uiConfig.progressBarDisponivelHD.setValue(utils.getDiskUsageFree())
            self.uiConfig.txtAvailableHD.setText('{:03.2f}'.format((utils.getDiskUsageFreeGb())))
            self.uiConfig.txtDirUsedVideosAllTime.setText('{:03.2f}'.format(utils.getDirUsedSpace(self.statusConfig.data["dirVideosAllTime"])))
            self.uiConfig.txtDirUsedVideosOnAlarmes.setText('{:03.2f}'.format(utils.getDirUsedSpace(self.statusConfig.data["dirVideosOnAlarmes"])))

            self.uiConfig.txtDiasEstimado.setText('{:d}'.format((utils.getNumDaysRecording())) + ' dias' )        
            
            



    # Tab de Configurações - TODO mudar nome depois
    def btnSaveEmail(self):
    
        log.info('btnSaveEmail::')
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
            self.uiConfig.txtEmailName.setFocus()
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
            
        elif self.camRunTime.camEmpty:
            log.info('initFormConfig::btnSaveEmail Aviso efetuado de configuracao da camera primeiro antes de teste de Email')
            self.uiConfig.lblStatus.setText('Para efetuar o teste de email, você precisa ter uma câmera configurada corretamente')
            msg.setText("Configure sua câmera primeiro !")
            msg.exec()                
            statusFields = False

        if statusFields:
            self.camRunTime.camSource = "webcam" if self.uiConfig.checkBoxWebCam.isChecked() else self.uiConfig.txtUrlRstp.text()
            self.camRunTime.isRecordingAllTime = "True" if self.uiConfig.checkBoxVideoRecordingAllTime.isChecked() else "False"
            self.camRunTime.isRecordingOnAlarmes = "True" if self.uiConfig.checkBoxVideoRecordingOnAlarmes.isChecked() else "False"

             
            passwd = utils.encrypt(self.uiConfig.txtEmailPassword.text())
            
            self.statusConfig.addConfigGeral(self.uiConfig.txtEmailName.text(),
                                  self.uiConfig.comboBoxServidorEmail.currentText(),
                                  self.uiConfig.txtEmailUser.text(),
                                  passwd,
                                  self.uiConfig.txtEmailSubject.text(),
                                  self.uiConfig.txtEmailTo.text(),
                                  self.camRunTime.isRecordingAllTime,
                                  self.camRunTime.isRecordingOnAlarmes,
                                  self.uiConfig.txtDirRecordingAllTime.text(),
                                  self.uiConfig.txtDirRecordingOnAlarmes.text(),
                                  self.camRunTime.camSource, 
                                  self.uiConfig.txtAvisoUtilizacaoHD.text())
            
            log.info('initFormConfig:: servidorEmail: {}'.format(self.uiConfig.comboBoxServidorEmail.currentText()))            
            
            if sendMailAlert(self.uiConfig.txtEmailName.text(), \
                    self.uiConfig.txtEmailTo.text(), \
                    self.uiConfig.txtEmailSubject.text(), \
                    self.uiConfig.comboBoxServidorEmail.currentText(), \
                    self.uiConfig.txtEmailUser.text(), \
                    self.camRunTime.frame, \
                    'teste', \
                    'testeRegion', \
                    'testeCam'):
                    
                    log.info('btnSaveEmail:: Teste email ok')
                    
                    msg.setText("Teste de Email Ok - Cheque seu email para confirmar se recebeu este alerta")
                    msg.exec()
                    
            
                    self.camRunTime.configEmailStatus = True        
                    self.uiConfig.lblCam1.clear()
                    self.refreshStatusConfig()
                    self.camRunTime.init()             
                    self.infCam.setCamRunTime(self.camRunTime)            
                    self.fillTabGeral()
                    
            else:
                self.camRunTime.configEmailStatus = False
                msg.setText("Senha ou usuário inválidos para envio de Email ! Cuidado, os alarmes não serão enviados ! ")
                msg.exec()
                
                
                
                    
                            
                             
            
            
            
            

            

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
        self.fillTabGeral()

        #global portaoVirtualSelecionado, portaoVirtualSelecionado, cropPolygon
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
        self.camRunTime.cropPolygon = True
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
        #print('ref_point_polygon: {:d}'.format(len(self.camRunTime.ref_point_polygon)))
        

        #checando campos em branco

        if len(self.uiConfig.txtRegionName.text()) == 0:
            msg.setText("Campo 'Nome da Região' em branco")
            msg.exec()
            self.uiConfig.txtRegionName.setFocus()
            statusFields = False
            
        if len(self.uiConfig.txtAlertaTimer.text()) == 0:
            msg.setText("Campo 'Alerta após n segundos' em branco")
            msg.exec()
            self.uiConfig.txtAlertaTimer.setFocus()
            statusFields = False

        elif len(self.uiConfig.txtThreshold.text()) == 0:
            msg.setText("Campo 'Acurácia' em branco")
            msg.exec()
            self.uiConfig.txtThreshold.setFocus()
            statusFields = False
            
        elif float(self.uiConfig.txtThreshold.text()) < 61:
            msg.setText("Cuidado, valores abaixo de 60% podem causar alarmes falso positivos ! Utilize valores baixos em ambientes com pouca visibilidade/luminosidade apenas")
            msg.exec()
            self.uiConfig.txtThreshold.setFocus()
            
            
        elif float(self.uiConfig.txtThreshold.text()) > 74:
            msg.setText("Cuidado, valores acima de 75% podem dificultar a detecção de pessoas ou carros! Utilize valores altos quando a imagem estiver com boa visibilidade/luminosidade")
            msg.exec()
            self.uiConfig.txtThreshold.setFocus()

        elif len(self.uiConfig.txtNameAlarm.text()) == 0:
            msg.setText("Campo 'Nome do Alarme' em branco")
            msg.exec()
            self.uiConfig.txtNameAlarm.setFocus()
            statusFields = False
            
        elif len(self.camRunTime.ref_point_polygon) < 3 and not self.statusConfig.checkNameRegion(self.uiConfig.txtRegionName.text()):
            msg.setText("Região não selecionada ! Através da aba ""Câmeras"" clique com o mouse até formar uma região de interesse  ")
            msg.exec()
            self.camRunTime.portaoVirtualSelecionado = False
            statusFields = False
           
        elif self.camRunTime.camEmpty:
            msg.setText("Configure sua câmera primeiro !")
            msg.exec()
            self.camRunTime.portaoVirtualSelecionado = False
            statusFields = False
        
        #elif len(self.camRunTime.ref_point_polygon) >= 3 and not self.statusConfig.checkNameRegion(self.uiConfig.txtRegionName.text()):

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
                      'car':'True' if self.uiConfig.checkCar.isChecked() else 'False'}
                      #'bike':'True' if self.uiConfig.checkBike.isChecked() else 'False',
                      #'dog':'True' if self.uiConfig.checkDog.isChecked() else 'False'}
                      
        if self.uiConfig.txtAlertaTimer.text() == 0:
            timerAlerta = 0
        else:
            timerAlerta = int(self.uiConfig.txtAlertaTimer.text())


        if statusFields:

            if self.statusConfig.checkNameRegion(self.uiConfig.txtRegionName.text()):
            
                points = self.statusConfig.getRegion(self.uiConfig.txtRegionName.text()).get('pointsPolygon')

            else:
                points = self.camRunTime.ref_point_polygon

            self.statusConfig.addRegion(self.uiConfig.txtRegionName.displayText(),
                                   newAlarm, objectType, round(float(self.uiConfig.txtThreshold.displayText()),2), points, timerAlerta )
            self.refreshStatusConfig()
            
            
            self.camRunTime.regions = self.statusConfig.getRegions()                        
           
            self.btnSaveAlarm()
            #self.comboRegionsUpdate(len(self.camRunTime.regions) - 1)
            
            #self.uiConfig.btnSaveRegion.setEnabled(False)
            self.uiConfig.btnCancelRegion.setEnabled(False)

            self.camRunTime.portaoVirtualSelecionado = True
            self.camRunTime.ref_point_polygon.clear()
            self.camRunTime.cropPolygon = False
            
            self.camRunTime.init()
            
            #self.comboAlarmsUpdate(0)

    def btnSaveAlarm(self):
        log.info('btnSaveAlarm::')
        #print('btnSaveAlarm::')
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

            if len(self.camRunTime.regions) > 0:
                self.comboRegionsUpdate(len(self.camRunTime.regions) - 1)
            
            
            self.uiConfig.btnSaveAlarm.setEnabled(True)
            #self.uiConfig.btnDeleteAlarm.setEnabled(False)
            self.uiConfig.btnCancelAlarm.setEnabled(False)
            self.uiConfig.btnNewAlarm.setEnabled(True)
            self.uiConfig.comboAlarms.setEnabled(True)           
            
                
            

    def clearListCameras(self):
        

        self.uiConfig.comboBoxCamAtivas.clear()
        self.uiConfig.comboBoxCamEncontradas.clear()
        
        self.uiConfig.txtNomeCamAtiva.clear()
        self.uiConfig.txtNomeCamDisponivel.clear()
        self.uiConfig.txtUserCamDisponivel.clear()
        self.uiConfig.txtIpCamDisponivel.clear()
        self.uiConfig.txtPasswdCamDisponivel.clear()
        self.uiConfig.txtPortaCamDisponivel.clear()
        self.uiConfig.txtCanalCamDisponivel.clear()
        self.uiConfig.lblStatusTestarCam.clear()

    def clearFieldsTabGeralEmail(self):
        

        self.uiConfig.txtEmailName.clear()
        #self.uiConfig.txtEmailPort.clear()
        #self.uiConfig.txtEmailSmtp.clear()
        self.uiConfig.txtEmailSubject.clear()
        self.uiConfig.txtEmailTo.clear()
        self.uiConfig.txtEmailUser.clear()
        self.uiConfig.txtEmailPassword.clear()
        self.uiConfig.lblStatus.clear()
        self.uiConfig.lblStatusProcurarCam.clear()
        
        
    def btnRemoverCamEncontrada(self):        
        
                    
        log.info('btnRemoverCamEncontrada')
        if self.uiConfig.comboBoxCamEncontradas.currentIndex() != -1: 
            
            idCombo = self.uiConfig.comboBoxCamEncontradas.currentText().split(':')[0]
            idCombo = idCombo.replace('[','')
            idCombo = idCombo.replace(']','')
            
            i = 0
            for cam in self.camRunTime.listCamEncontradas:
                if cam.get('id') == idCombo:
                    #self.camRunTime.listCamAtivas[i]['nome'] = self.uiConfig.txtNomeCamAtiva.text()                    
                    break
                i = i + 1
            
            if len(self.camRunTime.listCamEncontradas) > 0:
                self.camRunTime.listCamEncontradas.pop(i)                    
                self.camRunTime.statusConfig.addListCamEncontradasConfig(self.camRunTime.listCamEncontradas)
                self.fillTabGeral()
                self.infCam.setCamRunTime(self.camRunTime)
   

    def btnRemoverCamAtiva(self):        
                    
        log.info('btnRemoverCamAtiva')
        if self.uiConfig.comboBoxCamAtivas.currentIndex() != -1: 
            
            idCombo = self.uiConfig.comboBoxCamAtivas.currentText().split(':')[0]
            idCombo = idCombo.replace('[','')
            idCombo = idCombo.replace(']','')
            
            i = 0
            for cam in self.camRunTime.listCamAtivas:
                if cam.get('id') == idCombo:
                    #self.camRunTime.listCamAtivas[i]['nome'] = self.uiConfig.txtNomeCamAtiva.text()
                    
                    break
                i = i + 1
            self.camRunTime.listCamAtivas.pop(i)            
            self.camRunTime.statusConfig.addListCamAtivasConfig(self.camRunTime.listCamAtivas)
            self.fillTabGeral()
            #self.infCam.setCamRunTime(self.camRunTime)
            self.camRunTime.init()
    
    
    def btnSalvarNomeCamAtiva(self):        
                    
        log.info('btnSalvarNomeCamAtiva')
        if self.uiConfig.comboBoxCamAtivas.currentIndex() != -1: 
            
            idCombo = self.uiConfig.comboBoxCamAtivas.currentText().split(':')[0]
            idCombo = idCombo.replace('[','')
            idCombo = idCombo.replace(']','')
            
            i = 0
            for cam in self.camRunTime.listCamAtivas:
                if cam.get('id') == idCombo:
                    self.camRunTime.listCamAtivas[i]['nome'] = self.uiConfig.txtNomeCamAtiva.text()
                    break
                i = i + 1
            
            self.camRunTime.statusConfig.addListCamAtivasConfig(self.camRunTime.listCamAtivas)
            self.fillTabGeral()
            #self.infCam.setCamRunTime(self.camRunTime)
            self.camRunTime.init()
    
    def btnAtivarCam(self):
        #global listCamAtivas, self.uiConfig, statusConfig

        log.info('btnAtivarCam:: Ativando camera selecionada')
        
        if len(self.camRunTime.listCamAtivas) > 0 and self.camRunTime.listCamAtivas is not None: 
            idCombo = self.uiConfig.comboBoxCamAtivas.currentText().split(':')[0]
            idCombo = idCombo.replace('[','')
            idCombo = idCombo.replace(']','')
            print('idCombo: {}'.format(idCombo))

            i = 0 
            #zerando a camera ativada anteriormente 
            for cam in self.camRunTime.listCamAtivas:
                self.camRunTime.listCamAtivas[i]['emUso'] = 'False'
                i = i + 1

            i = 0 
            for cam in self.camRunTime.listCamAtivas:
                print('cam.get(id): {}'.format(cam.get('id')))
                if cam.get('id') == idCombo:
                    self.camRunTime.listCamAtivas[i]['emUso'] = 'True'
                    print('cam source: ' + cam.get('source'))
                    log.info('cam source: ' + cam.get('source'))
                    self.uiConfig.txtUrlRstp.setText(cam.get('source'))
                    self.statusConfig.setRtspConfig(cam.get('source'))
                    self.camRunTime.nameCam = cam.get('nome')
                    print('btnAtivarCam:: novo nome cam: {}'.format(self.camRunTime.nameCam))
                    
                i = i + 1


            self.uiConfig.checkBoxWebCam.setCheckState(False)
            self.uiConfig.txtUrlRstp.setEnabled(True)
            
            self.statusConfig.addListCamAtivasConfig(self.camRunTime.listCamAtivas)            
            self.uiConfig.lblCam1.clear()          
            self.camRunTime.updateIpCam()            
            #self.__init__() #IJF checar
            self.fillTabGeral()
            self.uiConfig.lblStatusProcurarCam.setText('Camera ativada')
            self.camRunTime.init()
            
        else:
            self.uiConfig.lblStatusProcurarCam.setText('Sem câmeras ativas. Clique em "Procurar Câmeras" para uma nova varredura')
            

    
    
    def btnNovaCam(self):
        
        log.info('btnNovaCam::')
        status = False
        
        if len(self.uiConfig.txtNomeCamDisponivel.text()) == 0 \
           or len(self.uiConfig.txtIpCamDisponivel.text()) == 0 \
           or len(self.uiConfig.txtUserCamDisponivel.text()) == 0 \
           or len(self.uiConfig.txtPasswdCamDisponivel.text()) == 0 \
           or len(self.uiConfig.txtPortaCamDisponivel.text()) == 0 \
           or len(self.uiConfig.txtCanalCamDisponivel.text()) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Campo em branco")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg.setText("Por favor, preenchda todos os campos para incluir uma nova câmera ! ")
                msg.exec()
        else:

            source = 'rtsp://' + self.uiConfig.txtUserCamDisponivel.text() + ':' + self.uiConfig.txtPasswdCamDisponivel.text() + '@' \
                                        + self.uiConfig.txtIpCamDisponivel.text() + ':' + self.uiConfig.txtPortaCamDisponivel.text() + '/' + self.uiConfig.txtCanalCamDisponivel.text()
            #novo id 
            idMaior = 0
            for cam in self.camRunTime.listCamAtivas:
                if int(cam.get('id')) > idMaior:
                    idMaior = int(cam.get('id'))
                    
            for cam in self.camRunTime.listCamEncontradas:
                if int(cam.get('id')) > idMaior:
                    idMaior = int(cam.get('id'))
            
            idMaior = idMaior + 1
            
            novaCam = {'ip':self.uiConfig.txtIpCamDisponivel.text(),
                       'user':self.uiConfig.txtUserCamDisponivel.text(),
                       'passwd':self.uiConfig.txtPasswdCamDisponivel.text(),
                       'channel':self.uiConfig.txtCanalCamDisponivel.text(),
                       'port':self.uiConfig.txtPortaCamDisponivel.text(),
                       'source':source,
                       'emUso':'False',
                       'id':str(idMaior),
                       'nome':self.uiConfig.txtNomeCamDisponivel.text(),
                       'mac':'0'                   
                       }

            self.camRunTime.listCamEncontradas.append(novaCam)
            self.camRunTime.statusConfig.addListCamEncontradasConfig(self.camRunTime.listCamEncontradas)
            self.fillTabGeral()
            self.uiConfig.lblStatusTestarCam.setText('Clique em "Testar Configuração" para checar se esta câmera está funcionando')
            self.comboBoxCamEncontradasStateChanged(len(self.camRunTime.listCamEncontradas)-1)
            self.camRunTime.init()
   
        
    def clearFieldsCamConfig(self):
        self.uiConfig.txtNomeCamAtiva.clear()
        self.uiConfig.txtNomeCamDisponivel.clear()
        self.uiConfig.txtIpCamDisponivel.clear()
        self.uiConfig.txtUserCamDisponivel.clear()
        self.uiConfig.txtPasswdCamDisponivel.clear()
        self.uiConfig.txtPortaCamDisponivel.clear()
        self.uiConfig.txtCanalCamDisponivel.clear()
        self.uiConfig.lblStatusTestarCam.clear()
        
    # def comboBoxCamEncontradasStateChanged(self, i):
        
        # #print('comboBoxCamEncontradasStateChanged: {:d}'.format(i))
        
        # idCombo = None
        
        # if i != -1: 
            # idCombo = self.uiConfig.comboBoxCamEncontradas.currentText().split(':')[0]
            # idCombo = idCombo.replace('[','')
            # idCombo = idCombo.replace(']','')
            # #print('idCombo: {}'.format(idCombo))            
            
            
            # for cam in self.camRunTime.listCamEncontradas:
                # if cam.get('id') == idCombo:
                    
                    # self.uiConfig.txtNomeCamDisponivel.setText(cam.get('nome'))
                    # self.uiConfig.txtIpCamDisponivel.setText(cam.get('ip'))
                    # self.uiConfig.txtUserCamDisponivel.setText(cam.get('user'))
                    # self.uiConfig.txtPasswdCamDisponivel.setText(cam.get('passwd'))
                    # self.uiConfig.txtPortaCamDisponivel.setText(cam.get('port'))
                    # self.uiConfig.txtCanalCamDisponivel.setText(cam.get('channel'))                    
                    
                    # break
                
            
            
   
    def comboBoxCamEncontradasStateChanged(self, i):
        
        log.info('comboBoxCamEncontradasStateChanged: {:d}'.format(i))
        nome = None
        idCombo = None
        
        if i != -1: 
            idCombo = self.uiConfig.comboBoxCamEncontradas.currentText().split(':')[0]
            idCombo = idCombo.replace('[','')
            idCombo = idCombo.replace(']','')
            #print('idCombo: {}'.format(idCombo))            
            
            for cam in self.camRunTime.listCamEncontradas:
                if cam.get('id') == idCombo:
                    self.uiConfig.txtNomeCamDisponivel.setText(cam.get('nome'))
                    self.uiConfig.txtIpCamDisponivel.setText(cam.get('ip'))
                    self.uiConfig.txtUserCamDisponivel.setText(cam.get('user'))
                    self.uiConfig.txtPasswdCamDisponivel.setText(cam.get('passwd'))
                    self.uiConfig.txtPortaCamDisponivel.setText(cam.get('port'))
                    self.uiConfig.txtCanalCamDisponivel.setText(cam.get('channel'))
                    break
           
            #self.uiConfig.txtNomeCamAtiva.setText(nome)   
    
    
    def comboBoxCamAtivasStateChanged(self, i):
        
        #print('comboBoxCamAtivasStateChanged: {:d}'.format(i))
        nome = None
        idCombo = None
        
        if i != -1: 
            idCombo = self.uiConfig.comboBoxCamAtivas.currentText().split(':')[0]
            idCombo = idCombo.replace('[','')
            idCombo = idCombo.replace(']','')
            #print('idCombo: {}'.format(idCombo))
            
            
            for cam in self.camRunTime.listCamAtivas:
                if cam.get('id') == idCombo:
                    nome = cam.get('nome')
                    break
            
            self.uiConfig.txtNomeCamAtiva.setText(nome)
    
        
    
    def btnTestarConfigCam(self):

        #global listCamAtivas, listCamEncontradas, statusconfig
        log.info('btnTestarConfigCam::')
        
        if len(self.uiConfig.txtNomeCamDisponivel.text()) == 0 \
           or len(self.uiConfig.txtIpCamDisponivel.text()) == 0 \
           or len(self.uiConfig.txtUserCamDisponivel.text()) == 0 \
           or len(self.uiConfig.txtPasswdCamDisponivel.text()) == 0 \
           or len(self.uiConfig.txtPortaCamDisponivel.text()) == 0 \
           or len(self.uiConfig.txtCanalCamDisponivel.text()) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Campo em branco")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg.setText("Por favor, preenchda todos os campos para incluir uma nova câmera ! ")
                msg.exec()
        else:

            self.uiConfig.lblStatusTestarCam.clear()
            self.uiConfig.lblStatusTestarCam.setText('Testando configuração. Aguarde por favor...')
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
                                        + cam.get('ip') + ':' + self.uiConfig.txtPortaCamDisponivel.text() + '/' + self.uiConfig.txtCanalCamDisponivel.text()

                        camConfigurada = cam
                        break
                    i = i + 1
                

                log.info('btnTestarConfigCam:: testando source: {}'.format(source))
                ipCam, error = utils.camSource(source)                   
                
                if error != '':                                                                    
                    log.warning('btnTestarConfigCam:: Error camSource: {}'.format(error))
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Configuração inválida")
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg.setText('Configuração inválida, tente outro usuario, senha, porta ou canal')
                    msg.exec()
                    self.uiConfig.lblStatusTestarCam.setText('Configuração inválida, tente outro usuario, senha, porta ou canal')

                else:                                    
                    log.info('btnTestarConfigCam:: Cam ativa encontrada')
                    self.uiConfig.lblStatusTestarCam.setText('Câmera configurada corretamente. Pronto para uso')
                    self.camRunTime.listCamEncontradas.pop(i)

                    camConfigurada['user'] = self.uiConfig.txtUserCamDisponivel.text()
                    camConfigurada['passwd'] = self.uiConfig.txtPasswdCamDisponivel.text()
                    camConfigurada['channel'] = self.uiConfig.txtCanalCamDisponivel.text()
                    camConfigurada['source'] = source 
                    camConfigurada['emUso'] = 'False' 
                    
                    self.camRunTime.listCamAtivas.append(camConfigurada)

                    self.camRunTime.statusConfig.addListCamAtivasConfig(self.camRunTime.listCamAtivas)
                    self.camRunTime.statusConfig.addListCamEncontradasConfig(self.camRunTime.listCamEncontradas)
                    
                    self.refreshStatusConfig()
                    self.camRunTime.__init__() 
                    self.fillTabGeral()
                    self.infCam.setCamRunTime(self.camRunTime)

    def btnProcurarCam(self):
        
        log.info('Procurando cameras na rede')                
        self.uiConfig.lblStatusProcurarCam.setText('Procurando câmeras na rede local. Aguarde por favor...')

        self.clearListCameras() 
        
        self.camRunTime.listCamEncontradas.clear()
        self.camRunTime.listCamAtivas.clear()

        
        self.uiConfig.progressBarProcurarCam.show()
        
        ## Chamar Thread ##
        
        
        self.threadProcurarCam = QThread()
        self.threadProcurarCam = CamFinder(False)
        self.threadProcurarCam.updateProgress.connect(self.updateProcurarCam)
        self.threadProcurarCam.start()        
        log.info('self.threadProcurarCam.start()')

        

    
    @QtCore.pyqtSlot(float, 'QVariantList', 'QVariantList', bool)
    def updateProcurarCam(self, progress, listCamEncontradas, listCamAtivas, rtspError):
    
        #print('Progress: {:.2f}'.format(progress))
        log.info('initFormConfig::updateProcurarCam')
        self.uiConfig.progressBarProcurarCam.show()
        self.uiConfig.progressBarProcurarCam.setValue(progress)
        
        self.camRunTime.listCamAtivas = listCamAtivas
        self.camRunTime.listCamEncontradas = listCamEncontradas
        
        if not rtspError:
            if progress == 100:    
                
                log.info('initFormConfig::updateProcurarCam:: Processo finalizado. Adicionando cameras')
                
                for cam in self.camRunTime.listCamAtivas:
                    self.uiConfig.comboBoxCamAtivas.addItem('[' + cam.get('id') + ']: ' + cam.get('ip') + ' : ' + cam.get('port'))

                for cam2 in self.camRunTime.listCamEncontradas:
                    self.uiConfig.comboBoxCamEncontradas.addItem('[' + cam2.get('id') + ']: ' + cam2.get('ip') + ' : ' + cam2.get('port'))

                self.statusConfig.zerarListCamAtivasConfig() 
                self.statusConfig.zerarListCamEncontradasConfig()

                self.statusConfig.addListCamAtivasConfig(self.camRunTime.listCamAtivas)
                self.statusConfig.addListCamEncontradasConfig(self.camRunTime.listCamEncontradas)
                
                self.uiConfig.lblStatusProcurarCam.setText('Busca por novas câmeras terminado')
                self.uiConfig.progressBarProcurarCam.hide()
                
                self.camRunTime.init() 
                self.fillTabGeral()
                self.infCam.setCamRunTime(self.camRunTime)
                
        elif rtspError == 'webcam':
            log.info('initFormConfig::updateProcurarCam:: Erro na Webcam')
            self.uiConfig.lblStatus.setText('Webcam com erro. Cheque a configuração da Webcam e reinicie o Portão Virtual !')
            
        elif rtspError == 'rtsp':
            
            log.info('initFormConfig::updateProcurarCam:: Checando se a camera mudou de IP')
            #checar se o mac address camEmUso vs nova cam ativa
            camEmUso = self.statusConfig.getCamEmUsoConfig()
            
            if progress == 100:
                
                if (camEmUso is not None) and (self.camRunTime.listCamAtivas is not None):
                                    
                    for cam in self.camRunTime.listCamAtivas:                                                                    
                
                        if cam.get('mac') == camEmUso.get('mac'):
                            if cam.get('ip') != camEmUso.get('ip'):                               
                
                                log.info('Camera em uso mudou de IP')
                                log.info('Camera em uso IP: {}'.format(camEmUso.get('ip')))
                                log.info('Novo IP: {}'.format(cam.get('ip')))
                
                                
                                self.camRunTime.ipCam, self.camRunTime.error = utils.camSource(cam.get('source'))

                                if self.camRunTime.error != '':
                                    self.camRunTime.ipCam = None
                                    self.camRunTime.rtspStatus = False
                                    log.info('Erro camSource: {}'.format(self.camRunTime.error))
                
                                    #ui.lblStatus.setText('Falha em localizar novo IP automaticamente. Tente configurar o endereço RTSP, e clique em "Salvar"')
                                    #ui.lblStatusProcurarCam.setText('Falha em localizar o novo IP automaticamente. Tente configurar uma nova câmera ou fazer uma nova varredura por câmeras clicando em "Procurar Câmeras". ')
                                else:

                                    self.statusConfig.setRtspConfig(cam.get('source'))
                                    self.statusConfig.addListCamAtivasConfig(self.camRunTime.listCamAtivas)
                                    self.statusConfig.addListCamEncontradasConfig(self.camRunTime.listCamEncontradas)
                                    #ui.txtUrlRstp.setText(cam.get('source'))

                                    self.camRunTime.rtspStatus = True 
                                    #self.camRunTime.ipCam.set(3, self.camRunTime.RES_X)
                                    #self.camRunTime.ipCam.set(4, self.camRunTime.RES_Y)
                                    
                                    log.info('Conexao com camera restabelecida.')
                                    self.uiConfig.lblStatus.setText('Conexão com a camera estabelecida! Feche a janela para inciar o Portão Virtual')
                                    self.uiConfig.lblStatusProcurarCam.setText('Conexão com a câmera estabelecida! Feche a janela para inciar o Portão Virtual')
                                    break

                    #checar se o mac address camEmUso vs nova cam encontrada 
                    if (self.camRunTime.listCamEncontradas is not None) and (camEmUso is not None):
                        for cam in self.camRunTime.listCamEncontradas:
                            if cam.get('mac') == camEmUso.get('mac'):
                                if cam.get('ip') != camEmUso.get('ip'):
                                    
                                    log.info('Camera em uso mudou de IP')
                                    log.info('Camera em uso IP: {}'.format(camEmUso.get('ip')))
                                    log.info('Novo IP: {}'.format(cam.get('ip')))
                                    
                                    #ipCam, error = utils.camSource(source)

                                    self.uiConfig.lblStatus.setText('Câmera previamente configurada trocou de IP, localizamos o novo IP com sucesso. Porém a senha, porta ou canal precisam ser novamente configurados !')
                                    self.uiConfig.lblStatusProcurarCam.setText('Câmera previamente configurada trocou de IP, localizamos o novo IP com sucesso. Porém a senha, porta ou canal precisam ser novamente configurados !')
                                    break



    def btnSaveStorage(self):

        global emailSentFullVideosAllTime, emailSentFullVideosOnAlarmes, emailSentDiskFull
        
        log.info('\n btnSaveStorage::')

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
                self.camRunTime.emailSentDiskFull = False 

        if self.uiConfig.txtDefinirMaximoOnAlarmes.text() != '0' and len(self.uiConfig.txtDefinirMaximoOnAlarmes.text()) != 0:

            if float(self.uiConfig.txtDefinirMaximoOnAlarmes.text().replace(',', '.')) < discoLivre:
                self.camRunTime.emailSentFullVideosOnAlarmes = False 

        if self.uiConfig.txtDefinirMaximoAllTime.text() != '0' and len(self.uiConfig.txtDefinirMaximoAllTime.text()) != 0:

            if float(self.uiConfig.txtDefinirMaximoAllTime.text().replace(',', '.')) < discoLivre:
                self.camRunTime.emailSentFullVideosAllTime = False 

        if statusFields:

            self.statusConfig.addStorageConfig(
                    self.camRunTime.diskMaxUsage, 
                    self.uiConfig.txtAvisoUtilizacaoHD.text().replace(',', '.'), 
                    self.uiConfig.txtDefinirMaximoOnAlarmes.text().replace(',', '.'),
                    self.uiConfig.txtDefinirMaximoAllTime.text().replace(',', '.'),
                    "True" if self.uiConfig.radioButtonDeleteOldestFiles.isChecked() else "False",
                    "True" if self.uiConfig.radioButtonStopSaveNewVideos.isChecked() else "False"
                    )
        
            
            self.checkStorage()            
            self.refreshStatusConfig()
            self.camRunTime.init()
            
    def checkBoxDesativarAlarmes(self, state):
        
        log.info('::checkBoxPararAlarmes')
        
        if state == 0:            
            log.info('checkBoxPararAlarmes desligado')
            self.statusConfig.setDesativarAlarmes('False')
            
        elif (state == 1 or state == 2):            
            log.info('checkBoxPararAlarmes ligado')
            self.statusConfig.setDesativarAlarmes('True')
            
        self.refreshStatusConfig()
    
    
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
            
    def checkBoxTodosDiasStateChanged(self, state):
        if state == 0:
           self.uiConfig.checkMon.setCheckState(False)
           self.uiConfig.checkTue.setCheckState(False)
           self.uiConfig.checkWed.setCheckState(False)
           self.uiConfig.checkThur.setCheckState(False)
           self.uiConfig.checkFri.setCheckState(False)
           self.uiConfig.checkSat.setCheckState(False)
           self.uiConfig.checkSun.setCheckState(False)
           
        # Qt.Checked 
        elif (state == 1 or state == 2):
        
           self.uiConfig.checkMon.setCheckState(True)
           self.uiConfig.checkTue.setCheckState(True)
           self.uiConfig.checkWed.setCheckState(True)
           self.uiConfig.checkThur.setCheckState(True)
           self.uiConfig.checkFri.setCheckState(True)
           self.uiConfig.checkSat.setCheckState(True)
           self.uiConfig.checkSun.setCheckState(True)
        
           
    
    
    def checkBoxWebcamStateChanged(self, state):
    
        log.info('checkBoxWebcamStateChanged::')
        
        if state == 0:
           self.uiConfig.txtUrlRstp.setEnabled(True)
        # Qt.Checked 
        elif (state == 1 or state == 2):
            self.uiConfig.txtUrlRstp.clear()
            self.uiConfig.txtUrlRstp.setEnabled(False)
            #se a webcam está ativa, desativar cameras em uso
            i = 0            
            cam = None
            for cam in self.camRunTime.listCamAtivas:
                self.camRunTime.listCamAtivas[i]['emUso'] = 'False'
                i = i + 1
            
            if cam is not None:
                self.statusConfig.setRtspConfig('webcam')
                self.camRunTime.nameCam = cam.get('Webcam')
                

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
        log.info('refreshStatusConfig::')
        self.statusConfig = utils.StatusConfig()
        self.camRunTime.regions = self.statusConfig.getRegions()
        self.camRunTime.emailConfig = self.statusConfig.getEmailConfig()
        self.camRunTime.init()

    def comboAlarmsUpdate(self, i):
        self.clearFieldsAlarm()

        #preenchendo lista de alarmes
        
        if not self.statusConfig.isAlarmEmpty(self.uiConfig.comboRegions.currentText()) and not self.statusConfig.isRegionsEmpty():

            #print('comboAlarmsUpdate i: {:d}'.format(i))
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

        self.refreshStatusConfig()
        self.clearFieldsTabRegiao()
        
        #print('comboRegionsUpdate:: i: {:d}'.format(i))
        
        #r = regions[i]       

        if not self.statusConfig.isRegionsEmpty():
            for r in self.camRunTime.regions:
                self.uiConfig.comboRegions.addItem(r.get("nameRegion"))

            if i < len(self.camRunTime.regions):
                r = self.camRunTime.regions[i]
                #print('comboRegionsUpdate:: nameRegion1: {}'.format(r.get('nameRegion')))
            #else:
            #    r = self.camRunTime.regions[0]
               
            if r is not None:
                #print('comboRegionsUpdate:: nameRegion: {}'.format(r.get('nameRegion')))
                self.uiConfig.txtRegionName.setText(r.get('nameRegion'))
                self.uiConfig.txtThreshold.setText(str(r.get('prob_threshold')))
                self.uiConfig.txtAlertaTimer.setText(str(r.get('timerAlerta')))
                self.uiConfig.checkPerson.setCheckState(r.get('objectType').get('person')=="True")
                self.uiConfig.checkCar.setCheckState(r.get('objectType').get('car')=="True")
                #self.uiConfig.checkBike.setCheckState(r.get('objectType').get('bike')=="True")
                #self.uiConfig.checkDog.setCheckState(r.get('objectType').get('dog')=="True")

                self.uiConfig.comboRegions.setCurrentIndex(i)
                
                self.uiConfig.comboAlarms.clear()
                self.clearFieldsAlarm()
                
                #preenchendo lista de alarmes                    
                if not self.statusConfig.isAlarmEmpty(r.get('nameRegion')):                    
                    for a in self.camRunTime.regions[i].get('alarm'):
                        self.uiConfig.comboAlarms.addItem(a.get('name'))                
                    
                    self.comboAlarmsUpdate(0)
                    
            self.uiConfig.btnDeleteRegion.setEnabled(True)
            self.uiConfig.btnCancelRegion.setEnabled(False)
            self.uiConfig.btnSaveRegion.setEnabled(True)
        else:
            self.uiConfig.btnDeleteRegion.setEnabled(False)
            self.uiConfig.btnCancelRegion.setEnabled(False)
            self.uiConfig.btnSaveRegion.setEnabled(False)
            
            
            
        

    def clearFieldsAlarm(self):
        self.uiConfig.checkMon.setCheckState(False)
        self.uiConfig.checkTue.setCheckState(False)
        self.uiConfig.checkWed.setCheckState(False)
        self.uiConfig.checkThur.setCheckState(False)
        self.uiConfig.checkFri.setCheckState(False)
        self.uiConfig.checkSat.setCheckState(False)
        self.uiConfig.checkSun.setCheckState(False)
        self.uiConfig.checkTodosDias.setCheckState(False)
        self.uiConfig.checkEmailAlert.setCheckState(False)
        self.uiConfig.checkAlertSound.setCheckState(False)
        self.uiConfig.timeStart.clear()
        self.uiConfig.timeEnd.clear()
        self.uiConfig.txtNameAlarm.clear()
        #self.uiConfig.comboAlarms.clear()

    def clearFieldsTabRegiao(self):
        self.uiConfig.txtRegionName.clear()
        self.uiConfig.txtNameAlarm.clear()
        self.uiConfig.txtThreshold.clear()
        self.uiConfig.txtAlertaTimer.clear()
        self.uiConfig.comboAlarms.clear()
        self.uiConfig.comboRegions.clear()        
        self.uiConfig.checkPerson.setCheckState(False)
        #self.uiConfig.checkBike.setCheckState(False)
        self.uiConfig.checkCar.setCheckState(False)
        #self.uiConfig.checkDog.setCheckState(False)
        self.uiConfig.checkMon.setCheckState(False)
        self.uiConfig.checkTue.setCheckState(False)
        self.uiConfig.checkWed.setCheckState(False)
        self.uiConfig.checkThur.setCheckState(False)
        self.uiConfig.checkFri.setCheckState(False)
        self.uiConfig.checkSat.setCheckState(False)
        self.uiConfig.checkSun.setCheckState(False)
        self.uiConfig.checkTodosDias.setCheckState(False)
        self.uiConfig.timeEnd.clear()
        self.uiConfig.timeStart.clear()

    def fillTabGeral(self):
        

        self.uiConfig.txtEmailName.clear()
        #self.uiConfig.txtEmailPort.clear()
        #self.uiConfig.txtEmailSmtp.clear()
        self.uiConfig.txtEmailSubject.clear()
        self.uiConfig.txtEmailTo.clear()
        self.uiConfig.txtEmailUser.clear()
        self.uiConfig.txtEmailPassword.clear()
        self.uiConfig.lblStatus.clear()
        self.uiConfig.lblStatusProcurarCam.clear()
        self.uiConfig.lblInitStatus.clear()
        
        self.clearFieldsAlarm()
        
        self.uiConfig.comboBoxCamAtivas.clear()
        self.uiConfig.comboBoxCamEncontradas.clear()
        
        self.clearListCameras()        
        self.clearFieldsCamConfig()

        self.refreshStatusConfig()

        self.uiConfig.checkBoxDesabilitarLoginAutomatico.setCheckState( True if self.statusConfig.getLoginAutomatico() == "True" else False )
        
        self.uiConfig.checkBoxDesativarAlarmes.setCheckState( True if self.statusConfig.getDesativarAlarmes() == "True" else False )

        self.uiConfig.checkBoxVideoRecordingOnAlarmes.setCheckState( True if self.statusConfig.data.get("isRecordingOnAlarmes") == "True" else False )

        self.uiConfig.checkBoxVideoRecordingAllTime.setCheckState( True if self.statusConfig.data.get("isRecordingAllTime") == "True" else False )

        if self.statusConfig.data.get("camSource") == "webcam":
            self.uiConfig.txtUrlRstp.clear()
            self.uiConfig.checkBoxWebCam.setCheckState(True)
            self.camRunTime.nameCam = 'Webcam'           
        else:
            self.uiConfig.txtUrlRstp.setText(self.statusConfig.data.get("camSource"))

        self.uiConfig.txtDirRecordingAllTime.setText(self.statusConfig.data.get("dirVideosAllTime"))
        self.uiConfig.txtDirRecordingOnAlarmes.setText(self.statusConfig.data.get("dirVideosOnAlarmes"))
        self.uiConfig.txtAvisoUtilizacaoHD.setText(self.statusConfig.data["storageConfig"].get("diskMinUsage"))
        self.uiConfig.txtEmailName.setText(self.statusConfig.data["emailConfig"].get('name'))
        #self.uiConfig.txtEmailPort.setText(self.statusConfig.data["emailConfig"].get('port'))
        #self.uiConfig.txtEmailSmtp.setText(self.statusConfig.data["emailConfig"].get('smtp'))
        self.uiConfig.txtEmailUser.setText(self.statusConfig.data["emailConfig"].get('user'))

        passwd = self.statusConfig.data["emailConfig"].get('password')
        
        
        
        if self.statusConfig.data["emailConfig"].get('servidorEmail') == 'Gmail':
            self.uiConfig.comboBoxServidorEmail.setCurrentIndex(0)
        else:
            self.uiConfig.comboBoxServidorEmail.setCurrentIndex(1)
        
        if len(passwd) > 0:
            passwdEmail = utils.decrypt(passwd) 
            self.uiConfig.txtEmailPassword.setText(passwdEmail)        
            if passwdEmail == 'error':
                self.uiConfig.lblStatus.setText('Cheque se sua senha do email está cadastrada corretamente')
                self.uiConfig.txtEmailPassword.setFocus()
                
        
        self.uiConfig.txtEmailSubject.setText(self.statusConfig.data["emailConfig"].get('subject'))
        self.uiConfig.txtEmailTo.setText(self.statusConfig.data["emailConfig"].get('to'))
        
        
        self.comboRegionsUpdate(0)
        #self.comboAlarmsUpdate(0)        


        #carregar cams previamente escaneadas na rede
        for cam in self.camRunTime.listCamAtivas:
            if cam.get('emUso') == 'True':
                self.uiConfig.comboBoxCamAtivas.addItem('[' + cam.get('id') + ']: ' + '[' + cam.get('nome') + '] ' + cam.get('ip') + ' : ' + cam.get('port') + ' [em uso]')
            else:
                self.uiConfig.comboBoxCamAtivas.addItem('[' + cam.get('id') + ']: ' + '[' + cam.get('nome') + '] ' + cam.get('ip') + ' : ' + cam.get('port'))

        for cam in self.camRunTime.listCamEncontradas:
            self.uiConfig.comboBoxCamEncontradas.addItem('[' + cam.get('id') + ']: ' + cam.get('ip') + ' : ' + cam.get('port'))
                         

        # if self.uiConfig.comboBoxCamAtivas.currentIndex() != -1: 
            # idCombo = self.uiConfig.comboBoxCamAtivas.currentText().split(':')[0]
            # idCombo = idCombo.replace('[','')
            # idCombo = idCombo.replace(']','')
            # #print('idCombo ativas: {}'.format(idCombo))            
            
            # for cam in self.camRunTime.listCamAtivas:
                # if cam.get('id') == idCombo:
                    # nome = cam.get('nome')
                    # break
            
            # print('fillTabGeral:: nome: {}'.format(nome))
            # print('fillTabGeral:: camRunTime.nameCam: {}'.format(self.camRunTime.nameCam))
            # self.uiConfig.txtNomeCamAtiva.setText(nome)
            # self.camRunTime.nameCam = nome
            #print('fillTabGeral:: camRunTime.nameCam: {}'.format(nome))
            
        if self.uiConfig.comboBoxCamEncontradas.currentIndex() != -1: 
            self.comboBoxCamEncontradasStateChanged(self.uiConfig.comboBoxCamEncontradas.currentIndex())
            # idCombo = self.uiConfig.comboBoxCamEncontradas.currentText().split(':')[0]
            # idCombo = idCombo.replace('[','')
            # idCombo = idCombo.replace(']','')
            # print('idCombo encontradas: {}'.format(idCombo))            
            
        
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
        
        if self.camRunTime.init_video and self.camRunTime.sessionStatus and self.camRunTime.rtspStatus :
            self.uiConfig.lblInitStatus.setText('Executando')
        else:
            self.uiConfig.lblInitStatus.setText('Erro com a sessão, câmera ou configuração. Favor reiniciar o Portão Virtual')

    def loginAutomatico(self):
    
        global loginStatus 

        #global init_video, statusLicence, uiLogin, conexao, login 

        log.info('Checando conexão com a Internet')
        #uiLogin.lblStatus.setText("Checando conexão com a Internet")

        self.camRunTime.conexao = utils.checkInternetAccess()
        #conexao = True

        if self.camRunTime.conexao:    
        
            log.info('Checando licença no servidor - Por favor aguarde')
            
            email = self.statusConfig.dataLogin['user']
            passwd = utils.decrypt(self.statusConfig.dataLogin['passwd'])
            
            self.camRunTime.login = {'user':utils.encrypt(email), 'passwd':utils.encrypt(passwd), 'token':utils.encrypt(self.camRunTime.token)}
            #log.info('loginAutomatico::TOKEN: {}'.format(self.camRunTime.token))
            
            self.camRunTime.statusLicence, self.camRunTime.error  = checkLoginPv(self.camRunTime.login) 
            #statusLicence = True ## testando apenas IJF
            
            if self.camRunTime.statusLicence:
                
                log.info("Usuario logado")
                self.camRunTime.init_video = True 
                loginStatus = True
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
                    self.statusConfig.setLoginAutomatico('False')
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Login inválido")
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg.setText("Usuário ou senha inválido, o login automático foi desabilitado ! Por favor, reinicie o Portão Virtual novamente corrigindo sua senha ou usuário ! ")
                    msg.exec()
                    #uiLogin.lblStatus.setText("Usuário ou senha inválida. Tente novamente")

        else:

            log.info("Erro de conexao com a Internet")
            #uiLogin.lblStatus.setText("Cheque sua conexão com a Internet por favor e tente mais tarde")

    
    
    @pyqtSlot()
    def warningSessionLossFirst(self):
        log.info('warningSessionLoss')
        self.uiConfig.lblInitStatus.setText('Login efetuado em outra máquina. Esta sessão será fechada em breve')
    
    
    @pyqtSlot()
    def warningSessionLoss(self):
    
        log.info('warningSessionLoss')
        utils.stopWatchDog()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Erro")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setText("Sua sessão expirou ! Verifique se alguém fez login em outra máquina e faça o login novamente.")
        msg.exec()
    
    @pyqtSlot()
    def checkStorage(self):    
        
        log.info('initFormConfig::checkStorage')
        self.camRunTime.dirVideosOnAlarmesUsedSpace = utils.getDirUsedSpace(self.statusConfig.data["dirVideosOnAlarmes"])
        self.camRunTime.dirVideosAllTimeUsedSpace = utils.getDirUsedSpace(self.statusConfig.data['dirVideosAllTime'])
        self.camRunTime.isDiskFull = utils.isDiskFull(self.camRunTime.diskMinUsage) 
        self.camRunTime.diskUsageFree = utils.getDiskUsageFree() 
        self.camRunTime.diskUsageFreeGb = utils.getDiskUsageFreeGb()        
        self.camRunTime.numDaysRecording = utils.getNumDaysRecording()
        
        
        self.uiConfig.progressBarDisponivelHD.setValue(utils.getDiskUsageFree())
        self.uiConfig.txtAvailableHD.setText('{:03.2f}'.format((utils.getDiskUsageFreeGb())))
        self.uiConfig.txtDirUsedVideosAllTime.setText('{:03.2f}'.format(utils.getDirUsedSpace(self.statusConfig.data["dirVideosAllTime"])))
        self.uiConfig.txtDirUsedVideosOnAlarmes.setText('{:03.2f}'.format(utils.getDirUsedSpace(self.statusConfig.data["dirVideosOnAlarmes"])))

        self.uiConfig.txtDiasEstimado.setText('{:d}'.format((utils.getNumDaysRecording())) + ' dias' )        
        
        
        
        if self.camRunTime.isDiskFull:
            self.uiConfig.lblInitStatus.setText('Seu HD está cheio, aumente seu espaço em disco !') 
            


if __name__=="__main__":    
    
    app = QApplication(sys.argv)                  
                 
    uiConfig = FormProc()    
    
    if socket.gethostname() != 'pv-server':
        print('main:: rodando local')
        uiConfig.show()
    
        
 
    sys.exit(app.exec_())
            
    
       
 
    