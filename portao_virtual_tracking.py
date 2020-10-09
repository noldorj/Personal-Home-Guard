import cv2 as cv
import numpy as np
#from datetime import date
import time
from objectTracking.pyimagesearch.centroidtracker import CentroidTracker
from Utils_tracking import sendMailAlert
from Utils_tracking import saveImageBox
import utilsCore as utils
import logging as log
import sys
from threading import Thread
from checkLicence.sendingData import checkLoginPv 
from objectDetectionTensorFlow import objectDetection 
from matplotlib.path import Path
import pluginOpenVino as pOpenVino

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
import sys
from mainForm import *
from formLogin import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QErrorMessage, QMessageBox, QPushButton
from PyQt5.QtCore import QTime, QThread


#import tensorflow as tf

log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)


#variaveis globais

conectado = None
conexao = False
frame = None

#tempo sem objetos detectados
tEmptyStart = time.time()

counter = 0
tEmpty = 0
tEmptyEnd = 0
tEmptyStart = 0
stopSound = False
initOpenVinoStatus = True

#gravando = statusConfig.data["isRecording"] == 'True'
nameVideo  = 'firstVideo'
gravando = False
newVideo = True
releaseVideo = False 
#objects = None
#FPS = ipCam.get(cv.CAP_PROP_FPS) #30.0 #frames per second
FPS = 4  #de acordo com o manual da mibo ic5 intelbras

#primeiro objeto é enviado
listObjectMailAlerted = []
listObjectSoundAlerted = []
listObjectVideoRecorded = []
out_video = None
init_video = False 
statusLicence = False
statusConfig = None
pb = None
pbtxt = None
regions = None
emailConfig = None
portaoVirtualSelecionado = False 
status_dir_criado = None
dir_video_trigger = None
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



#inicializa configuracoes do sistema

def initConfig():

    global statusConfig, pb, pbtxt, regions, emailConfig, portaoVirtualSelecionado
    global status_dir_criado, dir_video_trigger, source, ipCam, prob_threshold, hora, current_data_dir, isOpenVino
    global device, openVinoModelXml, openVinoModelBin, openVinoCpuExtension, openVinoPluginDir, openVinoModelName  
    
    current_data_dir = utils.getDate()
    current_data_dir = [current_data_dir.get('day'), current_data_dir.get('month')]
    hora = utils.getDate()['hour'].replace(':','-')
    
    statusConfig = utils.StatusConfig()
    
    isOpenVino = statusConfig.data["isOpenVino"] == 'True'
    
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
    if len(regions) > 0:
        portaoVirtualSelecionado = True
    
    #Criando diretorio para salvar videos de alarmes
    status_dir_criado, dir_video_trigger = utils.createDirectory(statusConfig.data["dirVideos"])
    
    #origem do stream do video
    source = statusConfig.data["camSource"]
    log.info('source: {}'.format(source))
    ipCam = utils.camSource(source)

    prob_threshold = float(statusConfig.data["prob_threshold"])



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
            print("Existe mais de um modelo 'Ativo'")
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
fourcc = cv.VideoWriter_fourcc(*'XVID')
#fourcc = cv.VideoWriter_fourcc('M','J','P','G')
#cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, FPS, (1280,720))

posConfigPv = 255



#---------------- gui Form Login -------------------
def btnExit():
    global statusLicence, init_video

    log.info('Login Cancelado')
    statusLicence = False
    init_video = False
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



def btnLogin():
    #checando licenca de usuario no servidor
    global init_video, statusLicence, uiLogin, conexao 

    log.info('Checando conexão com a Internet')
    uiLogin.lblStatus.setText("Checando conexão com a Internet")

    conexao = checkInternetAccess()

    if conexao:    
    
        log.info('Checando licença no servidor - Por favor aguarde')
        uiLogin.lblStatus.setText("Conectando com o servidor")
        
        login = {'user':uiLogin.txtEmail.text(), 'passwd':uiLogin.txtPasswd.text(), 'token':'2'}
        
        statusLicence, error  = checkLoginPv(login) 
        statusLicence = True ## testando apenas IJF
        
        if statusLicence:
            
            log.warning("Usuario logado")
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
                uiLogin.lblStatus.setText("Usuário ou senha inválida. Tente novamente")

    else:

        log.info("Erro de conexao com a Internet")
        uiLogin.lblStatus.setText("Cheque sua conexão com a Internet por favor e tente mais tarde")
        conexao = False
        statusLicence = False
        init_video = False


#---------------- gui  tab configuração geral -------------------


def clearFieldsTabGeralEmail():
    ui.txtEmailName.clear()
    ui.txtEmailPort.clear()
    ui.txtEmailSmtp.clear()
    ui.txtEmailSubject.clear()
    ui.txtEmailTo.clear()
    ui.txtEmailUser.clear()
    ui.txtEmailPassword.clear()


def btnSaveEmail():
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

    elif len(ui.txtDirRecording.text()) == 0:
        msg.setText("Campo 'Diretório de gravação' em branco")
        msg.exec()
        ui.txtDirRecording.setFocus()
        statusFields = False

    elif  ui.checkBoxWebCam.isChecked() and len(ui.txtUrlRstp.text()) > 0:
        msg.setText("Escolha somente 'Capturar da Webcam' ou 'Câmera RSTP'")
        msg.exec()
        ui.txtUrlRstp.setFocus()
        statusFields = False


    if statusFields:
        camSource = "webcam" if ui.checkBoxWebCam.isChecked() else ui.txtUrlRstp.text()
        isRecording = "True" if ui.checkBoxVideoRecording.isChecked() else "False"

        statusConfig.addConfigGeral(ui.txtEmailName.text(),
                              ui.txtEmailPort.text(),
                              ui.txtEmailSmtp.text(),
                              ui.txtEmailUser.text(),
                              ui.txtEmailPassword.text(),
                              ui.txtEmailSubject.text(),
                              ui.txtEmailTo.text(),
                              isRecording,
                              ui.txtDirRecording.text(),
                              camSource)


        refreshStatusConfig()
        clearFieldsTabGeralEmail()
        fillTabGeral()



def fillTabGeral():

    global emailConfig, statusConfig

    clearFieldsTabGeralEmail()

    ui.checkBoxVideoRecording.setCheckState( True if statusConfig.data.get("isRecording") == "True" else False )

    if statusConfig.data.get("camSource") == "webcam":
        ui.txtUrlRstp.clear()
    else:
        ui.txtUrlRstp.setText(statusConfig.data.get("camSource"))

    ui.txtDirRecording.setText(statusConfig.data.get("dirVideos"))
    ui.txtEmailName.setText(statusConfig.data["emailConfig"].get('name'))
    ui.txtEmailPort.setText(statusConfig.data["emailConfig"].get('port'))
    ui.txtEmailSmtp.setText(statusConfig.data["emailConfig"].get('smtp'))
    ui.txtEmailUser.setText(statusConfig.data["emailConfig"].get('user'))
    ui.txtEmailPassword.setText(statusConfig.data["emailConfig"].get('password'))
    ui.txtEmailSubject.setText(statusConfig.data["emailConfig"].get('subject'))
    ui.txtEmailTo.setText(statusConfig.data["emailConfig"].get('to'))


#---------------- gui tab modelos de deteccao -------------------

def clearFieldsTabConfigDetection():
    ui.txtModelName.clear()
    ui.txtModelBin.clear()
    ui.txtModelXml.clear()
    ui.comboListModels.clear()


def btnCancelOpenVino():
    ui.btnCancelOpenVino.setEnabled(False)
    ui.btnDeleteOpenVino.setEnabled(True)
    clearFieldsTabConfigDetection()
    comboListModelsUpdate(0)

def btnDeleteOpenVino():

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Sem modelo ativo")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    if len(statusConfig.data.get('openVinoModels')) > 0:
        if not statusConfig.deleteModel(ui.comboListModels.currentText()):
            msg.setText("Ao menos um modelo deve estar cadastrado e estar ativo. Adicione/altere algum modelo como 'Ativo' antes de delete-lo")
            msg.exec()
        else:
            refreshStatusConfig()
            comboListModelsUpdate(0)

def btnNewModel():
    clearFieldsTabConfigDetection()
    ui.txtModelName.setFocus()
    ui.btnCancelOpenVino.setEnabled(True)
    ui.btnDeleteOpenVino.setEnabled(False)

def btnSaveOpenVino():

    statusFields = True
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Campo em branco")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    #checando campos em branco

    if len(ui.txtModelName.text()) == 0:
        msg.setText("Campo 'Nome' em branco")
        msg.exec()
        ui.txtModelName.setFocus()
        statusFields = False

    elif len(ui.txtModelBin.text()) == 0:
        msg.setText("Campo 'Arquivo .bin' em branco")
        msg.exec()
        ui.txtModelBin.setFocus()
        statusFields = False

    elif len(ui.txtModelXml.text()) == 0:
        msg.setText("Campo 'Arquivo .xml' em branco")
        msg.exec()
        ui.txtModelXml.setFocus()
        statusFields = False
    
    elif len(ui.txtCpuExtension.text()) == 0:
        msg.setText("Campo 'CPU Extensions' em branco")
        msg.exec()
        ui.txtCpuExtension.setFocus()
        statusFields = False
    
    elif len(ui.txtPluginDir.text()) == 0:
        msg.setText("Campo 'Plugin Diretorio' em branco")
        msg.exec()
        ui.txtPluginDir.setFocus()
        statusFields = False

    elif not statusConfig.checkActiveModel() and len(statusConfig.data.get('openVinoModels')) == 1:
        statusFields = False
        msg.setText("Ao menos 1 modelo deve estar ativo. Marque a opção 'Ativo'")
        msg.exec()

    #elif statusConfig.checkActiveModel() and len(statusConfig.data.get('openVinoModels')) > 1 and ui.checkBoxActiveModel.isChecked():
    #    statusFields = False
    #    msg.setText("Já existe um modelo 'Ativo', desmarque a opção 'Ativo' antes de salvar")
    #    msg.exec()

    deviceTxt = "CPU"
    if ui.comboListDevices.currentIndex() == 0:
        deviceTxt = "CPU"
    elif ui.comboListDevices.currentIndex() == 1:
        deviceTxt = "GPU"
    elif ui.comboListDevices.currentIndex() == 2:
        deviceTxt = "MYRIAD"


    if statusFields:

        statusConfig.addOpenVinoModels("True" if ui.checkBoxActiveModel.isChecked() else "False",
                                   ui.txtModelName.text(),
                                   ui.txtModelXml.text(),
                                   ui.txtModelBin.text(),
                                   ui.txtCpuExtension.text(),
                                   ui.txtPluginDir.text(),
                                   deviceTxt)
        refreshStatusConfig()
        comboListModelsUpdate(ui.comboListModels.currentIndex())
        ui.btnCancelOpenVino.setEnabled(False)
        ui.btnDeleteOpenVino.setEnabled(True)


def comboListModelsUpdate(i):

    clearFieldsTabConfigDetection()

    if len(statusConfig.data.get('openVinoModels')) > 0:
        for m in statusConfig.data.get('openVinoModels'):
            ui.comboListModels.addItem(m.get('name'))

        ui.comboListModels.setCurrentIndex(i)

        m = statusConfig.data.get('openVinoModels')[i]

        ui.checkBoxActiveModel.setCheckState(True if m.get('isActive') == "True" else False)
        ui.txtModelName.setText(m.get('name'))
        ui.txtModelBin.setText(m.get('openVinoModelBin'))
        ui.txtModelXml.setText(m.get('openVinoModelXml'))
        ui.txtCpuExtension.setText(statusConfig.getCpuExtension())
        ui.txtPluginDir.setText(statusConfig.getPluginDir())
        ui.txtModelName.setText(m.get('name'))

        if m.get('openVinoDevice') == 'CPU':
            ui.comboListDevices.setCurrentIndex(0)
        elif m.get('openVinoDevice')  == 'GPU':
            ui.comboListDevices.setCurrentIndex(1)
        elif m.get('openVinoDevice') == 'MYRIAD':
            ui.comboListDevices.setCurrentIndex(2)




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

    #print('statusFields: {}'.format(statusFields))
    #print('campos: person: {}'.format(ui.checkPerson.isChecked()))
    #print('campos: person: {}'.format(ui.checkCar.isChecked()))
    #print('campos: person: {}'.format(ui.checkBike.isChecked()))
    #print('campos: person: {}'.format(ui.checkDog.isChecked()))

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

    #print('objectType: {}'.format(objectType))

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
    statusConfig.deleteAlarm(ui.comboRegions.currentText(), ui.comboAlarms.currentText())
    refreshStatusConfig()
    comboRegionsUpdate(0)
    comboAlarmsUpdate(0)


def btnDeleteRegion():
    statusConfig.deleteRegion(ui.comboRegions.currentText())
    refreshStatusConfig()
    comboRegionsUpdate(0)
    comboAlarmsUpdate(0)



def fillComboAlarm(regionId):

    #preenchendo lista de alarmes
    if not statusConfig.isAlarmEmpty(regionId):
        for a in regions[regionId].get('alarm'):
            #print('size alarm list: {}'.format(len(r.get('alarm'))))
            #print('name alarm added : {}'.format(a.get('name')))
            ui.comboAlarms.addItem(a.get('name'))

def comboRegionsUpdate(i):
    #print('combo regions update')
    #print('comboBox id: {}'.format(i))

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
            #print('alarm update from regionupdate')

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
    #print('alarmUpdate i: {}'.format(i))
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
    #print('tSoundLimit button: {}'.format(tSoundLimit))

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

def checkBoxWebcamStateChanged(state):
    if state == 0:
       ui.txtUrlRstp.setEnabled(True)
    # Qt.Checked 
    elif (state == 1 or state == 2):
        ui.txtUrlRstp.clear()
        ui.txtUrlRstp.setEnabled(False)



def initFormLogin(self, ret):

    global uiLogin, formLogin 

    log.info('Iniciando tela de login')

    uiLogin.btnLogin.clicked.connect(btnLogin)
    uiLogin.btnExit.clicked.connect(btnExit)

    windowLogin.show()
    app.exec_()



def callbackButtonRegioes(self, ret):

    # ----------- init tab modelos detecção --------------- 

    ui.btnSaveOpenVino.setEnabled(True)
    ui.btnNewModel.setEnabled(True)
    ui.btnDeleteOpenVino.setEnabled(True)
    ui.btnCancelOpenVino.setEnabled(False)

    #mostrando o modelo atualmente em uso
    currentIndex = 0

    if len(statusConfig.data.get('openVinoModels')) > 0:
        for m in statusConfig.data.get('openVinoModels'):
            if m.get('isActive') == "False":
                currentIndex = currentIndex + 1
            else:
                break
    comboListModelsUpdate(currentIndex)

    #slots
    ui.comboListModels.activated['int'].connect(comboListModelsUpdate)
    ui.btnNewModel.clicked.connect(btnNewModel)
    ui.btnDeleteOpenVino.clicked.connect(btnDeleteOpenVino)
    ui.btnSaveOpenVino.clicked.connect(btnSaveOpenVino)
    ui.btnCancelOpenVino.clicked.connect(btnCancelOpenVino)
    #windowConfig.destroyed.connect(tabClose)

    # ----------- init tab configuração geral --------------- 

    ui.btnSaveEmail.setEnabled(True)


    fillTabGeral()


    #slots
    ui.btnSaveEmail.clicked.connect(btnSaveEmail)
    #ui.checkBoxWebCam.stateChanged.connect(checkBoxWebcamStateChanged)

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

    threadWindow = Thread(target=windowConfig.show())
    threadWindow.start()
    #windowConfig.show()
    
ret = 1
initFormLogin(None, ret)

cv.namedWindow('frame')
cv.setMouseCallback('frame', polygonSelection)

if statusLicence and conexao:

    #global conectado, frame

    log.info('statusLicence on')
    
    initConfig()

    ### ---------------  OpenVino Init ----------------- ###
    if isOpenVino:

        log.info('isOpenVino in')
    
        ret, frame = ipCam.read()
        ret, next_frame = ipCam.read()
    
        #nchw, exec_net, input_blob, out_blob = pOpenVino.initOpenVino(device, statusConfig.data["openVinoModelXml"], statusConfig.data["openVinoModelBin"])
        #log.info('CPU Extension    : {}'.format(openVinoCpuExtension))
        #log.info('Plugin Diretorio : {}'.format(openVinoPluginDir))
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
            callbackButtonRegioes(None, ret)
            initOpenVinoStatus = False
            init_video = False
        else:
            cur_request_id = 0
            next_request_id = 1
            render_time = 0
    
    else:
        log.info("TensorFlow on")
        cvNet = cv.dnn.readNetFromTensorflow(pb, pbtxt)
        cvNet = cv.dnn.readNetFromTensorflow(pb, pbtxt)
    
    
    
    conectado, frame = ipCam.read()
    if frame is not None:
        (h,w) = frame.shape[:2]



while init_video:

    #if counter == 0:
    #    startFps = time.time()

    start = time.time()

    conectado, frame = ipCam.read()


    if (conectado and frame is not None and next_frame is not None):

        frame_no_label = frame.copy()
        frame_screen = frame.copy()
        frame_no_label_email = frame.copy()

        #objects = ct.update(rects = listObjectsTracking)

        currentData = utils.getDate()
        currentData = [currentData.get('day'), currentData.get('month')]

        if current_data_dir != currentData:
            status_dir_criado, dir_video_trigger = utils.createDirectory(statusConfig.data["dirVideos"])
            current_data_dir = utils.getDate()
            current_data_dir = [current_data_dir.get('day'), current_data_dir.get('month')]

        #desenhando regioes
        for r in regions:
             pts = np.array(r.get("pointsPolygon"), np.int32)
             pts = pts.reshape((-1,1,2))
             cv.polylines(frame_screen,[pts],True,(0,0,255), 2)

        if cropPolygon:
            pts = np.array(ref_point_polygon, np.int32)
            pts = pts.reshape((-1,1,2))
            cv.polylines(frame_screen,[pts],True,(0,0,255), 2)


        #passando o Frame selecionado do portao para deteccao somente se o portao virtual estiver selecionado
        if portaoVirtualSelecionado:

            #se eh openVino e este foi inicializado corretamente 
            if isOpenVino and initOpenVinoStatus:
            ### ---------------  OpenVino Get Objects ----------------- ###

                ret, listReturn  = pOpenVino.getListBoxDetected(ipCam, device, frame, next_frame, nchw, exec_net, out_blob, input_blob, cur_request_id, next_request_id, prob_threshold)

                if ret:
                    frame = next_frame
                    frame, next_frAme, cur_request_id, next_request_id, listObjects, listObjectsTracking, prob_threshold_returned  = listReturn[0], listReturn[1], listReturn[2], listReturn[3], listReturn[4], listReturn[5], listReturn[6]

                    cur_request_id, next_request_id = next_request_id, cur_request_id

            else:
                #chamada para a CNN do OpenCV - TensorFlow Object Detection API 
                log.info("CNN via TF Object Detection API")
                listObjects, listObjectTradking  = objectDetection(frame, idObjeto, listRectanglesDetected, detection, rows, cols)


        if len(listObjects) == 0 and portaoVirtualSelecionado:


            #listObjects.clear()
            #listObjectsTracking.clear()
            #objects = ct.update(listObjectsTracking)

            tEmptyEnd = time.time()
            tEmpty = tEmptyEnd- tEmptyStart
            #print('sem objetos')
            #print('empty: {}'.format(tEmpty))

            if tEmpty > 10:
                #print('tempty > 10')
                gravando = False
                newVideo = True
                releaseVideo = True

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
                        for r in regions:

                            #checando tipo objeto
                            typeObject = str(box[6])

                            if r.get('objectType').get(typeObject) == "True":


                                if prob_threshold_returned >= int(r.get('prob_threshold')):

                                    if isIdInsideRegion(centroid, r.get('pointsPolygon')):

                                        tEmptyEnd = time.time()
                                        tEmpty = tEmptyEnd- tEmptyStart

                                        tEmptyStart = time.time()

                                        #enquanto tiver objetos dentro da regiao o video eh gravado, independente do alarme
                                        gravando = True
                                        #resume_screensaver()

                                        #checando alarmes 
                                        d = utils.getDate()
                                        weekDay = d['weekDay']
                                        #print('weekDay {}'.format(weekDay))
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

                                                            #if (sendMailAlert('igorddf@gmail.com', 'igorddf@gmail.com', frame_no_label_email, str(box[6]), r.get('nameRegion'))):
                                                            #    log.info('Alerta enviado ID[' + str(objectID) + ']')
                                                            threadEmail = Thread(target=sendMailAlert, args=(emailConfig['name'],
                                                                                                               emailConfig['to'],
                                                                                                               emailConfig['subject'],
                                                                                                               emailConfig['port'],
                                                                                                               emailConfig['smtp'],
                                                                                                               emailConfig['user'],
                                                                                                               emailConfig['password'],
                                                                                                               frame_no_label_email,
                                                                                                               str(box[6]),
                                                                                                               r.get('nameRegion')))
                                                            threadEmail.start()

                                                            #if (sendMailAlert(emailConfig['name'],
                                                            #                  emailConfig['to'],
                                                            #                  emailConfig['subject'],
                                                            #                  emailConfig['port'],
                                                            #                  emailConfig['smtp'],
                                                            #                  emailConfig['user'],
                                                            #                  emailConfig['password'],
                                                            #                  frame_no_label_email,
                                                            #                  str(box[6]),
                                                            #                  r.get('nameRegion'))):
                                                            #    log.info('Alerta enviado ID[' + str(objectID) + ']')

                                                            listObjectMailAlerted.append(objectID)
                                        #end loop alarms
                                    else:

                                        tEmptyEnd = time.time()
                                        tEmpty = tEmptyEnd- tEmptyStart
                                        #print('tEmpty {}'.format(tEmpty))

                                        if tEmpty > 10:
                                            gravando = False
                                            newVideo = True
                                            releaseVideo = True
                                            #suspend_screensaver()


                                    #end if isIdInsideRegion

                                #end if prob_threshold_returned


                        #end loop in Regions

                    #end loop objectTracking.items()
            #end loop for box listObjects

        tEmptyEnd = time.time()
        tEmpty = tEmptyEnd- tEmptyStart
        #print('tEmpty end loop {}'.format(tEmpty))

        if newVideo and gravando:

             if out_video is not None:
                 out_video.release()
                 out_video = None
                 releaseVideo = False

             #grava video novo se tiver um objeto novo na cena
             hora = utils.getDate()['hour'].replace(':','-')
             nameVideo = dir_video_trigger + '/' + hora + '.avi'
             out_video = cv.VideoWriter(nameVideo, fourcc, FPS, (w,h))
             out_video.write(frame_no_label)
             newVideo = False

        if gravando:
            if out_video is not None:
                out_video.write(frame_no_label)

        cv.imshow('frame', frame_screen)

        end = time.time()

        renderTime = (end-start)*1000
        FPS = 1000/renderTime
        #print('render time: {:10.2f} ms'.format(renderTime))
        #print('FPS: {:10.2f} ms'.format(FPS))

        listObjects.clear()
        #listObjectsTracking.clear()

        #chamando callbackButtonRegioes  
        if cv.waitKey(1) & 0xFF == ord('c'):
            callbackButtonRegioes(None, ret)
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    else:
        if not conectado:
            log.warning('Reconectando em 5 segundos...')
            time.sleep(5)
            ipCam = utils.camSource(source)

if out_video is not None:
    log.warning('Fim da captura de video')
    out_video.release()

if ipCam and cv is not None:
    ipCam.release()
    cv.destroyAllWindows()



