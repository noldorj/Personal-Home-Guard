import cv2 as cv
import numpy as np
#from datetime import date
import time
from objectTracking.pyimagesearch.centroidtracker import CentroidTracker
#from imutils.video import VideoStream
#import imutils
#import os
from Utils_tracking import sendMailAlert
from Utils_tracking import saveImageBox
import utilsCore as utils
#import pluginOpenVino as pOpenVino
import logging as log
#import mainFormSlots

#import tensorflow as tf


classes = ["background", "pessoa", "bicileta", "carro", "moto", "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant",
    "unknown", "stop sign", "parking meter", "bench", "bird", "gato", "cachorro", "horse",
    "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "unknown", "backpack",
    "umbrella", "unknown", "unknown", "handbag", "tie", "suitecase", "frisbee", "skis",
    "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
    "surfboard", "tennis racket", "bottle", "unknown", "wine glass", "cup", "fork", "knife",
    "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog",
    "pizza", "donut", "cake", "chair", "couch", "potted plant", "bed", "unknown", "dining table",
    "unknown", "unknown", "toilet", "unknown", "tv", "laptop", "mouse", "remote", "keyboard",
    "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "unknown",
"book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush" ]

#tie, suitecase (= carro)

import subprocess
import ewmh

active_id = hex(ewmh.EWMH().getActiveWindow().id)

def suspend_screensaver():
    print('suspend')
    #window_id = subprocess.Popen('xwininfo -root | grep xwininfo | cut -d" " -f4', stdout=subprocess.PIPE, shell=True).stdout.read().strip()
    #run xdg-screensaver on root window
    subprocess.call('xdg-screensaver', 'suspend')

def resume_screensaver():
    print('resume')
    subprocess.Popen('xdg-screensaver resume ')

def activate_screensaver():
    subprocess.Popen('xdg-screensaver activate')



#statusConfig = utils.StatusConfig(configFile='config.json.gpu.webcam')
statusConfig = utils.StatusConfig(configFile='config.json.gpu')

# dnnMOdel for TensorFlow Object Detection API
pb = statusConfig.data["dnnModelPb"] 
pbtxt = statusConfig.data["dnnModelPbTxt"] 

#Carregando regioes salvas
regions = statusConfig.getRegions()
portaoVirtualSelecionado = False
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


#cvNet = cv.dnn.readNetFromTensorflow(pb, pbtxt)
# initialize our centroid tracker and frame dimensions
ct = CentroidTracker()
(H, W) = (None, None)

#diretorio dos videos dos alarmes
#dir_video_trigger = './'


listObjectDetected = list()

idObjeto = 0


def objectDetection(img):
    global idObjeto
    global listObjectDetected
    global detection
    global listRectanglesDetected
    global rows, cols
    box = []

    #img = cv.imread(img)
    if img is not None:
        rows = img.shape[0]
        cols = img.shape[1]
        resized = cv.resize(img, (300,300)) 
        cvNet.setInput(cv.dnn.blobFromImage(resized, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        cvOut = cvNet.forward()


        for detection in cvOut[0,0,:,:]:

            score = float(detection[2])

            if score > 0.35:

                left = int(detection[3] * cols)
                top = int(detection[4] * rows)
                right = int(detection[5] * cols)
                bottom = int(detection[6] * rows)

                idx = int(detection[1]) #indice da classe identificada
                label = "{}: {:.2f}%".format(classes[idx],score*100)
                classe = classes[idx]

                box = (left, top, right, bottom, label, idx, classe)


                if classes[idx] is 'pessoa' or \
                    classes[idx] is 'gato' or \
                    classes[idx] is 'cachorro':
#                    classes[idx] is 'carro' or \
#                    classes[idx] is 'moto' or \

#                    print('Objeto: ' + classes[idx])

#                    log.log(log.DEBUG, "Objeto: {}".format(classe))

#                    log.info("Objeto: {}".format(classe))
                    #print('Objeto: {} '.format(label))

                    boxTracking = (left, top, right, bottom)

                    listObjectsTracking.append(boxTracking)

                    listRectanglesDetected.append(box)

#                else:
#                    print('Objecto desconhecido: ' + classes[idx])

#	else:
        # print('\n frame lost')

    return listRectanglesDetected



drawing = False     # true if mouse is pressed
mode = True         # if True, draw rectangle.
ix, iy = -1, -1

ref_point = []
ref_point_polygon = list()
crop = False
cropPolygon = False
showGate = False
regiaoPortao = None

from matplotlib.path import Path

def isIdInsideRegion(centroid, ref_point_polygon):

    path = Path(ref_point_polygon)
    #print('centroid[0]: {}'.format(centroid[0]))
    #print('centroid[1]: {}'.format(centroid[1]))
    mask = path.contains_points([(centroid[0], centroid[1])])
    #print('mask: {}'.format(mask))
    return mask


def polygonSelection(event, x, y, flags, param):

    global ref_point_polygon, cropPolygon, portaoVirtualSelecionado
    #print('polygonSelection')
    #print('flags: {}'.format(flags))
    #print('event: {}'.format(event))

    if event == cv.EVENT_LBUTTONDOWN and not portaoVirtualSelecionado and flags == cv.EVENT_FLAG_CTRLKEY+1:

        ref_point_polygon.append([x, y])
        #print(' ')
        #print('cv.EVENT_FLAG_CTRLKEY on')
        #print('size of ref_point_polygon: {}'.format(len(ref_point_polygon)))
        cropPolygon = True

    #elif not portaoVirtualSelecionado and event == cv.EVENT_LBUTTONUP and flags == cv.EVENT_FLAG_SHIFTKEY+1 and cropPolygon:
    #elif not portaoVirtualSelecionado and flags == 0 and cropPolygon:
    elif not portaoVirtualSelecionado and flags == 0:

        #ref_point_polygon.append((x, y))
        #print(' ')
        print('cv.EVENT_FLAG_ALTKEY off')
        #print('size of ref_point_polygon: {}'.format(len(ref_point_polygon)))
        #cropPolygon = False
        portaoVirtualSelecionado = True


cv.namedWindow('frame')
cv.setMouseCallback('frame', polygonSelection)

objDetectado = False

hora = utils.getDate()['hour'].replace(':','-')

#TO-DO: tem que pegar do arquivo de texto
current_data_dir = utils.getDate()
current_data_dir = [current_data_dir.get('day'), current_data_dir.get('month')]

timer_without_object = 0
start_time = 0
#gravando = statusConfig.data["isRecording"] == 'True'
nameVideo  = 'firstVideo'
gravando = False
newVideo = True
releaseVideo = False 
objects = None
#FPS = ipCam.get(cv.CAP_PROP_FPS) #30.0 #frames per second
FPS = 4  #de acordo com o manual da mibo ic5 intelbras

#primeiro objeto é enviado
listObjectMailAlerted = []
listObjectSoundAlerted = []
listObjectVideoRecorded = []
out_video = None

#fourcc = cv.VideoWriter_fourcc(*'X264')
#for linux x264 need to recompile opencv mannually
fourcc = cv.VideoWriter_fourcc(*'XVID')
#fourcc = cv.VideoWriter_fourcc('M','J','P','G')
#cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, FPS, (1280,720))

isOpenVino = statusConfig.data["isOpenVino"] == 'True'
if isOpenVino:
    import pluginOpenVino as pOpenVino

device = statusConfig.data["openVinoDevice"]

posConfigPv = 255

#import mainFormSlots
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
import sys
from mainForm import *
from PyQt5.QtWidgets import QMainWindow, QApplication, QErrorMessage, QMessageBox, QPushButton
from PyQt5.QtCore import QTime

windowConfig = QWidget()
ui = Ui_formConfig()
ui.setupUi(windowConfig)

def initInterface():
    cv.createButton('Configurar ', callbackButtonRegioes, None,cv.QT_PUSH_BUTTON)


#---------------- gui -------------------

def refreshStatusConfig():
    statusConfig = utils.StatusConfig(configFile='config.json.gpu')
    regions = statusConfig.getRegions()


def btnCancelRegion():
    ui.btnSaveRegion.setEnabled(False)
    ui.btnCancelRegion.setEnabled(False)
    if len(regions) > 0:
        ui.btnDeleteRegion.setEnabled(True)
    else:
        ui.btnDeleteRegion.setEnabled(False)

    ui.btnNewRegion.setEnabled(True)
    ui.btnNewAlarm.setEnabled(True)
    clearFields()
    comboRegionsUpdate(0)

    global portaoVirtualSelecionado
    portaoVirtualSelecionado = True


def clearFields():
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
    ui.btnSaveRegion.setEnabled(False)
    ui.btnSaveAlarm.setEnabled(False)
    ui.btnDeleteAlarm.setEnabled(True)
    ui.btnCancelAlarm.setEnabled(False)
    ui.btnNewAlarm.setEnabled(True)
    ui.comboAlarms.setEnabled(True)
    comboRegionsUpdate(ui.comboRegions.currentIndex())

def btnNewRegion():
    print('botao btnNewRegion')
    global portaoVirtualSelecionado, ref_point_polygon

    portaoVirtualSelecionado = False
    ref_point_polygon.clear()
    print('Selecione novo portao com a tecla CTLR pressionada')

    #clear fields
    clearFields()
    #ui.comboRegions.clear()
    ui.btnCancelRegion.setEnabled(True)
    ui.btnDeleteRegion.setEnabled(False)
    ui.btnSaveRegion.setEnabled(True)
    ui.btnDeleteAlarm.setEnabled(False)
    ui.btnCancelAlarm.setEnabled(False)
    ui.btnSaveAlarm.setEnabled(False)

def btnSaveRegion():
    print('botao btnSaveRegion')
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

    elif len(ref_point_polygon) == 0:
        msg.setText("Região não selecionada! manter tecla CTRL pressionada até selecionar todos os pontos desejados")
        msg.exec()
        portaoVirtualSelecionado = False

    if statusFields and len(ref_point_polygon) > 0:

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
                      'dog':'True' if ui.checkBike.isChecked() else 'False'}

        points = ref_point_polygon

        #points = [[[15,15],[15,65],[65,15],[65,65]]]

        statusConfig.addRegion(ui.txtRegionName.displayText(),
                               newAlarm, objectType, round(float(ui.txtThreshold.displayText()),2), points )
        refreshStatusConfig()
        #print('count: {}'.format(len(regions)))
        comboRegionsUpdate(len(regions)-1)
        comboAlarmsUpdate(0)
        ui.btnSaveRegion.setEnabled(False)
        #ref_point_polygon.clear()



        portaoVirtualSelecionado = True
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

        print('botao btnSAveAlarm')
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
        #a = {"name":ui.txtNameAlarm.displayText(), 'time':t, 'days':days}
        statusConfig.addAlarm(ui.comboRegions.currentIndex(), a)
        refreshStatusConfig()

        comboRegionsUpdate(ui.comboRegions.currentIndex())
        ui.btnSaveAlarm.setEnabled(False)
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

    clearFields()
    #r = regions[i]

    ui.comboAlarms.clear()

    if not statusConfig.isRegionsEmpty():
        for r in regions:
            ui.comboRegions.addItem(r.get("nameRegion"))

        r = regions[i]
        ui.txtRegionName.insert(r.get('nameRegion'))
        ui.txtThreshold.insert(str(r.get('prob_threshold')*100))
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
def callbackButtonRegioes(self, ret):

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

    ui.btnSaveAlarm.setEnabled(False)
    ui.btnCancelRegion.setEnabled(False)
    ui.btnCancelAlarm.setEnabled(False)
    ui.btnSaveRegion.setEnabled(False)
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
    windowConfig.show()
    #print('Button regioes')


initInterface()
counter = 0
tEmpty = 0
tEmptyEnd = 0
tEmptyStart = 0

### ---------------  OpenVino Init ----------------- ###
if isOpenVino:

    ret, frame = ipCam.read()
    ret, next_frame = ipCam.read()
    nchw, exec_net, input_blob, out_blob = pOpenVino.initOpenVino(device, statusConfig.data["openVinoModelXml"], statusConfig.data["openVinoModelBin"])
    cur_request_id = 0
    next_request_id = 1
    render_time = 0
### ---------------  OpenVino Init ----------------- ###
else:
    cvNet = cv.dnn.readNetFromTensorflow(pb, pbtxt)

conectado, frame = ipCam.read()
if frame is not None:
    (h,w) = frame.shape[:2]

#print('w,h {}'.format((w,h)))

#tempo sem objetos detectados
tEmptyStart = time.time()

while True:

    #if counter == 0:
    #    startFps = time.time()

    start = time.time()

    conectado, frame = ipCam.read()

    #print('w,h {}'.format((w,h)))

    if (conectado and frame is not None and next_frame is not None):

        frame_no_label = frame.copy()
        frame_screen = frame.copy()
        frame_no_label_email = frame.copy()

        objects = ct.update(rects = listObjectsTracking)

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
             cv.polylines(frame_screen,[pts],True,(0,255,255))

        if cropPolygon:
            pts = np.array(ref_point_polygon, np.int32)
            pts = pts.reshape((-1,1,2))
            cv.polylines(frame_screen,[pts],True,(0,255,255))


        #passando o Frame selecionado do portao para deteccao somente se o portao virtual estiver selecionado
        if portaoVirtualSelecionado:

            if isOpenVino:
            ### ---------------  OpenVino Get Objects ----------------- ###

                ret, listReturn  = pOpenVino.getListBoxDetected(ipCam, device, frame, next_frame, nchw, exec_net, out_blob, input_blob, cur_request_id, next_request_id, prob_threshold)

                if ret:
                    frame = next_frame
                    frame, next_frAme, cur_request_id, next_request_id, listObjects, listObjectsTracking, prob_threshold_returned  = listReturn[0], listReturn[1], listReturn[2], listReturn[3], listReturn[4], listReturn[5], listReturn[6]

                    cur_request_id, next_request_id = next_request_id, cur_request_id

            else:
                #chamada para a CNN do OpenCV - TensorFlow Object Detection API 
                log.info("CNN via TF Object Detection API")
                listObjects = objectDetection(frame)


        if len(listObjects) == 0 and portaoVirtualSelecionado:


            listObjects.clear()
            listObjectsTracking.clear()
            objects = ct.update(listObjectsTracking)

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

            for box in listObjects:

                if portaoVirtualSelecionado:
                    #print('Checando portao virtual')

                    #objetos com ID e centro de massa
                    objectsTracking = ct.update(listObjectsTracking)

                    for (objectID, centroid) in objectsTracking.items():

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

                                print('prob_threshold_returned: {}'.format(prob_threshold_returned))
                                print('prob_threshold config: {}'.format(r.get('prob_threshold')))

                                if prob_threshold_returned >= int(r.get('prob_threshold')):
                                    print(' ')
                                    print('in')

                                    if isIdInsideRegion(centroid, r.get('pointsPolygon')):

                                        tEmptyEnd = time.time()
                                        tEmpty = tEmptyEnd- tEmptyStart
                                        #print('tEmpty {}:'.format(tEmpty))

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

                                                    if a.get('isSoundAlert') == "True":
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

                                                            if (sendMailAlert('igorddf@gmail.com', 'igorddf@gmail.com', frame_no_label_email, str(box[6]), r.get('nameRegion'))):
                                                                log.info('Alerta enviado ID[' + str(objectID) + ']')

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
        listObjectsTracking.clear()
        objects.update()

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    else:
        if not conectado:
            print('Reconectando em 3 segundos...')
            time.sleep(3)
            ipCam = utils.camSource(source)

if out_video is not None:
    print('video release fora do loop')
    out_video.release()

ipCam.release()
cv.destroyAllWindows()



