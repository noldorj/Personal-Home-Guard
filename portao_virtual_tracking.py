import cv2 as cv
import numpy as np
#from datetime import date
import time
from objectTracking.pyimagesearch.centroidtracker import CentroidTracker
from Utils_tracking import sendMailAlert
from Utils_tracking import sendMail
from Utils_tracking import saveImageBox
import utilsCore as utils
import logging as log
import sys
from collections import deque
import os
import subprocess
import getpass
import shutil
from rtsp_discover.rtsp_discover import getListCam

#import ffmpeg

from threading import Thread
from checkLicence.sendingData import checkLoginPv 
from checkLicence.sendingData import changePasswdPv 
from checkLicence.sendingData import checkSessionPv
from checkLicence.sendingData import forgotPasswordPv 

from objectDetectionTensorFlow import objectDetection 

import secrets
import psutil


from matplotlib.path import Path

#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8')
#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', filename='pv.log', encoding='utf-8', level=log.DEBUG)

log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S',  encoding='utf-8', level=log.CRITICAL, stream=sys.stdout ) 
OS_PLATFORM = 'windows'

if sys.platform == 'linux':
    OS_PLATFORM = 'linux'
    #subprocess.call([r'openvino/bin/setupvars.sh'])
#else:
    #subprocess.call([r'openvino\bin\setupvars.bat'])

import pluginOpenVino as pOpenVino

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
import sys
from mainForm import *
from formLogin import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QErrorMessage, QMessageBox, QPushButton
from PyQt5.QtCore import QTime, QThread


#import tensorflow as tf


#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, stream=sys.stdout)
#variaveis globais


diskFullWarned = False
diskFullVideosOnAlarmes = False
diskFullVideosAllTimeWarned = False

emailSentFullVideosOnAlarmes = False
emailSentFullVideosAllTime = False
emailSentDiskFull = False
emailSentdirVideosAllTimeEmpty = False
emailSentdirVideosOnAlarmesEmpty = False

pilhaAlertasNaoEnviados = deque() 

listCamEncontradas = []
listCamAtivas = []

conectado = None
conexao = False
frame = None

rtspStatus = True

fernetKey = None

#CHECK_SESSION = 300 # checar sessao a cada 5 min
CHECK_SESSION = 30 # checar sessao a cada 5 min
#GRAVANDO_TIME = 300 #gravar videos de 5min 
GRAVANDO_TIME = 30 #gravar videos de 5min 

LOGIN_AUTOMATICO = False

#INTERNET_OFF = 60 #3 horas apos queda de internet para o programa perder as funcoes
INTERNET_OFF = 7200 #3 horas apos queda de internet para o programa perder as funcoes
STOP_ALL = False

#720p: 1280 x 720
#480p: 854 x 480

RES_X = 854 
RES_Y = 480 


token = secrets.token_urlsafe(20)
gravandoAllTime = False
gravandoOnAlarmes = False

#tempo sem objetos detectados
tEmptyStart = time.time()

counter = 0
tEmpty = 0
tEmptyEnd = 0
tEmptyStart = 0
stopSound = False
initOpenVinoStatus = True

nameVideo  = 'firstVideo'
nameVideoAllTime  = 'firstVideo'
newVideo = True
releaseVideoOnAlarmes = False 
releaseVideoAllTime = False 
h = None
w = None
#objects = None
#FPS = ipCam.get(cv.CAP_PROP_FPS) #30.0 #frames per second
FPS = 4  #de acordo com o manual da mibo ic5 intelbras

#primeiro objeto é enviado
listObjectMailAlerted = []
listObjectSoundAlerted = []
listObjectVideoRecorded = []
out_video = None
out_video_all_time = None

init_video = False 
pausaConfig = False

statusPasswd = False
statusLicence = False

statusConfig = None
pb = None
pbtxt = None
regions = None
emailConfig = None
portaoVirtualSelecionado = False 
status_dir_criado_on_alarmes = None
status_dir_criado_all_time = None
dir_video_trigger_on_alarmes = None
dir_video_trigger_all_time = None
source = None
ipCam = None
prob_threshold = 60.0 
#list de objetos identificados pela CNN
listObjects = []
#lista de objetos detectados da rede neural
detection =[]
#lista de boxes detectados
listRectanglesDetected = []
#lista de objetos traqueados
listObjectsTracking = []
#linhas e colunas do video (resolucao)
rows = None
cols = None
next_frame = None
nchw = []
exec_net = None
out_blob = None
input_blob = None
cur_request_id, next_request_id, render_time = 0, 0, 0
prob_threshold_returned = 0
#colors = np.random.uniform(0, 255, size=(len(classes), 3))
tSound, tSoundEnd, tSoundLimit, tSoundStart = 0, 0, 0, 0
# initialize our centroid tracker and frame dimensions
ct = CentroidTracker()
(H, W) = (None, None)
listObjectDetected = list()
idObjeto = 0
drawing = False     # true if mouse is pressed
mode = True         # if True, draw rectangle.
ix, iy = -1, -1
#ref_point = []
ref_point_polygon = list()
#crop = False
cropPolygon = False
#showGate = False
#regiaoPortao = None
hora = None
current_data_dir = None
isOpenVino = True
device = 'CPU'
openVinoModelXml = None 
openVinoModelBin = None
openVinoCpuExtension = None 
openVinoPluginDir = None 
openVinoModelName = None

login = None 
sessionStatus = True

#variaveis do disco
diskMinUsage = 15
diskMaxUsage = 85
spaceMaxDirVideosOnAlarme = 0 #zero significa sem limites de utilizacao do disco 
spaceMaxDirVideosAllTime = 0  #zero significa sem limites de utilizacao do disco 
eraseOldestFiles = True 
stopSaveNewVideos = False


#inicializa configuracoes do sistema

def initConfig():

    log.debug(' ')
    log.debug('initConfig')
    log.debug(' ')

    global statusConfig, pb, pbtxt, regions, emailConfig, portaoVirtualSelecionado
    global status_dir_criado_all_time, status_dir_criado_all_time, dir_video_trigger_on_alarmes, dir_video_trigger_all_time, source, ipCam, prob_threshold, hora, current_data_dir, isOpenVino
    global device, openVinoModelXml, openVinoModelBin, openVinoCpuExtension, openVinoPluginDir, openVinoModelName, gravandoAllTime 
    global spaceMaxDirVideosAllTime, spaceMaxDirVideosOnAlarme, eraseOldestFiles, stopSaveNewVideos, diskMaxUsage, diskMinUsage, rtspStatus, LOGIN_AUTOMATICO
    global listCamAtivas, listCamEncontradas
    
    current_data_dir = utils.getDate()
    current_data_dir = [current_data_dir.get('day'), current_data_dir.get('month')]
    hora = utils.getDate()['hour'].replace(':','-')
    
    statusConfig = utils.StatusConfig()

    LOGIN_AUTOMATICO = True if statusConfig.getLoginAutomatico() == 'True' else False
    
    gravandoAllTime = True if statusConfig.data["isRecordingAllTime"] == 'True' else False
    gravandoOnAlarmes = True if statusConfig.data["isRecordingOnAlarmes"] == 'True' else False
    diskMinUsage = int(statusConfig.data["storageConfig"]["diskMinUsage"])
    
    isOpenVino = statusConfig.data["isOpenVino"] == 'True'

    listCamAtivas = statusConfig.getListCamAtivas()

    listCamEncontradas = statusConfig.getListCamEncontradas()

    spaceMaxDirVideosOnAlarme = float(statusConfig.data["storageConfig"]["spaceMaxDirVideosOnAlarme"])  
    spaceMaxDirVideosAllTime = float(statusConfig.data["storageConfig"]["spaceMaxDirVideosAllTime"])  
    eraseOldestFiles = True if statusConfig.data["storageConfig"]["eraseOldestFiles"] == 'True' else False 
    stopSaveNewVideos = True if statusConfig.data["storageConfig"]["stopSaveNewVideos"] == 'True' else False 
    
    #if isOpenVino:
    #    import pluginOpenVino as pOpenVino

    #device = statusConfig.data["openVinoDevice"]
    device, openVinoModelXml, openVinoModelBin, openVinoCpuExtension, openVinoPluginDir, openVinoModelName  = statusConfig.getActiveDevice()

    
    # dnnMOdel for TensorFlow Object Detection API
    pb = statusConfig.data["dnnModelPb"] 
    pbtxt = statusConfig.data["dnnModelPbTxt"] 
    
    #Carregando regioes salvas
    regions = statusConfig.getRegions()
    emailConfig = statusConfig.getEmailConfig()
    
    #se existirem regioes ja selecionadas, o portao virtual é mostrado
    #if len(regions) > 0:
    #    portaoVirtualSelecionado = True
    portaoVirtualSelecionado = True
    
    #Criando diretorio para salvar videos de alarmes
    status_dir_criado_on_alarmes, dir_video_trigger_on_alarmes = utils.createDirectory(statusConfig.data["dirVideosOnAlarmes"])

    status_dir_criado_all_time, dir_video_trigger_all_time = utils.createDirectory(statusConfig.data["dirVideosAllTime"])
    
    
    #origem do stream do video
    source = statusConfig.data["camSource"]
    log.debug('source: {}'.format(source))
    ipCam, error = utils.camSource(source)

    if error != '':
        ipCam = None
        rtspStatus = False
        log.critical('Erro camSource: {}'.format(error))
        ui.lblStatus.setText('Erro de conexao da camera. Tente configurar o endereço RTSP, e clique em "Salvar"')
        ui.lblStatusProcurarCam.setText('Erro de conexao da camera. Tente configurar uma nova câmera ou fazer uma nova varredura por câmeras clicando em "Procurar Câmeras". ')
        
        #checar se houve mudança de IP
        camEmUso = statusConfig.getCamEmUsoConfig()

        camListEncontradas, camListAtivas = getListCam() 

        #checar se o mac address camEmUso vs nova cam ativa
        for cam in camListAtivas:
            if cam.get('mac') == camEmUso.get('mac'):
                if cam.get('ip') != camEmUso.get('ip'):
                    
                    log.debug('Camera em uso mudou de IP')
                    log.debug('Camera em uso IP: {}'.format(camEmUso.get('ip')))
                    log.debug('Novo IP: {}'.format(cam.get('ip')))
                    
                    ipCam, error = utils.camSource(cam.get('source'))

                    if error != '':
                        ipCam = None
                        rtspStatus = False
                        log.critical('Erro camSource: {}'.format(error))
                        ui.lblStatus.setText('Falha em localizar novo IP automaticamente. Tente configurar o endereço RTSP, e clique em "Salvar"')
                        ui.lblStatusProcurarCam.setText('Falha em localizar o novo IP automaticamente. Tente configurar uma nova câmera ou fazer uma nova varredura por câmeras clicando em "Procurar Câmeras". ')
                    else:

                        statusConfig.setRtspConfig(cam.get('source'))
                        statusConfig.addListCamAtivasConfig(listCamAtivas)
                        statusConfig.addListCamEncontradasConfig(listCamEncontradas)
                        ui.txtUrlRstp.setText(cam.get('source'))

                        rtspStatus = True 
                        ipCam.set(3, RES_X)
                        ipCam.set(4, RES_Y)
                        log.debug('Conexao com camera restabelecida.')
                        ui.lblStatus.setText('Conexão com a camera estabelecida! Feche a janela para inciar o Portão Virtual')
                        ui.lblStatusProcurarCam.setText('Conexão com a câmera estabelecida! Feche a janela para inciar o Portão Virtual')
                        break



        #checar se o mac address camEmUso vs nova cam encontrada 
        for cam in camListEncontradas:
            if cam.get('mac') == camEmUso.get('mac'):
                if cam.get('ip') != camEmUso.get('ip'):
                    log.debug('Camera em uso mudou de IP')
                    log.debug('Camera em uso IP: {}'.format(camEmUso.get('ip')))
                    log.debug('Novo IP: {}'.format(cam.get('ip')))
                    
                    #ipCam, error = utils.camSource(source)

                    ui.lblStatus.setText('Câmera previamente configurada trocou de IP, localizamos o novo IP com sucesso. Porém a senha, porta ou canal precisam ser novamente configurados !')
                    ui.lblStatusProcurarCam.setText('Câmera previamente configurada trocou de IP, localizamos o novo IP com sucesso. Porém a senha, porta ou canal precisam ser novamente configurados !')
                    break 

    else:
        rtspStatus = True 
        ipCam.set(3, RES_X)
        ipCam.set(4, RES_Y)
        log.debug('Conexao com camera restabelecida.')
        ui.lblStatus.setText('Conexão com a camera estabelecida! Feche a janela para inciar o Portão Virtual')
        ui.lblStatusProcurarCam.setText('Conexão com a câmera estabelecida! Feche a janela para inciar o Portão Virtual')

    prob_threshold = float(statusConfig.data["prob_threshold"])

    #configuracoes de armazenamento
    

def isIdInsideRegion(centroid, ref_point_polygon):
    path = Path(ref_point_polygon)
    mask = path.contains_points([(centroid[0], centroid[1])])
    return mask


def polygonSelection(event, x, y, flags, param): 
    global ref_point_polygon, cropPolygon, portaoVirtualSelecionado

    if event == cv.EVENT_LBUTTONDBLCLK and not portaoVirtualSelecionado:  
        
        ref_point_polygon.append([x, y])
        cropPolygon = True

    elif not portaoVirtualSelecionado and flags == 0:

        portaoVirtualSelecionado = True


#from fbs_runtime.application_context.PyQt5 import ApplicationContext

#app = ApplicationContext()

app = QApplication (sys.argv)


class FormLogin(QWidget):
    def __init__(self, parent=None):
        super(FormLogin, self).__init__(parent)
        self.ui = Ui_formLogin()
        self.ui.setupUi(self)

    def closeEvent(self, event):
        log.info('close formLogin')


#uiLogin = Ui_formLogin()
#windowLogin = FormLogin()
#uiLogin.setupUi(windowLogin)

uiLogin = Ui_formLogin()
windowLogin = FormLogin()
uiLogin.setupUi(windowLogin)


class FormProc(QWidget):
    def __init__(self, parent=None):
        super(FormProc, self).__init__(parent)
        self.ui = Ui_formConfig()
        self.ui.setupUi(self)

    def closeEvent(self, event):
        statusFields = True
        pausaConfig = False
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Campo 'Ativo'")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        #checar se há somente 1 modelo OpenVino ativo
        if not statusConfig.checkActiveModel():
            msg.setText("Um modelo deve estar selecionado como 'Ativo'")
            msg.exec()
            event.ignore()

        elif not statusConfig.checkDuplicatedActiveModels():
            log.debug("Existe mais de um modelo 'Ativo'")
            msg.setText("Existe mais de um modelo como 'Ativo'")
            msg.exec()
            event.ignore()

ui = Ui_formConfig()
windowConfig = FormProc()
ui.setupUi(windowConfig)



#cv.namedWindow('frame')
#cv.setMouseCallback('frame', polygonSelection)


#fourcc = cv.VideoWriter_fourcc(*'X264')
#for linux x264 need to recompile opencv mannually
fourcc = cv.VideoWriter_fourcc(*'X''V''I''D') #IJF
#fourcc = cv.VideoWriter_fourcc('M','J','P','G')
#fourcc = cv.VideoWriter_fourcc(*'MP4V')

#cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, FPS, (1280,720))

posConfigPv = 255



#---------------- gui Form Login -------------------
def btnExit():
    global statusLicence, init_video

    log.debug('Login Cancelado')
    statusLicence = False
    init_video = False

    stopWatchDog()

    windowLogin.close()



#import httplib
import http.client as httplib

def checkInternetAccess():

    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        log.info('Checando conexao...')
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        log.info('Falha na conexao')
        conn.close()
        return False

def btnAlterarSenha():
    global uiLogin, statusPasswd

    log.info("Alterando a senha")
    
    conexao = checkInternetAccess()

    if conexao:    

        if (uiLogin.txtNovaSenha.text() == uiLogin.txtNovaSenha2.text()):
        
            login = {'user':utils.encrypt(uiLogin.txtEmail_minhaConta.text()), 'passwd':utils.encrypt(uiLogin.txtNovaSenha.text()), 'token':utils.encrypt(token)} 
            

            statusPasswd, error = changePasswdPv(login)
            
            if statusPasswd:
                
                log.info("Senha alterada com sucesso")
                uiLogin.lblStatus.setText("Senha alterada com sucesso")
            
            else:

                #se o servidor estiver fora do ar - libera acesso ao sistema 
                if error == "conexao":
                    log.warning("Erro de conexão com o servidor")
                    uiLogin.lblStatus.setText("Erro de conexão com o servidor")

                elif error == "login":
                    log.warning("Usuario invalido")
                    uiLogin.lblStatus.setText("Usuário ou senha inválida. Tente novamente")
    else:
        log.info("Erro de conexao com a Internet")
        uiLogin.lblStatus.setText("Cheque sua conexão com a Internet por favor e tente mais tarde")

def btnEsqueciSenha():
    global uiLogin, conexao

    log.info('btnEsqueciSenha:: Checando conexão com a Internet')
    uiLogin.lblStatus.setText("Checando conexão com a Internet")

    conexao = checkInternetAccess()

    if conexao:    
    
        log.info('btnEsqueciSenha:: Checando licença no servidor - Por favor aguarde')
        #uiLogin.lblStatus.setText("Conectando com o servidor")
        status, error = forgotPasswordPv(uiLogin.txtEmail.text()) 
        
        if error == "conexao":
            log.warning("btnEsqueciSenha:: Erro de conexão com o servidor")
            uiLogin.lblStatus.setText("Error de conexão com o servidor - tente novamente")

        elif error == "login":

            log.warning("Usuario invalido")
            uiLogin.lblStatus.setText("Usuário desconhecido.")

        if status:
            log.warning("Email de recuperação de senha enviado")
            uiLogin.lblStatus.setText("Email de recuperação de senha enviado")

    else:
         
        log.warning("Erro de conexao com a Internet")
        uiLogin.lblStatus.setText("Cheque sua conexão com a Internet.")


def btnAtivarCam():
    global listCamAtivas, ui, statusConfig

    log.debug('Ativando camera selecionada')
    
    if len(listCamAtivas) > 0: 
        idCombo = ui.comboBoxCamAtivas.currentText().split(':')[0]
        idCombo = idCombo.replace('[','')
        idCombo = idCombo.replace(']','')
        log.debug('idCombo: ' + idCombo)

        i = 0 
        #zerando a camera ativada anteriormente 
        for cam in listCamAtivas:
            listCamAtivas[i]['emUso'] = 'False'
            i = i + 1

        i = 0 
        for cam in listCamAtivas:
            if cam.get('id') == idCombo:
                listCamAtivas[i]['emUso'] = 'True'
                log.debug('cam source: ' + cam.get('source'))
                ui.txtUrlRstp.setText(cam.get('source'))
                statusConfig.setRtspConfig(cam.get('source'))
                ui.lblStatusProcurarCam.setText('Camera ativada')
            i = i + 1


        statusConfig.addListCamAtivasConfig(listCamAtivas)
        initConfig()


    else:
        ui.lblStatusProcurarCam.setText('Sem câmeras ativas. Clique em "Procurar Câmeras" para uma nova varredura')

def btnTestarConfigCam():

    global listCamAtivas, listCamEncontradas, statusconfig
    log.debug('Testando configuracao de camera encontrada na rede')

    camConfigurada = None
    source = None
   
    if ui.comboBoxCamEncontradas.currentIndex() != -1: 

        idCombo = ui.comboBoxCamEncontradas.currentText().split(':')[0]
        idCombo = idCombo.replace('[','')
        idCombo = idCombo.replace(']','')
    
        i = 0 

        for cam in listCamEncontradas:

            if cam.get('id') == idCombo:
                source = 'rtsp://' + ui.txtUserCamDisponivel.text() + ':' + ui.txtPasswdCamDisponivel.text() + '@' \
                                + cam.get('ip') + ':' + ui.txtPortaCamDisponivel.text() + '/' + ui.txtCanalCamDiponivel.text()

                camConfigurada = cam
                break
            i = i + 1
        

        ipCam, error = utils.camSource(source)                   
        
        if error != '':                                                                    
            log.warning('Erro camSource: {}'.format(error))
            ui.lblStatusTestarCam.setText('Configuração inválida, tente outro usuario, senha, porta ou canal')

        else:                                    
            log.info('Cam ativa encontrada')
            ui.lblStatusTestarCam.setText('Câmera configurada corretamente. Pronto para uso')
            listCamEncontradas.pop(i)

            camConfigurada['user'] = ui.txtUserCamDisponivel.text()
            camConfigurada['passwd'] = ui.txtPasswdCamDisponivel.text()
            camConfigurada['channel'] = ui.txtCanalCamDiponivel.text()
            camConfigurada['source'] = source 
            camConfigurada['emUso'] = 'False' 
            
            listCamAtivas.append(camConfigurada)

            statusConfig.addListCamAtivasConfig(listCamAtivas)
            statusConfig.addListCamEncontradasConfig(listCamEncontradas)
            
            initConfig()
            fillTabGeral()


def btnProcurarCam():
    
    log.debug('Procurando cameras na rede')
    global listCamAtivas, listCamEncontradas, statusconfig

    clearListCameras() 
    
    listCamEncontradas.clear()
    listCamAtivas.clear()

    ui.lblStatusProcurarCam.setText('Procurando cameras na rede... aguarde')

    listCamEncontradas, listCamAtivas = getListCam()

    for cam in listCamAtivas:
        ui.comboBoxCamAtivas.addItem('[' + cam.get('id') + ']:' + cam.get('ip') + ' : ' + cam.get('port'))

    for cam2 in listCamEncontradas:
        ui.comboBoxCamEncontradas.addItem('[' + cam2.get('id') + ']:' + cam2.get('ip') + ' : ' + cam2.get('port'))

    statusConfig.zerarListCamAtivasConfig() 
    statusConfig.zerarListCamEncontradasConfig()

    statusConfig.addListCamAtivasConfig(listCamAtivas)
    statusConfig.addListCamEncontradasConfig(listCamEncontradas)
    
    initConfig()
    fillTabGeral()


def btnSaveStorage():

    global emailSentFullVideosAllTime, emailSentFullVideosOnAlarmes, emailSentDiskFull

    statusFields = True 
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Campo em branco")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    #checando campos em branco
    discoLivre = utils.getDiskUsageFreeGb()
    discoLivrePorcentagem = utils.getDiskUsageFree()

    if len(ui.txtDefinirMaximoAllTime.text()) == 0 and not ui.checkBoxNoLimitsVideosAllTime.isChecked():
        msg.setText("Favor preencher o campo 'Espaço máximo em GB na pasta Videos 24hs' ")
        msg.exec()
        ui.txtDefinirMaximoAllTime.setFocus()
        statusFields = False


    if len(ui.txtDefinirMaximoOnAlarmes.text()) == 0 and not ui.checkBoxNoLimitsVideosOnAlarmes.isChecked():
        msg.setText("Favor preencher o campo 'Espaço máximo em GB na pasta Videos Alarmes' ")
        msg.exec()
        ui.txtDefinirMaximoOnAlarmes.setFocus()
        statusFields = False


    if  not ui.checkBoxNoLimitsVideosAllTime.isChecked() \
        and ui.txtDefinirMaximoAllTime.text() != '0' \
        and len(ui.txtDefinirMaximoAllTime.text()) != 0:

            if float(ui.txtDefinirMaximoAllTime.text().replace(',', '.')) > discoLivre: 
                msg.setText("Não há espaço em disco disponível, coloque um valor em GB menor que " + str(discoLivre) + ".")
                msg.exec()
                ui.txtDefinirMaximoAllTime.setFocus()
                statusFields = False


    if  not ui.checkBoxNoLimitsVideosOnAlarmes.isChecked() \
        and len(ui.txtDefinirMaximoOnAlarmes.text()) != 0 \
        and ui.txtDefinirMaximoOnAlarmes.text() != '0':
        
            if float(ui.txtDefinirMaximoOnAlarmes.text().replace(',', '.')) > discoLivre:
                msg.setText("Não há espaço em disco disponível, coloque um valor em GB menor que " + str(discoLivre) + ".")
                msg.exec()
                ui.txtDefinirMaximoOnAlarmes.setFocus()
                statusFields = False


    log.info('txtAvisoUtilizacaoHD: {}'.format(ui.txtAvisoUtilizacaoHD.text()))
    log.info('getDiskUsageFreeGb: {:f}'.format(utils.getDiskUsageFreeGb()))


    if len(ui.txtAvisoUtilizacaoHD.text()) == 0:
        discoValor = discoLivrePorcentagem - 5 
        if discoValor <= 0:
            ui.txtAvisoUtilizacaoHD.setText(str(discoLivrePorcentagem))
        else:
            ui.txtAvisoUtilizacaoHD.setText(str(discoValor))

        msg.setText("Favor preencher o campo 'Nível mínimo de espaço em disco em porcentagem' ")
        msg.exec()
        ui.txtAvisoUtilizacaoHD.setFocus()
        statusFields = False

    if ui.txtAvisoUtilizacaoHD.text() != '0' and len(ui.txtAvisoUtilizacaoHD.text()) != 0:

        if float(ui.txtAvisoUtilizacaoHD.text().replace(',', '.')) < discoLivrePorcentagem:
            emailSentDiskFull = False 

    if ui.txtDefinirMaximoOnAlarmes.text() != '0' and len(ui.txtDefinirMaximoOnAlarmes.text()) != 0:

        if float(ui.txtDefinirMaximoOnAlarmes.text().replace(',', '.')) < discoLivre:
            emailSentFullVideosOnAlarmes = False 

    if ui.txtDefinirMaximoAllTime.text() != '0' and len(ui.txtDefinirMaximoAllTime.text()) != 0:

        if float(ui.txtDefinirMaximoAllTime.text().replace(',', '.')) < discoLivre:
            emailSentFullVideosAllTime = False 

    if statusFields:

        statusConfig.addStorageConfig(
                diskMaxUsage, 
                ui.txtAvisoUtilizacaoHD.text().replace(',', '.'), 
                ui.txtDefinirMaximoOnAlarmes.text().replace(',', '.'),
                ui.txtDefinirMaximoAllTime.text().replace(',', '.'),
                "True" if ui.radioButtonDeleteOldestFiles.isChecked() else "False",
                "True" if ui.radioButtonStopSaveNewVideos.isChecked() else "False"
                )
    
        refreshStatusConfig() 
        initConfig()


def loginAutomatico():

    global init_video, statusLicence, uiLogin, conexao, login 

    log.debug('Checando conexão com a Internet')
    #uiLogin.lblStatus.setText("Checando conexão com a Internet")

    conexao = checkInternetAccess()
    #conexao = True

    if conexao:    
    
        log.debug('Checando licença no servidor - Por favor aguarde')
        
        email = statusConfig.dataLogin['user']
        passwd = utils.decrypt(statusConfig.dataLogin['passwd'])
        
        login = {'user':utils.encrypt(email), 'passwd':utils.encrypt(passwd), 'token':utils.encrypt(token)}
        
        statusLicence, error  = checkLoginPv(login) 
        #statusLicence = True ## testando apenas IJF
        
        if statusLicence:
            
            log.debug("Usuario logado")
            init_video = True 
            windowLogin.close()
        
        else:

            #se o servidor estiver fora do ar - libera acesso ao sistema 
            if error == "conexao":
                log.warning("Erro de conexão com o servidor")

                init_video = True
                statusLicence = True
                log.warning("Liberando acesso")
                windowLogin.close()

            elif error == "login":

                init_video = False
                log.warning("Usuario invalido")
                #uiLogin.lblStatus.setText("Usuário ou senha inválida. Tente novamente")

    else:

        log.info("Erro de conexao com a Internet")
        #uiLogin.lblStatus.setText("Cheque sua conexão com a Internet por favor e tente mais tarde")

def btnLogin():
    #checando licenca de usuario no servidor
    global init_video, statusLicence, uiLogin, conexao, login 

    log.info('Checando conexão com a Internet')
    uiLogin.lblStatus.setText("Checando conexão com a Internet")

    conexao = checkInternetAccess()
    #conexao = True

    if conexao:    
    
        log.info('Checando licença no servidor - Por favor aguarde')
        uiLogin.lblStatus.setText("Conectando com o servidor")
        
        login = {'user':utils.encrypt(uiLogin.txtEmail.text()), 'passwd':utils.encrypt(uiLogin.txtPasswd.text()), 'token':utils.encrypt(token)}
        #log.info('token: {}'.format(token))
        
        statusLicence, error  = checkLoginPv(login) 
        #statusLicence = True ## testando apenas IJF
        
        if statusLicence:
            
            log.debug("Usuario logado")
            init_video = True 
            initWatchDog()
            windowLogin.close()
        
        else:

            #se o servidor estiver fora do ar - libera acesso ao sistema 
            if error == "conexao":
                log.warning("Erro de conexão com o servidor")

                init_video = True
                statusLicence = True
                log.warning("Liberando acesso")
                windowLogin.close()

            elif error == "login":

                init_video = False
                log.warning("Usuario invalido")
                uiLogin.lblStatus.setText("Usuário ou senha inválida. Tente novamente")

    else:

        log.info("Erro de conexao com a Internet")
        uiLogin.lblStatus.setText("Cheque sua conexão com a Internet por favor e tente mais tarde")
        


#---------------- gui  tab configuração geral -------------------

def clearListCameras():
    global ui

    ui.comboBoxCamAtivas.clear()
    ui.comboBoxCamEncontradas.clear()
    
    ui.txtUserCamDisponivel.clear()
    ui.txtPasswdCamDisponivel.clear()
    ui.txtPortaCamDisponivel.clear()
    ui.txtCanalCamDiponivel.clear()
    ui.lblStatusTestarCam.clear()


def clearFieldsTabGeralEmail():
    global ui

    ui.txtEmailName.clear()
    ui.txtEmailPort.clear()
    ui.txtEmailSmtp.clear()
    ui.txtEmailSubject.clear()
    ui.txtEmailTo.clear()
    ui.txtEmailUser.clear()
    ui.txtEmailPassword.clear()
    ui.lblStatus.clear()
    ui.lblStatusProcurarCam.clear()
    


def btnSaveEmail():
    global ui

    statusFields = True 
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Campo em branco")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    #checando campos em branco

    if len(ui.txtEmailName.text()) == 0:
        msg.setText("Campo 'Nome' em branco")
        msg.exec()
        ui.txtEmailNome.setFocus()
        statusFields = False

    elif len(ui.txtEmailPort.text()) == 0:
        msg.setText("Campo 'Porta' em branco")
        msg.exec()
        ui.txtEmailPort.setFocus()
        statusFields = False

    elif len(ui.txtEmailSmtp.text()) == 0:
        msg.setText("Campo 'SMTP' em branco")
        msg.exec()
        ui.txtEmailSmtp.setFocus()
        statusFields = False

    elif len(ui.txtEmailUser.text()) == 0:
        msg.setText("Campo 'Usuário' em branco")
        msg.exec()
        ui.txtEmailUser.setFocus()
        statusFields = False

    elif len(ui.txtEmailPassword.text()) == 0:
        msg.setText("Campo 'Senha' em branco")
        msg.exec()
        ui.txtEmailPassword.setFocus()
        statusFields = False

    elif len(ui.txtEmailSubject.text()) == 0:
        msg.setText("Campo 'Assunto' em branco")
        msg.exec()
        ui.txtEmailSubject.setFocus()
        statusFields = False

    elif len(ui.txtEmailTo.text()) == 0:
        msg.setText("Campo 'Destinatários' em branco")
        msg.exec()
        ui.txtEmailTo.setFocus()
        statusFields = False


    elif  ui.checkBoxVideoRecordingAllTime.isChecked() and len(ui.txtDirRecordingAllTime.text()) ==  0:
        msg.setText("Campo 'Diretório de gravação 24h' em branco")
        msg.exec()
        ui.txtDirRecordingAllTime.setFocus()
        statusFields = False


    elif  ui.checkBoxVideoRecordingOnAlarmes.isChecked() and len(ui.txtDirRecordingOnAlarmes.text()) ==  0:
        msg.setText("Campo 'Diretório de gravação de Alarmes' em branco")
        msg.exec()
        ui.txtDirRecordingOnAlarmes.setFocus()
        statusFields = False



    elif  ui.checkBoxWebCam.isChecked() and len(ui.txtUrlRstp.text()) > 0:
        msg.setText("Escolha somente 'Capturar da Webcam' ou 'Câmera RSTP'")
        msg.exec()
        ui.txtUrlRstp.setFocus()
        statusFields = False


    if statusFields:
        camSource = "webcam" if ui.checkBoxWebCam.isChecked() else ui.txtUrlRstp.text()
        isRecordingAllTime = "True" if ui.checkBoxVideoRecordingAllTime.isChecked() else "False"
        isRecordingOnAlarmes = "True" if ui.checkBoxVideoRecordingOnAlarmes.isChecked() else "False"

         
        passwd = utils.encrypt(ui.txtEmailPassword.text())

        statusConfig.addConfigGeral(ui.txtEmailName.text(),
                              ui.txtEmailPort.text(),
                              ui.txtEmailSmtp.text(),
                              ui.txtEmailUser.text(),
                              passwd,
                              ui.txtEmailSubject.text(),
                              ui.txtEmailTo.text(),
                              isRecordingAllTime,
                              isRecordingOnAlarmes,
                              ui.txtDirRecordingAllTime.text(),
                              ui.txtDirRecordingOnAlarmes.text(),
                              camSource, 
                              ui.txtAvisoUtilizacaoHD.text())


        refreshStatusConfig()
        clearFieldsTabGeralEmail()
        fillTabGeral()

        initConfig()




def fillTabGeral():

    global emailConfig, statusConfig

    clearFieldsTabGeralEmail()
    
    clearListCameras()

    refreshStatusConfig()

    ui.checkBoxDesabilitarLoginAutomatico.setCheckState( True if statusConfig.getLoginAutomatico() == "True" else False )


    ui.checkBoxVideoRecordingOnAlarmes.setCheckState( True if statusConfig.data.get("isRecordingOnAlarmes") == "True" else False )

    ui.checkBoxVideoRecordingAllTime.setCheckState( True if statusConfig.data.get("isRecordingAllTime") == "True" else False )

    if statusConfig.data.get("camSource") == "webcam":
        ui.txtUrlRstp.clear()
    else:
        ui.txtUrlRstp.setText(statusConfig.data.get("camSource"))

    ui.txtDirRecordingAllTime.setText(statusConfig.data.get("dirVideosAllTime"))
    ui.txtDirRecordingOnAlarmes.setText(statusConfig.data.get("dirVideosOnAlarmes"))
    ui.txtAvisoUtilizacaoHD.setText(statusConfig.data["storageConfig"].get("diskMinUsage"))
    ui.txtEmailName.setText(statusConfig.data["emailConfig"].get('name'))
    ui.txtEmailPort.setText(statusConfig.data["emailConfig"].get('port'))
    ui.txtEmailSmtp.setText(statusConfig.data["emailConfig"].get('smtp'))
    ui.txtEmailUser.setText(statusConfig.data["emailConfig"].get('user'))

    passwdEmail = utils.decrypt(statusConfig.data["emailConfig"].get('password')) 

    ui.txtEmailPassword.setText(passwdEmail)
    
    if passwdEmail == 'error':
        ui.lblStatus.setText('Cheque se sua senha do email está cadastrada corretamente')
        ui.txtEmailPassword.setFocus()
    
    ui.txtEmailSubject.setText(statusConfig.data["emailConfig"].get('subject'))
    ui.txtEmailTo.setText(statusConfig.data["emailConfig"].get('to'))

    #carregar cams previamente escaneadas na rede

    for cam in listCamAtivas:
        if cam.get('emUso') == 'True':
            ui.comboBoxCamAtivas.addItem('[' + cam.get('id') + ']:' + cam.get('ip') + ' : ' + cam.get('port') + ' [em uso]')
        else:
            ui.comboBoxCamAtivas.addItem('[' + cam.get('id') + ']:' + cam.get('ip') + ' : ' + cam.get('port'))

    for cam in listCamEncontradas:
        ui.comboBoxCamEncontradas.addItem('[' + cam.get('id') + ']:' + cam.get('ip') + ' : ' + cam.get('port'))
    
    
    #configuracoes de armazenamento
    if spaceMaxDirVideosAllTime == 0:
        
        ui.txtDefinirMaximoAllTime.setText('0')
        ui.txtDefinirMaximoAllTime.setEnabled(False)
        ui.checkBoxNoLimitsVideosAllTime.setChecked(True)

    else: 
        ui.txtDefinirMaximoAllTime.setText(str(spaceMaxDirVideosAllTime))
        ui.txtDefinirMaximoAllTime.setEnabled(True)
    
    if spaceMaxDirVideosOnAlarme == 0: 

        ui.txtDefinirMaximoOnAlarmes.setText('0')
        ui.txtDefinirMaximoOnAlarmes.setEnabled(False)
        ui.checkBoxNoLimitsVideosOnAlarmes.setChecked(True)
    else:
        ui.txtDefinirMaximoOnAlarmes.setEnabled(True)
        ui.txtDefinirMaximoOnAlarmes.setText(str(spaceMaxDirVideosOnAlarme))
        ui.checkBoxNoLimitsVideosOnAlarmes.setChecked(False)
    
    
    ui.radioButtonStopSaveNewVideos.setChecked(stopSaveNewVideos)
    ui.radioButtonDeleteOldestFiles.setChecked(eraseOldestFiles)
    ui.progressBarDisponivelHD.setValue(utils.getDiskUsageFree())
    ui.txtAvailableHD.setText('{:03.2f}'.format((utils.getDiskUsageFreeGb())))
    ui.txtDirUsedVideosAllTime.setText('{:03.2f}'.format(utils.getDirUsedSpace(statusConfig.data["dirVideosAllTime"])))
    ui.txtDirUsedVideosOnAlarmes.setText('{:03.2f}'.format(utils.getDirUsedSpace(statusConfig.data["dirVideosOnAlarmes"])))

    ui.txtDiasEstimado.setText('{:d}'.format((utils.getNumDaysRecording())) + ' dias' )

    


#---------------- gui tab modelos de deteccao -------------------

#def clearFieldsTabConfigDetection():
#    ui.txtModelName.clear()
#    ui.txtModelBin.clear()
#    ui.txtModelXml.clear()
#    ui.comboListModels.clear()


#def btnCancelOpenVino():
#    ui.btnCancelOpenVino.setEnabled(False)
#    ui.btnDeleteOpenVino.setEnabled(True)
#    clearFieldsTabConfigDetection()
#    comboListModelsUpdate(0)

#def btnDeleteOpenVino():
#
#    msg = QMessageBox()
#    msg.setIcon(QMessageBox.Information)
#    msg.setWindowTitle("Sem modelo ativo")
#    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
#
#    if len(statusConfig.data.get('openVinoModels')) > 0:
#        if not statusConfig.deleteModel(ui.comboListModels.currentText()):
#            msg.setText("Ao menos um modelo deve estar cadastrado e estar ativo. Adicione/altere algum modelo como 'Ativo' antes de delete-lo")
#            msg.exec()
#        else:
#            refreshStatusConfig()
#            comboListModelsUpdate(0)

#def btnNewModel():
#    clearFieldsTabConfigDetection()
#    ui.txtModelName.setFocus()
#    ui.btnCancelOpenVino.setEnabled(True)
#    ui.btnDeleteOpenVino.setEnabled(False)

#def btnSaveOpenVino():
#
#    statusFields = True
#    msg = QMessageBox()
#    msg.setIcon(QMessageBox.Information)
#    msg.setWindowTitle("Campo em branco")
#    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
#
#    #checando campos em branco
#
#    if len(ui.txtModelName.text()) == 0:
#        msg.setText("Campo 'Nome' em branco")
#        msg.exec()
#        ui.txtModelName.setFocus()
#        statusFields = False
#
#    elif len(ui.txtModelBin.text()) == 0:
#        msg.setText("Campo 'Arquivo .bin' em branco")
#        msg.exec()
#        ui.txtModelBin.setFocus()
#        statusFields = False
#
#    elif len(ui.txtModelXml.text()) == 0:
#        msg.setText("Campo 'Arquivo .xml' em branco")
#        msg.exec()
#        ui.txtModelXml.setFocus()
#        statusFields = False
#    
#    elif len(ui.txtCpuExtension.text()) == 0:
#        msg.setText("Campo 'CPU Extensions' em branco")
#        msg.exec()
#        ui.txtCpuExtension.setFocus()
#        statusFields = False
#    
#    elif len(ui.txtPluginDir.text()) == 0:
#        msg.setText("Campo 'Plugin Diretorio' em branco")
#        msg.exec()
#        ui.txtPluginDir.setFocus()
#        statusFields = False
#
#    elif not statusConfig.checkActiveModel() and len(statusConfig.data.get('openVinoModels')) == 1:
#        statusFields = False
#        msg.setText("Ao menos 1 modelo deve estar ativo. Marque a opção 'Ativo'")
#        msg.exec()
#
#    #elif statusConfig.checkActiveModel() and len(statusConfig.data.get('openVinoModels')) > 1 and ui.checkBoxActiveModel.isChecked():
#    #    statusFields = False
#    #    msg.setText("Já existe um modelo 'Ativo', desmarque a opção 'Ativo' antes de salvar")
#    #    msg.exec()
#
#    deviceTxt = "CPU"
#    if ui.comboListDevices.currentIndex() == 0:
#        deviceTxt = "CPU"
#    elif ui.comboListDevices.currentIndex() == 1:
#        deviceTxt = "GPU"
#    elif ui.comboListDevices.currentIndex() == 2:
#        deviceTxt = "MYRIAD"
#
#
#    if statusFields:
#
#        statusConfig.addOpenVinoModels("True" if ui.checkBoxActiveModel.isChecked() else "False",
#                                   ui.txtModelName.text(),
#                                   ui.txtModelXml.text(),
#                                   ui.txtModelBin.text(),
#                                   ui.txtCpuExtension.text(),
#                                   ui.txtPluginDir.text(),
#                                   deviceTxt)
#        refreshStatusConfig()
#        comboListModelsUpdate(ui.comboListModels.currentIndex())
#        ui.btnCancelOpenVino.setEnabled(False)
#        ui.btnDeleteOpenVino.setEnabled(True)


#def comboListModelsUpdate(i):
#
#   # clearFieldsTabConfigDetection()
#
#    if len(statusConfig.data.get('openVinoModels')) > 0:
#        for m in statusConfig.data.get('openVinoModels'):
#            ui.comboListModels.addItem(m.get('name'))
#
#        ui.comboListModels.setCurrentIndex(i)
#
#        m = statusConfig.data.get('openVinoModels')[i]
#
#        ui.checkBoxActiveModel.setCheckState(True if m.get('isActive') == "True" else False)
#        ui.txtModelName.setText(m.get('name'))
#        ui.txtModelBin.setText(m.get('openVinoModelBin'))
#        ui.txtModelXml.setText(m.get('openVinoModelXml'))
#        ui.txtCpuExtension.setText(statusConfig.getCpuExtension())
#        ui.txtPluginDir.setText(statusConfig.getPluginDir())
#        ui.txtModelName.setText(m.get('name'))
#
#        if m.get('openVinoDevice') == 'CPU':
#            ui.comboListDevices.setCurrentIndex(0)
#        elif m.get('openVinoDevice')  == 'GPU':
#            ui.comboListDevices.setCurrentIndex(1)
#        elif m.get('openVinoDevice') == 'MYRIAD':
#            ui.comboListDevices.setCurrentIndex(2)




#---------------- gui  tab adicionar regiao -------------------

def refreshStatusConfig():
    global statusConfig, regions, emailConfig
    statusConfig = utils.StatusConfig()
    regions = statusConfig.getRegions()
    emailConfig = statusConfig.getEmailConfig()


def btnCancelRegion():
    if len(regions) > 0:
        ui.btnDeleteRegion.setEnabled(True)
    else:
        ui.btnDeleteRegion.setEnabled(False)

    ui.btnNewRegion.setEnabled(True)
    ui.btnNewAlarm.setEnabled(True)
    #ui.btnSaveRegion.setEnabled(False)
    ui.btnCancelRegion.setEnabled(False)
    clearFieldsTabRegiao()
    comboRegionsUpdate(0)

    global portaoVirtualSelecionado, portaoVirtualSelecionado, cropPolygon
    portaoVirtualSelecionado = True
    portaoVirtualSelecionado = True
    ref_point_polygon.clear()
    cropPolygon = False


def clearFieldsTabRegiao():
    ui.txtRegionName.clear()
    ui.txtNameAlarm.clear()
    ui.txtThreshold.clear()
    ui.comboAlarms.clear()
    ui.comboRegions.clear()
    #ui.checkEmailAlert.setCheckState(False)
    #ui.checkAlertSound.setCheckState(False)
    ui.checkPerson.setCheckState(False)
    ui.checkBike.setCheckState(False)
    ui.checkCar.setCheckState(False)
    ui.checkDog.setCheckState(False)
    ui.checkMon.setCheckState(False)
    ui.checkTue.setCheckState(False)
    ui.checkWed.setCheckState(False)
    ui.checkThur.setCheckState(False)
    ui.checkFri.setCheckState(False)
    ui.checkSat.setCheckState(False)
    ui.checkSun.setCheckState(False)
    ui.timeEnd.clear()
    ui.timeStart.clear()

def btnCancelAlarm():
    ui.btnDeleteAlarm.setEnabled(True)
    ui.btnCancelAlarm.setEnabled(False)
    ui.btnNewAlarm.setEnabled(True)
    ui.comboAlarms.setEnabled(True)
    comboRegionsUpdate(ui.comboRegions.currentIndex())

def btnNewRegion():
    global portaoVirtualSelecionado, ref_point_polygon

    portaoVirtualSelecionado = False
    ref_point_polygon.clear()

    #clear fields
    clearFieldsTabRegiao()
    #ui.comboRegions.clear()
    ui.btnCancelRegion.setEnabled(True)
    ui.btnDeleteRegion.setEnabled(False)
    ui.btnSaveRegion.setEnabled(True)
    ui.btnDeleteAlarm.setEnabled(False)
    ui.btnCancelAlarm.setEnabled(False)
    ui.btnSaveAlarm.setEnabled(False)

def btnSaveRegion():
    statusFields = True
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Campo em branco")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    global ref_point_polygon, portaoVirtualSelecionado, cropPolygon

    #checando campos em branco

    if len(ui.txtRegionName.text()) == 0:
        msg.setText("Campo 'Nome da Região' em branco")
        msg.exec()
        ui.txtRegionName.setFocus()
        statusFields = False

    elif len(ui.txtThreshold.text()) == 0:
        msg.setText("Campo 'Acurácia' em branco")
        msg.exec()
        ui.txtThreshold.setFocus()
        statusFields = False

    elif len(ui.txtNameAlarm.text()) == 0:
        msg.setText("Campo 'Nome do Alarme' em branco")
        msg.exec()
        ui.txtNameAlarm.setFocus()
        statusFields = False

    elif len(ref_point_polygon) == 0 and not statusConfig.checkNameRegion(ui.txtRegionName.text()):
        msg.setText("Região não selecionada! manter tecla CTRL pressionada até selecionar todos os pontos desejados")
        msg.exec()
        portaoVirtualSelecionado = False


    points = []

    t = {'start':{'hour':ui.timeStart.time().hour(), 'min':ui.timeStart.time().minute()},
         'end':{'hour':ui.timeEnd.time().hour(), 'min':ui.timeEnd.time().minute()}}

    days = {'mon':'True' if ui.checkMon.isChecked() else 'False',
            'tue':'True' if ui.checkTue.isChecked() else 'False',
            'wed':'True' if ui.checkWed.isChecked() else 'False',
            'thu':'True' if ui.checkThur.isChecked() else 'False',
            'fri':'True' if ui.checkFri.isChecked() else 'False',
            'sat':'True' if ui.checkSat.isChecked() else 'False',
            'sun':'True' if ui.checkSun.isChecked() else 'False'
           }
    newAlarm = [{"name":ui.txtNameAlarm.displayText(), 'time':t, 'days':days, 
                 'isEmailAlert':'True' if ui.checkEmailAlert.isChecked() else 'False',
                 'isSoundAlert':'True' if ui.checkAlertSound.isChecked() else 'False'
                }]

    objectType = {'person':'True' if ui.checkPerson.isChecked() else 'False',
                  'car':'True' if ui.checkCar.isChecked() else 'False',
                  'bike':'True' if ui.checkBike.isChecked() else 'False',
                  'dog':'True' if ui.checkDog.isChecked() else 'False'}


    if statusFields:

        if len(ref_point_polygon) == 0 and statusConfig.checkNameRegion(ui.txtRegionName.text()):
            points = statusConfig.getRegion(ui.txtRegionName.text()).get('pointsPolygon')

        else:
            points = ref_point_polygon

        statusConfig.addRegion(ui.txtRegionName.displayText(),
                               newAlarm, objectType, round(float(ui.txtThreshold.displayText()),2), points )
        refreshStatusConfig()
        comboRegionsUpdate(ui.comboRegions.currentIndex())
        comboAlarmsUpdate(0)
        #ui.btnSaveRegion.setEnabled(False)
        ui.btnCancelRegion.setEnabled(False)

        portaoVirtualSelecionado = True
        ref_point_polygon.clear()
        cropPolygon = False

def btnSaveAlarm():
    statusFields = True
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Campo em branco")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    #checando campos em branco

    if len(ui.txtNameAlarm.text()) == 0:
        msg.setText("Campo 'Nome do Alarme' em branco")
        msg.exec()
        ui.txtNameAlarm.setFocus()
        statusFields = False

    if statusFields:

        t = {'start':{'hour':ui.timeStart.time().hour(), 'min':ui.timeStart.time().minute()},
             'end':{'hour':ui.timeEnd.time().hour(), 'min':ui.timeEnd.time().minute()}}
        days = {'mon':'True' if ui.checkMon.isChecked() else 'False',
                'tue':'True' if ui.checkTue.isChecked() else 'False',
                'wed':'True' if ui.checkWed.isChecked() else 'False',
                'thu':'True' if ui.checkThur.isChecked() else 'False',
                'fri':'True' if ui.checkFri.isChecked() else 'False',
                'sat':'True' if ui.checkSat.isChecked() else 'False',
                'sun':'True' if ui.checkSun.isChecked() else 'False'
               }
        a = {"name":ui.txtNameAlarm.displayText(), 'time':t, 'days':days, 
                     'isEmailAlert':'True' if ui.checkEmailAlert.isChecked() else 'False',
                     'isSoundAlert':'True' if ui.checkAlertSound.isChecked() else 'False'
                    }
        statusConfig.addAlarm(ui.comboRegions.currentIndex(), a)
        refreshStatusConfig()

        comboRegionsUpdate(ui.comboRegions.currentIndex())
        ui.btnSaveAlarm.setEnabled(True)
        ui.btnDeleteAlarm.setEnabled(False)
        ui.btnCancelAlarm.setEnabled(False)
        ui.btnNewAlarm.setEnabled(True)
        ui.comboAlarms.setEnabled(True)


def btnDeleteAlarm():
    global statusConfig, ui

    statusConfig.deleteAlarm(ui.comboRegions.currentText(), ui.comboAlarms.currentText())
    refreshStatusConfig()
    comboRegionsUpdate(0)
    comboAlarmsUpdate(0)


def btnDeleteRegion():
    global statusConfig, ui

    statusConfig.deleteRegion(ui.comboRegions.currentText())
    refreshStatusConfig()
    comboRegionsUpdate(0)
    comboAlarmsUpdate(0)



def fillComboAlarm(regionId):

    #preenchendo lista de alarmes
    if not statusConfig.isAlarmEmpty(regionId):
        for a in regions[regionId].get('alarm'):
            ui.comboAlarms.addItem(a.get('name'))


def comboBoxCamAtivasUpdate(i):
    global ui




def comboRegionsUpdate(i):
    global ui

    clearFieldsTabRegiao()
    #r = regions[i]

    ui.comboAlarms.clear()

    if not statusConfig.isRegionsEmpty():
        for r in regions:
            ui.comboRegions.addItem(r.get("nameRegion"))

        r = regions[i]
        ui.txtRegionName.insert(r.get('nameRegion'))
        ui.txtThreshold.insert(str(r.get('prob_threshold')))
        #ui.checkEmailAlert.setCheckState(r.get('isEmailAlert')=="True")
        #ui.checkAlertSound.setCheckState(r.get('isSoundAlert')=="True")
        ui.checkPerson.setCheckState(r.get('objectType').get('person')=="True")
        ui.checkCar.setCheckState(r.get('objectType').get('car')=="True")
        ui.checkBike.setCheckState(r.get('objectType').get('bike')=="True")
        ui.checkDog.setCheckState(r.get('objectType').get('dog')=="True")

        if not statusConfig.isAlarmEmpty(i):
            fillComboAlarm(i)
            #comboAlarmsUpdate(0)
            #ui.comboAlarms.setCurrentIndex(0)

        ui.comboRegions.setCurrentIndex(i)
        comboAlarmsUpdate(0)
        ui.btnDeleteRegion.setEnabled(True)
        ui.btnCancelRegion.setEnabled(False)



def clearFieldsAlarm():
    ui.checkMon.setCheckState(False)
    ui.checkTue.setCheckState(False)
    ui.checkWed.setCheckState(False)
    ui.checkThur.setCheckState(False)
    ui.checkFri.setCheckState(False)
    ui.checkSat.setCheckState(False)
    ui.checkSun.setCheckState(False)
    ui.checkEmailAlert.setCheckState(False)
    ui.checkAlertSound.setCheckState(False)
    ui.timeStart.clear()
    ui.timeEnd.clear()
    ui.txtNameAlarm.clear()
    #ui.comboAlarms.clear()

def btnNewAlarm():
    clearFieldsAlarm()
    ui.btnSaveAlarm.setEnabled(True)
    ui.btnDeleteAlarm.setEnabled(False)
    ui.btnCancelAlarm.setEnabled(True)
    ui.comboAlarms.setEnabled(False)

def comboAlarmsUpdate(i):
    clearFieldsAlarm()

    #preenchendo lista de alarmes
    if not statusConfig.isAlarmEmpty(ui.comboRegions.currentText()) and not statusConfig.isRegionsEmpty():

        ui.btnDeleteAlarm.setEnabled(True)
        a = regions[ui.comboRegions.currentIndex()].get('alarm')[i]
        ui.checkMon.setCheckState(a.get('days').get('mon') == 'True')
        ui.checkTue.setCheckState(a.get('days').get('tue') == 'True')
        ui.checkWed.setCheckState(a.get('days').get('wed') == 'True')
        ui.checkThur.setCheckState(a.get('days').get('thu') == 'True')
        ui.checkFri.setCheckState(a.get('days').get('fri') == 'True')
        ui.checkSat.setCheckState(a.get('days').get('sat') == 'True')
        ui.checkSun.setCheckState(a.get('days').get('sun') == 'True')
        ui.checkEmailAlert.setCheckState(a.get('isEmailAlert') == 'True')
        ui.checkAlertSound.setCheckState(a.get('isSoundAlert') == 'True')
        ui.txtNameAlarm.insert(a.get('name'))
        ui.comboAlarms.setCurrentIndex(i)

        tStart = QTime(int(a.get('time').get('start').get('hour')), int(a.get('time').get('start').get('min')))
        ui.timeStart.setTime(tStart)

        tEnd = QTime(int(a.get('time').get('end').get('hour')),int(a.get('time').get('end').get('min')))
        ui.timeEnd.setTime(tEnd)

    else:
       ui.btnDeleteAlarm.setEnabled(False)



#---------------- gui -------------------
def callbackButton1min(self, ret):
    global tSoundLimit, tSoundStart
    tSoundLimit = tSoundLimit + 60
    tSoundStart = time.time()

def callbackButton30min(self, ret):
    global tSoundLimit, tSoundStart
    tSoundLimit = tSoundLimit + 1800
    tSoundStart = time.time()

def callbackButtonResumeSound(self, ret):
    global tSoundLimit, tSoundStart, stopSound
    tSoundLimit = 0
    tSoundStart = 0
    tSoundEnd = 0
    tSound = 0
    stopSound = False


#def checkBoxVideoRecordingStateChanged(state):
#    if state == 0:
#       ui.checkBoxVideoRecordingOnAlarmes.setCheckState(True)
#    # Qt.Checked 
#    elif (state == 1 or state == 2):
#        ui.checkBoxVideoRecordingOnAlarmes.setCheckState(False)
#
#
#
#def checkBoxVideoRecordingOnAlarmesStateChanged(state):
#    if state == 0:
#       ui.checkBoxVideoRecording.setCheckState(True)
#    # Qt.Checked 
#    elif (state == 1 or state == 2):
#        ui.checkBoxVideoRecording.setCheckState(False)
#        #ui.txtUrlRstp.setEnabled(False)




def checkBoxLoginAutoStart(state):
    global statusConfig

    statusConfig = utils.StatusConfig()

    if OS_PLATFORM == 'windows':
        ATALHO_PATH = 'PortaoVirtual.lnk'
        USER_NAME = getpass.getuser()       
        ROOT_PATH = os.path.splitdrive(os.environ['WINDIR'])[0]    
        AUTO_START_PATH = ROOT_PATH + '/Users/' + USER_NAME + '/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup' 
       
    
    if state == 0:
        
        log.info('Auto start login off')
        statusConfig.setLoginAutoStart('False')
        
        if os.path.exists(AUTO_START_PATH + '/' + ATALHO_PATH):
            os.remove(AUTO_START_PATH + '/' + ATALHO_PATH)
        else:
            log.info("Atalho na pasta de Inicialização do sistema não existe")

    elif (state == 1 or state == 2):
        
        log.info('Auto start login On')
        statusConfig.setLoginAutoStart('True')  
        
        if not os.path.exists(AUTO_START_PATH + '/' + ATALHO_PATH):              
            shutil.copy2(ATALHO_PATH, AUTO_START_PATH) # complete target filename given
        

def checkBoxLoginAutomatico(state):
    global LOGIN_AUTOMATICO, statusConfig

    statusConfig = utils.StatusConfig()
    
    if state == 0:
        
        log.info('Login automatico off')
        statusConfig.setLoginAutomatico('False')
        LOGIN_AUTOMATICO = False


    elif (state == 1 or state == 2):
        
        log.info('Login automatico on')
        statusConfig.setLoginAutomatico('True')
        LOGIN_AUTOMATICO = True 
        

def checkBoxDesabilitarLoginAutomatico(state):
    global LOGIN_AUTOMATICO, statusConfig

    statusConfig = utils.StatusConfig()
    
    if state == 0:
        
        log.info('Login automatico off')
        statusConfig.setLoginAutomatico('False')
        LOGIN_AUTOMATICO = False


    elif (state == 1 or state == 2):
        
        log.info('Login automatico on')
        statusConfig.setLoginAutomatico('True')
        LOGIN_AUTOMATICO = True 



def checkBoxSalvarLogin(state):
    global fernetKey, statusConfig

    statusConfig = utils.StatusConfig()
    
    if state == 0:
        
        log.info('salvar login off')
        statusConfig.addLoginConfig(uiLogin.txtEmail.text(),
                                    '',
                                    'False',
                                    statusConfig.dataLogin['loginAutomatico'],
                                    statusConfig.dataLogin['autoStart']
                                    )
        log.info('Salvar Login desligado')

    elif (state == 1 or state == 2):
        

        passEncrypted = utils.encrypt(uiLogin.txtPasswd.text())        
        
        statusConfig.addLoginConfig(uiLogin.txtEmail.text(),
                                    passEncrypted,
                                    'True',
                                    statusConfig.dataLogin['loginAutomatico'],
                                    statusConfig.dataLogin['autoStart'])
        
        log.info('Salvar Login ligado')



def checkBoxWebcamStateChanged(state):
    if state == 0:
       ui.txtUrlRstp.setEnabled(True)
    # Qt.Checked 
    elif (state == 1 or state == 2):
        ui.txtUrlRstp.clear()
        ui.txtUrlRstp.setEnabled(False)

def checkBoxNoLimitsVideosAllTime(state):
    if state == 0:
       ui.txtDefinirMaximoAllTime.setEnabled(True)
    # Qt.Checked 
    elif (state == 1 or state == 2):
        ui.txtDefinirMaximoAllTime.setText('0')
        ui.txtDefinirMaximoAllTime.setEnabled(False)


def checkBoxNoLimitsVideosOnAlarmes(state):
    if state == 0:
       ui.txtDefinirMaximoOnAlarmes.setEnabled(True)
    # Qt.Checked 
    elif (state == 1 or state == 2):
        ui.txtDefinirMaximoOnAlarmes.setText('0') #zero significa sem limites de utilizacao do disco
        ui.txtDefinirMaximoOnAlarmes.setEnabled(False)


def initFormLogin(self, ret):

    global uiLogin, formLogin, fernetKey 
        
    
    statusConfig = utils.StatusConfig()

    if statusConfig.dataLogin.get('autoStart') == 'True':
        uiLogin.checkBoxLoginAutoStart.setCheckState(True)
    else:
        uiLogin.checkBoxLoginAutoStart.setCheckState(False)
    
    if statusConfig.dataLogin.get('salvarLogin') == 'True':
        
        uiLogin.txtEmail.setText(statusConfig.dataLogin.get('user'))
        
        passwd = utils.decrypt(statusConfig.dataLogin.get('passwd')) 
        
        uiLogin.txtPasswd.setText(passwd)
        uiLogin.checkBoxSalvarLogin.setCheckState(True)

    log.info('Iniciando tela de login')

    uiLogin.btnLogin.clicked.connect(btnLogin)
    uiLogin.btnExit.clicked.connect(btnExit)
    
    
    uiLogin.btnEsqueciSenha.clicked.connect(btnEsqueciSenha)
    uiLogin.checkBoxSalvarLogin.stateChanged.connect(checkBoxSalvarLogin)
    uiLogin.checkBoxLoginAutomatico.stateChanged.connect(checkBoxLoginAutomatico)
    uiLogin.checkBoxLoginAutoStart.stateChanged.connect(checkBoxLoginAutoStart)
    
    uiLogin.btnAlterarSenha.clicked.connect(btnAlterarSenha)

    windowLogin.show()
    app.exec_()

#import shlex

def getProcessId(name):
    for proc in psutil.process_iter():
        if proc.name() == name:            
            log.info('Pid: {:d}'.format(proc.pid))
            log.info('name: {}'.format(proc.name()))
            return proc.pid
    return 0


def killProcessId(name):
    log.debug('killProcessId chamado')
    for proc in psutil.process_iter():
        if proc.name() == name:            
            log.debug('Pid: {:d}'.format(proc.pid))
            log.debug('name: {}'.format(proc.name()))
            proc.kill()
            return True 
    return False 


def initWatchDog():

    DETACHED_PROCESS = 0x00000008
    log.debug('initWatchDog...')

    
    if sys.platform == 'linux':    
        app = os.getcwd() + '/' + 'wd'
    else:
        log.info('Windows WatchDog')
        app = 'wd.exe'

    pid = getProcessId('wd.exe')
    if  pid == 0:
        try: 
            #subprocess.Popen(app, creationflags=DETACHED_PROCESS)
            #cmd = "<full filepath plus arguments of child process>"
            #cmds = shlex.split(app)
            #log.info('cmds: {}'.format(cmds))
            subprocess.Popen(app.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, start_new_session=True, close_fds=True)
            #p = subprocess.Popen(app.split(), shell=False)
            #(output, err) = p.communicate()
            #log.info("Command output: {}".format(output))
            #p_status = p.wait()
            #log.info('p_status: {}'.format(p_status))

        except Exception as e: 
            log.critical('Erro initWatchDog: {}'.format(e))
        else:
            log.debug('WatchDog carregado. PID: {:d}'.format(getProcessId('wd.exe')))
    else:
        log.debug('WatchDog rodando. Pid: {:d}'.format(pid))


def stopWatchDog():
    log.debug('Encerrando Watchdog')

    if sys.platform == 'linux':    
        namePid = 'wd' 
    else:
        namePid = 'wd.exe' 

    pid = getProcessId(namePid) 
    while pid != 0:
        try:
            log.debug('kill name: {}'.format(namePid))

            if OS_PLATFORM == 'linux':
                os.kill(pid, 9)
            else:
                os.system("taskkill /f /im " + namePid)

        except Exception as e:
            log.error('Erro matando processo: {:d}'.format(pid))
            log.error('Error: {}'.format(e))
            killProcessId(namePid)
        else:
            log.debug('WatchDog encerrado. PId: {:d}'.format(pid))

        pid = getProcessId(namePid) 



def callbackButtonRegioes(self, ret):

    # ----------- init tab modelos detecção --------------- 

    #ui.btnSaveOpenVino.setEnabled(True)
    #ui.btnNewModel.setEnabled(True)
    #ui.btnDeleteOpenVino.setEnabled(True)
    #ui.btnCancelOpenVino.setEnabled(False)

    #mostrando o modelo atualmente em uso
    currentIndex = 0

    if len(statusConfig.data.get('openVinoModels')) > 0:
        for m in statusConfig.data.get('openVinoModels'):
            if m.get('isActive') == "False":
                currentIndex = currentIndex + 1
            else:
                break


    # ----------- init tab configuração geral --------------- 

    ui.btnSaveEmail.setEnabled(True)


    fillTabGeral()


    #slots
    ui.btnSaveEmail.clicked.connect(btnSaveEmail)
    ui.btnSaveStorage.clicked.connect(btnSaveStorage)



    ui.btnAtivarCam.clicked.connect(btnAtivarCam)
    ui.btnProcurarCam.clicked.connect(btnProcurarCam)
    ui.btnTestarConfigCam.clicked.connect(btnTestarConfigCam)

    ui.checkBoxWebCam.stateChanged.connect(checkBoxWebcamStateChanged)
    ui.checkBoxDesabilitarLoginAutomatico.stateChanged.connect(checkBoxDesabilitarLoginAutomatico)

   
    ui.checkBoxNoLimitsVideosAllTime.stateChanged.connect(checkBoxNoLimitsVideosAllTime)
    ui.checkBoxNoLimitsVideosOnAlarmes.stateChanged.connect(checkBoxNoLimitsVideosOnAlarmes)
    
    #ui.checkBoxVideoRecordingOnAlarmes.stateChanged.connect(checkBoxVideoRecordingOnAlarmesStateChanged)

    #ui.checkBoxVideoRecording.stateChanged.connect(checkBoxVideoRecordingStateChanged)

    refreshStatusConfig()


    # ----------- init tab adicionar regioes --------------- 
    if not statusConfig.isRegionsEmpty():
        ui.btnDeleteRegion.setEnabled(True)
        ui.btnDeleteAlarm.setEnabled(True)

        for r in regions:
            ui.comboRegions.addItem(r.get("nameRegion"))
        comboRegionsUpdate(ui.comboRegions.currentIndex())
        comboAlarmsUpdate(ui.comboAlarms.currentIndex())
    else:
        ui.btnDeleteRegion.setEnabled(False)
        ui.btnDeleteAlarm.setEnabled(False)

    ui.btnSaveAlarm.setEnabled(True)
    ui.btnCancelRegion.setEnabled(False)
    ui.btnCancelAlarm.setEnabled(False)
    #ui.btnSaveRegion.setEnabled(False)
    ui.btnNewAlarm.setEnabled(True)
    ui.comboAlarms.setEnabled(True)

    #linkando com slots
    ui.comboRegions.activated['int'].connect(comboRegionsUpdate)
    #ui.comboRegions.currentIndexChanged['int'].connect(comboRegionsUpdate)
    ui.comboAlarms.activated['int'].connect(comboAlarmsUpdate)
    ui.btnSaveAlarm.clicked.connect(btnSaveAlarm)
    ui.btnSaveRegion.clicked.connect(btnSaveRegion)
    ui.btnDeleteAlarm.clicked.connect(btnDeleteAlarm)
    ui.btnDeleteRegion.clicked.connect(btnDeleteRegion)
    ui.btnCancelAlarm.clicked.connect(btnCancelAlarm)
    ui.btnCancelRegion.clicked.connect(btnCancelRegion)
    ui.btnNewRegion.clicked.connect(btnNewRegion)
    ui.btnNewAlarm.clicked.connect(btnNewAlarm)

    if ret == 2: 
        log.debug('windowConfig.show()')
        windowConfig.show()
        app.exec_()
    else:
        threadWindow = Thread(target=windowConfig.show())
        threadWindow.start()
    
ret = 1

initConfig()

statusConfig = utils.StatusConfig()

LOGIN_AUTOMATICO = True if statusConfig.getLoginAutomatico() == 'True' else False

if LOGIN_AUTOMATICO:
    log.debug('Iniciando login automatico')

    loginAutomatico()
    initWatchDog() 

else:
    initFormLogin(None, ret)
    #initWatchDog() 

cv.namedWindow('frame', cv.WINDOW_FREERATIO)
cv.setWindowTitle('frame', 'Portão Virtual')
cv.setMouseCallback('frame', polygonSelection)

timeInternetOffStart = None

def initOpenVino():
    global isOpenVino, ret, frame, next_frame, cvNet, nchw, exec_net, input_blob, out_blob
    global device, openVinoModelXml, openVinoModelBin, openVinoCpuExtension, openVinoPluginDir
    global initOpenVinoStatus, init_video, cur_request_id, next_request_id, render_time
    global out_video_all_time, timeSessionInit, timeGravandoAllInit, timeGravandoAll, hora, nameVideoAllTime, dir_video_trigger_all_time, timeInternetOffStart, h, w
    
    ### ---------------  OpenVino Init ----------------- ###
    if isOpenVino:
    
        ret, frame = ipCam.read()
        ret, next_frame = ipCam.read()
        
        #frame = cv.resize(frame, (RES_X, RES_Y)) 
        
        #next_frame = cv.resize(next_frame, (RES_X, RES_Y)) 
    
        cvNet = None
    
        try:
            nchw, exec_net, input_blob, out_blob = pOpenVino.initOpenVino(device, openVinoModelXml, openVinoModelBin, openVinoCpuExtension, openVinoPluginDir)
    
        except:
            log.critical('Erro ao iniciar OpenVino - checar arquivo de configuracao')
            #abrindo janela de configuracao"
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Erro ao abrir mómodulo OpenVino - checar aba de configurações")
            msg.exec()
            callbackButtonRegioes(None, 1)
            initOpenVinoStatus = False
            init_video = False
        else:
            log.info('Openvino carregado')
            log.info(' ')
            cur_request_id = 0
            next_request_id = 1
            render_time = 0
    
    else:
        log.info("TensorFlow on")
        cvNet = cv.dnn.readNetFromTensorflow(pb, pbtxt)
        cvNet = cv.dnn.readNetFromTensorflow(pb, pbtxt)
    
    conectado, frame = ipCam.read()
    if frame is not None:
        #frame = cv.resize(frame, (RES_X, RES_Y)) 
        (h,w) = frame.shape[:2]


    timeSessionInit = time.time()
    timeGravandoAllInit = time.time()
    timeInternetOffStart = time.time()
    
    hora = utils.getDate()['hour'].replace(':','-')
    nameVideoAllTime = dir_video_trigger_all_time + '/' + hora + '.avi'
    
    #primeiro arquivo fica zuado - bug
    #if out_video_all_time is not None: 
    #h = nchw[2]
    #w = nchw[3]
    out_video_all_time = cv.VideoWriter(nameVideoAllTime, fourcc, FPS, (w,h))


if statusLicence and conexao:

    if rtspStatus:

        initOpenVino()
        
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Camera não configurada ou com erro de configuração. Checar configurações de RTSP")
        msg.setWindowTitle("Camera não configurada")
        msg.exec()
        #log.info('qmessageBox rtspStatus: {}'.format(rtspStatus))
        callbackButtonRegioes(None, 2)


while init_video and sessionStatus and rtspStatus :

    #if counter == 0:
    #    startFps = time.time()

    start = time.time()
    #log.info('while')
    

    conectado, frame = ipCam.read()
    #if frame is not None:
    #    frame = cv.resize(frame, (RES_X, RES_Y)) 
    

    if (conectado and frame is not None and next_frame is not None):

        frame_no_label = frame.copy()
        frame_screen = frame.copy()
        frame_no_label_email = frame.copy()

        #objects = ct.update(rects = listObjectsTracking)

        currentData = utils.getDate()
        currentData = [currentData.get('day'), currentData.get('month')]

        if current_data_dir != currentData:
            status_dir_criado_on_alarmes, dir_video_trigger_on_alarmes = utils.createDirectory(statusConfig.data["dirVideosOnAlarmes"])
            status_dir_criado_all_time, dir_video_trigger_all_time = utils.createDirectory(statusConfig.data["dirVideosAllTime"])
            current_data_dir = utils.getDate()
            current_data_dir = [current_data_dir.get('day'), current_data_dir.get('month')]

        #desenhando regioes
        for r in regions:
             pts = np.array(r.get("pointsPolygon"), np.int32)
             pts = pts.reshape((-1,1,2))
             cv.polylines(frame_screen,[pts],True,(0,0,255), 2)

        if cropPolygon:
            #log.info('if cropPolygon')
            pts = np.array(ref_point_polygon, np.int32)
            pts = pts.reshape((-1,1,2))
            cv.polylines(frame_screen,[pts],True,(0,0,255), 2)


        #passando o Frame selecionado do portao para deteccao somente se o portao virtual estiver selecionado
        if portaoVirtualSelecionado and (STOP_ALL == False):

            #se eh openVino e este foi inicializado corretamente 
            if isOpenVino and initOpenVinoStatus:
            ### ---------------  OpenVino Get Objects ----------------- ###

                ret, listReturn  = pOpenVino.getListBoxDetected(ipCam, device, frame, next_frame, nchw, exec_net, out_blob, input_blob, cur_request_id, next_request_id, prob_threshold, RES_X, RES_Y)

                if ret:
                    frame = next_frame
                    frame, next_frAme, cur_request_id, next_request_id, listObjects, listObjectsTracking, prob_threshold_returned  = listReturn[0], listReturn[1], listReturn[2], listReturn[3], listReturn[4], listReturn[5], listReturn[6]

                    cur_request_id, next_request_id = next_request_id, cur_request_id

            else:
                #chamada para a CNN do OpenCV - TensorFlow Object Detection API 
                log.info("CNN via TF Object Detection API")
                listObjects, listObjectTradking  = objectDetection(frame, idObjeto, listRectanglesDetected, detection, rows, cols)


        if len(listObjects) == 0 and portaoVirtualSelecionado:

            tEmptyEnd = time.time()
            tEmpty = tEmptyEnd - tEmptyStart

            if tEmpty > 10:
                #print('tempty > 10')
                gravandoOnAlarmes = False
                newVideo = True
                releaseVideoOnAlarmes = True

        #se tem objetos detectados pela CNN
        else:

            #objectsTracking = ct.update(listObjectsTracking)

            for box in listObjects:

                if portaoVirtualSelecionado:

                    #objetos com ID e centro de massa
                    objectsTracking = ct.update(listObjectsTracking)

                    for (objectID, centroid) in objectsTracking.items():

                        # ajustando posicao do centroid 

                        #desenhando o box e label
                        cv.rectangle(frame_screen, (int(box[0]), int(box[1]) ), (int(box[2]), int(box[3])), (23, 230, 210), thickness=2)
                        top = int (box[1])
                        y = top - 15 if top - 15 > 15 else top + 15
                        cv.putText(frame_screen, str(box[4]), (int(box[0]), int(y)),cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
                        text = "ID {}".format(objectID)
                        cv.putText(frame_screen, text, (centroid[0] - 10, centroid[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv.circle(frame_screen, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)


                        #checando para varias regioes
                        if len(regions) != 0:
                            for r in regions:

                                #checando tipo objeto
                                typeObject = str(box[6])

                                if r.get('objectType').get(typeObject) == "True":

                                    if prob_threshold_returned >= int(r.get('prob_threshold')):

                                        if isIdInsideRegion(centroid, r.get('pointsPolygon')):

                                            tEmptyEnd = time.time()
                                            tEmpty = tEmptyEnd - tEmptyStart

                                            tEmptyStart = time.time()

                                            #enquanto tiver objetos dentro da regiao o video eh gravado, independente do alarme
                                             
                                            if statusConfig.data["isRecordingOnAlarmes"] == 'True':
                                                gravandoOnAlarmes = True

                                            #checando alarmes 
                                            d = utils.getDate()
                                            weekDay = d['weekDay']
                                            minute = int(d['minute'])
                                            hour = int(d['hourOnly'])

                                            currentMinutes = (hour * 60) + minute

                                            for a in r.get('alarm'):

                                                startMinutes = (int(a.get('time').get('start').get('hour'))*60) + int(a.get('time').get('start').get('min'))
                                                endMinutes = (int(a.get('time').get('end').get('hour'))*60) + int(a.get('time').get('end').get('min'))


                                                if a.get('days').get(weekDay) == "True":

                                                    if currentMinutes >= startMinutes and currentMinutes < endMinutes:

                                                        if tSoundLimit > 0:

                                                            tSoundEnd = time.time()
                                                            tSound = tSoundEnd - tSoundStart

                                                            if tSound < tSoundLimit:
                                                                stopSound = True
                                                            else:
                                                                stopSound = False
                                                                tSoundLimit = 0

                                                        if a.get('isSoundAlert') == "True" and not stopSound:
                                                            #evitar campainhas seguidas para mesmo objeto
                                                            if listObjectSoundAlerted.count(objectID) == 0:
                                                                utils.playSound()
                                                                listObjectSoundAlerted.append(objectID)

                                                        if a.get('isEmailAlert') == "True":

                                                            #evitar emails seguidos para mesmo objeto
                                                            if listObjectMailAlerted.count(objectID) == 0:

                                                                log.info('Enviando alerta por email')
                                                                #salvando foto para treinamento
                                                                #crop no box
                                                                #left, top, right, bottom
                                                                #frame_no_label = frame_no_label[int(box[1])-10:int(box[1]) + int(box[3]) , int(box[0])+10:int(box[2])]
                                                                #saveImageBox(frame_no_label, str(box[6]))

                                                                if checkInternetAccess():

                                                                    log.info('Alerta enviado ID[' + str(objectID) + ']')
                                                                    threadEmail = Thread(target=sendMailAlert, args=(emailConfig['name'],
                                                                                                                       emailConfig['to'],
                                                                                                                       emailConfig['subject'],
                                                                                                                       emailConfig['port'],
                                                                                                                       emailConfig['smtp'],
                                                                                                                       emailConfig['user'],
                                                                                                                       frame_no_label_email,
                                                                                                                       str(box[6]),
                                                                                                                       r.get('nameRegion')))
                                                                    threadEmail.start()
                                                                    listObjectMailAlerted.append(objectID)
                                                                else:
                                                                    alertaNaoEnviado = [emailConfig['name'],
                                                                                          emailConfig['to'],
                                                                                          emailConfig['subject'],
                                                                                          emailConfig['port'],
                                                                                          emailConfig['smtp'],
                                                                                          emailConfig['user'],
                                                                                          frame_no_label_email,
                                                                                          str(box[6]),
                                                                                          r.get('nameRegion'), 
                                                                                          objectID]

                                                                    pilhaAlertasNaoEnviados.append(alertaNaoEnviado)
                                                                    
                                                                    listObjectMailAlerted.append(objectID)

                                                                    log.critical('Sem conexao com a Internet - Alarmes serão enviados assim que houver conexao')
                                                                    log.critical('Numero de alarmes não enviados até o momento: {:d}'.format(len(pilhaAlertasNaoEnviados)))
                                            #end loop alarms
                                        else:

                                            tEmptyEnd = time.time()
                                            tEmpty = tEmptyEnd- tEmptyStart

                                            if tEmpty > 10:
                                                gravandoOnAlarmes = False
                                                newVideo = True
                                                releaseVideoOnAlarmes = True
                                                #suspend_screensaver()


                                        #end if isIdInsideRegion

                                    #end if prob_threshold_returned


                            #end loop in Regions
                        #se nao houver regiao configurada, enviar um alarme generico
                        else:
                            log.info('Sem regiao configurada')

                            #evitar emails seguidos para mesmo objeto
                            if listObjectMailAlerted.count(objectID) == 0:
                                log.info('Enviando alerta por email')
                                
                                #60% acuracia padrao 
                                if prob_threshold_returned >= 60:

                                    tEmptyEnd = time.time()
                                    tEmpty = tEmptyEnd - tEmptyStart

                                    tEmptyStart = time.time()

                                    #enquanto tiver objetos dentro da regiao o video eh gravado, independente do alarme
                                     
                                    if statusConfig.data["isRecordingOnAlarmes"] == 'True':
                                        gravandoOnAlarmes = True
                                    

                                    #checando alarmes 
                                    d = utils.getDate()
                                    weekDay = d['weekDay']
                                    #print('weekDay {}'.format(weekDay))
                                    minute = int(d['minute'])
                                    hour = int(d['hourOnly'])

                                    currentMinutes = (hour * 60) + minute
                                    
                                    log.info('Enviando alerta por email')

                                    if checkInternetAccess():

                                        log.info('Alerta enviado ID[' + str(objectID) + ']')
                                        threadEmail = Thread(target=sendMailAlert, args=(emailConfig['name'],
                                                                                           emailConfig['to'],
                                                                                           emailConfig['subject'],
                                                                                           emailConfig['port'],
                                                                                           emailConfig['smtp'],
                                                                                           emailConfig['user'],
                                                                                           frame_no_label_email,
                                                                                           str(box[6]),
                                                                                           'câmera (sem região definida)'))
                                        threadEmail.start()
                                        listObjectMailAlerted.append(objectID)
                                    else:
                                        alertaNaoEnviado = [emailConfig['name'],
                                                              emailConfig['to'],
                                                              emailConfig['subject'],
                                                              emailConfig['port'],
                                                              emailConfig['smtp'],
                                                              emailConfig['user'],
                                                              frame_no_label_email,
                                                              str(box[6]),
                                                              'câmera (sem região definida)', 
                                                              objectID]

                                        pilhaAlertasNaoEnviados.append(alertaNaoEnviado)
                                        
                                        listObjectMailAlerted.append(objectID)

                                        log.critical('Sem conexao com a Internet - Alarmes serão enviados assim que houver conexao')
                                        log.critical('Numero de alarmes não enviados até o momento: {:d}'.format(len(pilhaAlertasNaoEnviados)))




                    #end loop objectTracking.items()
            #end loop for box listObjects

        tEmptyEnd = time.time()
        tEmpty = tEmptyEnd- tEmptyStart
        #print('tEmpty end loop {}'.format(tEmpty))

        timeGravandoAll = time.time() - timeGravandoAllInit
        
        if not utils.isDiskFull(diskMinUsage):

            if spaceMaxDirVideosOnAlarme == 0 or ( spaceMaxDirVideosOnAlarme >= utils.getDirUsedSpace(statusConfig.data["dirVideosOnAlarmes"]) ):

                if newVideo and gravandoOnAlarmes and (STOP_ALL == False):
                
                    if out_video is not None:
                       out_video.release()
                       out_video = None
                       releaseVideoOnAlarmes = False

                    #grava video novo se tiver um objeto novo na cena
                    hora = utils.getDate()['hour'].replace(':','-')
                    nameVideo = dir_video_trigger_on_alarmes + '/' + hora + '.avi'
                    
                    #if out_video is not None:
                    #h = nchw[2]
                    #w = nchw[3]
                    out_video = cv.VideoWriter(nameVideo, fourcc, FPS, (w,h))
                    out_video.write(frame_no_label)
                    newVideo = False

                
                #if gravando:
                if gravandoOnAlarmes and (STOP_ALL == False):
                    if out_video is not None:
                        out_video.write(frame_no_label)

            #espaço maximo na pasta VideosOnAlarmes atingido 
            else:
                #avisar por email 1x a cada X tempo ? 
                if not emailSentFullVideosOnAlarmes:  
                    
                    data = utils.getDate()
                    data_email_sent = data['hour'] + ' - ' + data['day'] + '/' + data['month'] + '/' + data['year']
                    log.critical('Espaço maximo na pasta {} atingido'.format(statusConfig.data["dirVideosOnAlarmes"]))
                    threadEmail = Thread(target=sendMail, args=(

                        'Portao Virtual - Falta de espaço  na pasta "Alarmes"',
                        'Espaço maximo na pasta " {} " atingido. \n\n \
                        Status do armazenamento - {} \n \
                        Espaço livre em disco em %       : {:3d}% \n \
                        Espaço livre em disco em GB      : {:3.2f} GB \n \
                        Espaço utilizado "Video Alarmes" : {:3.2f} GB \n \
                        Espaço utilizado "Video 24hs"    : {:3.2f} GB \n \
                        Número de dias estimados para gravação: {:3d} \n \
                        '.format(statusConfig.data["dirVideosOnAlarmes"], 
                            data_email_sent,
                            utils.getDiskUsageFree(), 
                            utils.getDiskUsageFreeGb(),
                            utils.getDirUsedSpace(statusConfig.data['dirVideosOnAlarmes']),
                            utils.getDirUsedSpace(statusConfig.data['dirVideosAllTime']), 
                            utils.getNumDaysRecording()
                            )) )
                    
                    threadEmail.start()
                    emailSentFullVideosOnAlarmes = True
                    #avisar por email 1x a cada X tempo ? 


            if spaceMaxDirVideosAllTime == 0 or ( spaceMaxDirVideosAllTime >= utils.getDirUsedSpace(statusConfig.data["dirVideosAllTime"]) ):
            
                if gravandoAllTime and (STOP_ALL == False):
                    if out_video_all_time is not None:
                        out_video_all_time.write(frame_no_label)
                
                
                if gravandoAllTime and (timeGravandoAll >= GRAVANDO_TIME) and (STOP_ALL == False):

                    if out_video_all_time is not None:
                         out_video_all_time.release()
                         out_video_all_time = None
                    
                    #if out_video_all_time is not None:
                    
                    hora = utils.getDate()['hour'].replace(':','-')
                    nameVideoAllTime = dir_video_trigger_all_time + '/' + hora + '.avi'
                    
                    #if out_video_all_time is not None:
                    #h = nchw[2]
                    #w = nchw[3]
                    out_video_all_time = cv.VideoWriter(nameVideoAllTime, fourcc, FPS, (w,h))
                    out_video_all_time.write(frame_no_label)

                    timeGravandoAllInit = time.time()
                        

            else:
                
                if not emailSentFullVideosAllTime:  
                    log.critical('Espaço maximo na pasta {} atingido'.format(statusConfig.data["dirVideosAllTime"]))

                    data = utils.getDate()
                    data_email_sent = data['hour'] + ' - ' + data['day'] + '/' + data['month'] + '/' + data['year']
                    threadEmail = Thread(target=sendMail, args=(

                        'Portao Virtual - Falta de espaço  na pasta "Videos 24hs"',
                        'Espaço maximo na pasta " {} " atingido. \n\n \
                        Status do armazenamento - {} \n \
                        Espaço livre em disco em %       : {:3d}% \n \
                        Espaço livre em disco em GB      : {:3.2f}GB \n \
                        Espaço utilizado "Video Alarmes" : {:3.2f}GB \n \
                        Espaço utilizado "Video 24hs"    : {:3.2f}GB \n \
                        Número de dias estimados para gravação: {:3d} \n \
                        '.format(statusConfig.data["dirVideosAllTime"], 
                            data_email_sent,
                            utils.getDiskUsageFree(), 
                            utils.getDiskUsageFreeGb(),
                            utils.getDirUsedSpace(statusConfig.data['dirVideosOnAlarmes']),
                            utils.getDirUsedSpace(statusConfig.data['dirVideosAllTime']), 
                            utils.getNumDaysRecording()
                            )) )

                    threadEmail.start()
                    emailSentFullVideosAllTime = True
                    #avisar por email 1x a cada X tempo ? 

        #disco cheio 
        else:

            if not emailSentDiskFull:  
                if eraseOldestFiles:
                    textEmail = 'Seu HD está cheio, como você configurou o Portão Virtual a deletar \
                            os videos mais antigos, recomendamos que aumente seu espaço em disco \
                            para não perder as gravações realizadas.'

                    threadEmailDiskFull = Thread(target=sendMail, args=('Portao Virtual - seu HD está cheio !', textEmail))
                    threadEmailDiskFull.start()
                    emailSentDiskFull = True
                    log.info('Email de disco cheio enviado - apagando videos antigos ')
                    #avisar por email 1x a cada X tempo ? 
                else:
                    textEmail = 'Seu HD está cheio, como você configurou o Portão Virtual a não \
                            gravar videos novos, recomendamos que aumente seu espaço em disco \
                            para poder novos videos quando ocorrer futuros alarmes.'

                    threadEmailDiskFull = Thread(target=sendMail, args=('Portao Virtual - seu HD está cheio !', textEmail))
                    threadEmailDiskFull.start()
                    emailSentDiskFull = True
                    log.info('Email de disco cheio enviado - interromper novos videos')


            # realmente apaga os videos mais antigos ? 
            if eraseOldestFiles:

                if utils.freeDiskSpace(statusConfig.getDirVideosAllTime()) == False:
                    
                    log.critical('Diretorios de "Videos 24hs" já está vazio')
                    if not emailSentdirVideosAllTimeEmpty:
                        textEmail = 'Mesmo apagando a pasta "Videos 24hs", seu HD continua cheio ! \n\n \ Nossa sugestão é que você libere mais espaço para pode gravar os "Videos 24hs"' 

                        threadEmailAllEmpty = Thread(target=sendMail, args=('Portao Virtual - pasta "Videos 24hs" apagada - seu HD está cheio !',textEmail))
                        threadEmailAllEmpty.start()
                        emailSentdirVideosAllTimeEmpty = True

            
                #se ainda não tiver sido suficiente
                if utils.isDiskFull(diskMinUsage):
                    log.info('Apagando diretórios de Alarmes')
                    #log.info('Dir: {}'.format(statusConfig.getDirVideosOnAlarmes()))
                    if utils.freeDiskSpace(statusConfig.getDirVideosOnAlarmes()) == False:
                        log.critical('Diretorios de "Vidos Alarme" já está vazio')

                        if not emailSentdirVideosOnAlarmesEmpty:
                            textEmail = 'Mesmo apagando a pasta "Videos Alarme", seu HD continua cheio ! \n\n  \
                                     Nossa sugestão é que você libere mais espaço para pode gravar os "Videos Alarme"' 
                                    
                            threadEmailAlarmesEmpty = Thread(target=sendMail, args=('Portao Virtual - pasta "Videos Alarmes" apagada - seu HD está cheio !',textEmail))
                            threadEmailAlarmesEmpty.start()
                            emailSentdirVideosOnAlarmesEmpty = True

            # ou então parar de gravar novos videos
            elif stopSaveNewVideos:
                gravandoAllTime = False
                gravandoOnAlarmes = False


        cv.imshow('frame', frame_screen)

        end = time.time()

        renderTime = (end-start)*1000
        FPS = 1000/renderTime
        #print('render time: {:10.2f} ms'.format(renderTime))
        #print('FPS: {:10.2f} ms'.format(FPS))

        timeSessionEnd = time.time() 
        timeSession = timeSessionEnd - timeSessionInit
        
        #log.info('timeSession: {}'.format(timeSession))

        if timeSession >= CHECK_SESSION:

            session = {login['user'], login['token']}

            conexao = checkInternetAccess()

            if conexao: 

                log.debug('Conexao com a Internet estabelecida')
                STOP_ALL = False

                while (len(pilhaAlertasNaoEnviados) > 0) and (STOP_ALL == False):  
                    #enviando alerta de emails anteriores

                    alertaEmail = pilhaAlertasNaoEnviados.popleft()

                    threadEmail = Thread(target=sendMailAlert, args=(alertaEmail[0],
                    alertaEmail[1],
                    alertaEmail[2],
                    alertaEmail[3],
                    alertaEmail[4],
                    alertaEmail[5],
                    alertaEmail[6],
                    alertaEmail[7],
                    alertaEmail[8]))
                    
                    threadEmail.start()
                    log.debug('Email de alerta durante perda de conexao enviado. pilha: {}'.format(len(pilhaAlertasNaoEnviados)))

                    #listObjectMailAlerted.append(alertaEmail[9])


                #ativar funcoes
                
                sessionStatus, error = checkSessionPv(login)

                timeInternetOffStart = time.time() 

                if error == 'servidorOut':
                    log.critical('Servidor não respondendo. Ignorando checkSession')
                    sessionStatus = True
               
                if sessionStatus == False:
                    log.warning('sessionStatus: {}'.format(sessionStatus))
                    log.warning('stopWatchDog chamado')
                    stopWatchDog()


            else:
                log.critical("Sem internet - sessao não checada")
                log.critical("sessionStatus: {}".format(sessionStatus))
               
                if (time.time() - timeInternetOffStart) >= INTERNET_OFF: 
                    
                    STOP_ALL = True 
                    #release dos videos
                    if out_video is not None:
                       out_video.release()
                       out_video = None
                       releaseVideoOnAlarmes = False
                    
                    if out_video_all_time is not None:
                         out_video_all_time.release()
                         out_video_all_time = None
                         releaseVideoAllTime = False


                    log.critical('Tempo maximo sem Internet permitido esgotado - Portao Virtual ficará inativo')
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Sem conexão com a Internet")
                    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    msg.setText("Tempo maximo de 3 horas sem conexão com a Internet atingido - Portao Virtual ficará inativo, mostrando somente as imagens")
                    msg.exec()
                    #desativar funcoes

                #emitir mensagem de aviso
                sessionStatus = True

            timeSessionInit = time.time()

        
        listObjects.clear()
        #listObjectsTracking.clear()

        #chamando callbackButtonRegioes  
        if cv.waitKey(1) & 0xFF == ord('c'):
            pausaConfig = True
            callbackButtonRegioes(None, ret)
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            stopWatchDog()
            break

    else:
        if not conectado:
            log.warning('Reconectando em 5 segundos...')
            #init_video = False
            time.sleep(5)
            ipCam, error = utils.camSource(source)
            ipCam.set(3, RES_X)
            ipCam.set(4, RES_Y)
            #ipCam = utils.camSource(source)
        else:
            log.warning('Reconectando em 5 segundos...')
            initOpenVino() 
            time.sleep(5)

if out_video is not None:
    log.warning('Fim da captura de video out_video_all_time')
    out_video.release()

if out_video_all_time is not None:
    log.warning('Fim da captura de video out_video_all_time')
    out_video_all_time.release()


if ipCam and cv is not None:
    log.info('ipCam release and cv.destroyAllWindows') 
    ipCam.release()
    cv.destroyAllWindows()



