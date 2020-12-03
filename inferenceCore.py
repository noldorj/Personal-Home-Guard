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
from objectDetectionTensorFlow import objectDetection 
import secrets
import psutil
import pluginOpenVino as pOpenVino
from utilsCore import checkInternetAccess
from matplotlib.path import Path
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
#import tensorflow as tf

#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8')
#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', filename='pv.log', encoding='utf-8', level=log.DEBUG)
#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, stream=sys.stdout)
#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S',  encoding='utf-8', level=log.CRITICAL, stream=sys.stdout ) 

#from fbs_runtime.application_context.PyQt5 import ApplicationContext

#app = ApplicationContext()

#app = QApplication (sys.argv)





#cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, FPS, (1280,720))




#---------------- gui Form Login -------------------



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







class InferenceCore(QThread):

    change_pixmap_signal = pyqtSignal(np.ndarray)
    camRunTime = None

    def __init__(self):
        super().__init__()
        self._run_flag = True
        print('InferenceCore __init__')

        #cv.namedWindow('frame', cv.WINDOW_FREERATIO)
        #cv.setWindowTitle('frame', 'Portão Virtual')
        #cv.setMouseCallback('frame', self.polygonSelection)
        
    def setCamRunTime(self, camRunTime):
        self.camRunTime = camRunTime

    def isIdInsideRegion(centroid, ref_point_polygon):
        path = Path(ref_point_polygon)
        mask = path.contains_points([(centroid[0], centroid[1])])
        return mask


    def polygonSelection(self, event, x, y, flags, param): 
        #global ref_point_polygon, cropPolygon, portaoVirtualSelecionado

        if event == cv.EVENT_LBUTTONDBLCLK and not self.camRunTime.portaoVirtualSelecionado:  
            
            self.camRunTime.ref_point_polygon.append([x, y])
            self.camRunTime.cropPolygon = True

        elif not self.camRunTime.portaoVirtualSelecionado and flags == 0:

            self.camRunTime.portaoVirtualSelecionado = True

    def initOpenVino(self):
        #global isOpenVino, ret, frame, next_frame, cvNet, nchw, exec_net, input_blob, out_blob
        #global device, openVinoModelXml, openVinoModelBin, openVinoCpuExtension, openVinoPluginDir
        #global initOpenVinoStatus, init_video, cur_request_id, next_request_id, render_time
        #global out_video_all_time, timeSessionInit, timeGravandoAllInit, timeGravandoAll, hora, nameVideoAllTime, dir_video_trigger_all_time, timeInternetOffStart, h, w
        
        ### ---------------  OpenVino Init ----------------- ###
        
        if self.camRunTime.isOpenVino:

            print('initOpenVino')
            print('initOpenVino2')
        
            self.camRunTime.ret, self.camRunTime.frame = self.camRunTime.ipCam.read()
            self.camRunTime.ret, self.camRunTime.next_frame = self.camRunTime.ipCam.read()
            
            #frame = cv.resize(frame, (RES_X, RES_Y)) 
            
            #next_frame = cv.resize(next_frame, (RES_X, RES_Y)) 
        
            cvNet = None
            print('try initOpenVino')
            try:
                self.camRunTime.nchw, self.camRunTime.exec_net, self.camRunTime.input_blob, self.camRunTime.out_blob = \
                    pOpenVino.initOpenVino(self.camRunTime.device, self.camRunTime.openVinoModelXml, \
                    self.camRunTime.openVinoModelBin, self.camRunTime.openVinoCpuExtension, self.camRunTime.openVinoPluginDir)
        
            except:
                log.critical('Erro ao iniciar OpenVino - checar arquivo de configuracao')
                print('Erro ao iniciar OpenVino - checar arquivo de configuracao')
                #abrindo janela de configuracao"
                #msg = QMessageBox()
                #msg.setIcon(QMessageBox.Information)
                #msg.setWindowTitle("Erro ao abrir mómodulo OpenVino - checar aba de configurações")
                #msg.exec()
                #callbackButtonRegioes(None, 1)
                self.camRunTime.initOpenVinoStatus = False
                self.camRunTime.init_video = False
            else:
                print('Openvino carregado')
                log.info(' ')
                self.camRunTime.cur_request_id = 0
                self.camRunTime.next_request_id = 1
                self.camRunTime.render_time = 0
        
        else:
            log.info("TensorFlow on")
            cvNet = cv.dnn.readNetFromTensorflow(pb, pbtxt)
            cvNet = cv.dnn.readNetFromTensorflow(pb, pbtxt)
        
        self.camRunTime.conectado, self.camRunTime.frame = self.camRunTime.ipCam.read()
        if self.camRunTime.frame is not None:
            #frame = cv.resize(frame, (RES_X, RES_Y)) 
            (self.camRunTime.h, self.camRunTime.w) = self.camRunTime.frame.shape[:2]


        self.camRunTime.timeSessionInit = time.time()
        self.camRunTime.timeGravandoAllInit = time.time()
        self.camRunTime.timeInternetOffStart = time.time()
        
        self.camRunTime.hora = utils.getDate()['hour'].replace(':','-')
        self.camRunTime.nameVideoAllTime = self.camRunTime.dir_video_trigger_all_time + '/' + self.camRunTime.hora + '.avi'
        
        #primeiro arquivo fica zuado - bug
        #if out_video_all_time is not None: 
        #h = nchw[2]
        #w = nchw[3]
        self.camRunTime.out_video_all_time = cv.VideoWriter(self.camRunTime.nameVideoAllTime, self.camRunTime.fourcc, self.camRunTime.FPS, (self.camRunTime.w, self.camRunTime.h))

    def run(self):
        # capture from web cam
        #cap = cv.VideoCapture('rtsp://admin:WWYZRL@192.168.5.101:554/profile0')
        
        #while self._run_flag:
        #    ret, cv_img = cap.read()
        #    if ret:
        #        self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        #cap.release() 
        print('InferenceCore run()')
        self.initOpenVino()
        print('init_video: ' + str(self.camRunTime.init_video))

        #while True:        
        while self.camRunTime.init_video and self.camRunTime.sessionStatus and self.camRunTime.rtspStatus :

            #if counter == 0:
            #    startFps = time.time()

            self.camRunTime.start = time.time()
            #log.info('while')
            

            self.camRunTime.conectado, self.camRunTime.frame = self.camRunTime.ipCam.read()
            #if frame is not None:
            #    frame = cv.resize(frame, (RES_X, RES_Y)) 
            

            if (self.camRunTime.frame is not None and self.camRunTime.next_frame is not None):
            #if (self.camRunTime.conectado and self.camRunTime.frame is not None and self.camRunTime.next_frame is not None):

                frame_no_label = self.camRunTime.frame.copy()
                frame_screen = self.camRunTime.frame.copy()
                frame_no_label_email = self.camRunTime.frame.copy()

                #objects = ct.update(rects = listObjectsTracking)

                self.camRunTime.currentData = utils.getDate()
                self.camRunTime.currentData = [self.camRunTime.currentData.get('day'), self.camRunTime.currentData.get('month')]

                if self.camRunTime.current_data_dir != self.camRunTime.currentData:
                    self.camRunTime.status_dir_criado_on_alarmes, self.camRunTime.dir_video_trigger_on_alarmes = utils.createDirectory(statusConfig.data["dirVideosOnAlarmes"])
                    status_dir_criado_all_time, dir_video_trigger_all_time = utils.createDirectory(statusConfig.data["dirVideosAllTime"])
                    current_data_dir = utils.getDate()
                    current_data_dir = [current_data_dir.get('day'), current_data_dir.get('month')]

                #desenhando regioes
                for r in self.camRunTime.regions:
                     pts = np.array(r.get("pointsPolygon"), np.int32)
                     pts = pts.reshape((-1,1,2))
                     cv.polylines(frame_screen,[pts],True,(0,0,255), 2)

                if self.camRunTime.cropPolygon:
                    #log.info('if cropPolygon')
                    pts = np.array(ref_point_polygon, np.int32)
                    pts = pts.reshape((-1,1,2))
                    cv.polylines(frame_screen,[pts],True,(0,0,255), 2)


                #passando o Frame selecionado do portao para deteccao somente se o portao virtual estiver selecionado
                if self.camRunTime.portaoVirtualSelecionado and (self.camRunTime.STOP_ALL == False):

                    #se eh openVino e este foi inicializado corretamente 
                    if self.camRunTime.isOpenVino and self.camRunTime.initOpenVinoStatus:
                    ### ---------------  OpenVino Get Objects ----------------- ###

                        self.camRunTime.ret, listReturn  = pOpenVino.getListBoxDetected(self.camRunTime.ipCam, self.camRunTime.device, self.camRunTime.frame,
                                           self.camRunTime.next_frame, self.camRunTime.nchw, self.camRunTime.exec_net, self.camRunTime.out_blob,
                                           self.camRunTime.input_blob, self.camRunTime.cur_request_id, self.camRunTime.next_request_id, 
                                           self.camRunTime.prob_threshold, self.camRunTime.RES_X, self.camRunTime.RES_Y)

                        if self.camRunTime.ret:
                            self.camRunTime.frame = self.camRunTime.next_frame
                            self.camRunTime.frame, self.camRunTime.next_frame, self.camRunTime.cur_request_id,
                            self.camRunTime.next_request_id, self.camRunTime.listObjects, self.camRunTime.listObjectsTracking,
                            self.camRunTime.prob_threshold_returned  = listReturn[0], listReturn[1], listReturn[2], listReturn[3], listReturn[4], listReturn[5], listReturn[6]

                            self.camRunTime.cur_request_id, self.camRunTime.next_request_id = self.camRunTime.next_request_id, self.camRunTime.cur_request_id

                    else:
                        #chamada para a CNN do OpenCV - TensorFlow Object Detection API 
                        log.info("CNN via TF Object Detection API")
                        self.camRunTime.listObjects, self.camRunTime.listObjectTradking  = objectDetection(frame, idObjeto, listRectanglesDetected, detection, rows, cols)


                if len(self.camRunTime.listObjects) == 0 and self.camRunTime.portaoVirtualSelecionado:

                    self.camRunTime.tEmptyEnd = time.time()
                    self.camRunTime.tEmpty = self.camRunTime.tEmptyEnd - self.camRunTime.tEmptyStart

                    if self.camRunTime.tEmpty > 10:
                        #print('tempty > 10')
                        self.camRunTime.gravandoOnAlarmes = False
                        self.camRunTime.newVideo = True
                        self.camRunTime.releaseVideoOnAlarmes = True

                #se tem objetos detectados pela CNN
                else:

                    #objectsTracking = ct.update(listObjectsTracking)

                    for box in self.camRunTime.listObjects:

                        if self.camRunTime.portaoVirtualSelecionado:

                            #objetos com ID e centro de massa
                            self.camRunTime.objectsTracking = ct.update(self.camRunTime.listObjectsTracking)

                            for (objectID, centroid) in self.camRunTime.objectsTracking.items():

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
                                if len(self.camRunTime.regions) != 0:
                                    for r in self.camRunTime.regions:

                                        #checando tipo objeto
                                        typeObject = str(box[6])

                                        if r.get('objectType').get(typeObject) == "True":

                                            if self.camRunTime.prob_threshold_returned >= int(r.get('prob_threshold')):

                                                if self.isIdInsideRegion(centroid, r.get('pointsPolygon')):

                                                    self.camRunTime.tEmptyEnd = time.time()
                                                    self.camRunTime.tEmpty = self.camRunTime.tEmptyEnd - self.camRunTime.tEmptyStart

                                                    self.camRunTime.tEmptyStart = time.time()

                                                    #enquanto tiver objetos dentro da regiao o video eh gravado, independente do alarme
                                                     
                                                    if self.camRunTime.statusConfig.data["isRecordingOnAlarmes"] == 'True':
                                                        self.camRunTime.gravandoOnAlarmes = True

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
                                                                    if self.camRunTime.listObjectSoundAlerted.count(objectID) == 0:
                                                                        utils.playSound()
                                                                        self.camRunTime.listObjectSoundAlerted.append(objectID)

                                                                if a.get('isEmailAlert') == "True":

                                                                    #evitar emails seguidos para mesmo objeto
                                                                    if self.camRunTime.listObjectMailAlerted.count(objectID) == 0:

                                                                        log.info('Enviando alerta por email')
                                                                        #salvando foto para treinamento
                                                                        #crop no box
                                                                        #left, top, right, bottom
                                                                        #frame_no_label = frame_no_label[int(box[1])-10:int(box[1]) + int(box[3]) , int(box[0])+10:int(box[2])]
                                                                        #saveImageBox(frame_no_label, str(box[6]))

                                                                        if utils.checkInternetAccess():

                                                                            log.info('Alerta enviado ID[' + str(objectID) + ']')
                                                                            threadEmail = Thread(target=sendMailAlert, args=(self.camRunTime.emailConfig['name'],
                                                                                                                               self.camRunTime.emailConfig['to'],
                                                                                                                               self.camRunTime.emailConfig['subject'],
                                                                                                                               self.camRunTime.emailConfig['port'],
                                                                                                                               self.camRunTime.emailConfig['smtp'],
                                                                                                                               self.camRunTime.emailConfig['user'],
                                                                                                                               frame_no_label_email,
                                                                                                                               str(box[6]),
                                                                                                                               r.get('nameRegion')))
                                                                            threadEmail.start()
                                                                            self.camRunTime.listObjectMailAlerted.append(objectID)
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

                                                                            self.camRunTime.pilhaAlertasNaoEnviados.append(alertaNaoEnviado)
                                                                            
                                                                            self.camRunTime.listObjectMailAlerted.append(objectID)

                                                                            log.critical('Sem conexao com a Internet - Alarmes serão enviados assim que houver conexao')
                                                                            log.critical('Numero de alarmes não enviados até o momento: {:d}'.format(len(pilhaAlertasNaoEnviados)))
                                                    #end loop alarms
                                                else:

                                                    self.camRunTime.tEmptyEnd = time.time()
                                                    self.camRunTime.tEmpty = self.camRunTime.tEmptyEnd - self.camRunTime.tEmptyStart

                                                    if self.camRunTime.tEmpty > 10:
                                                        self.camRunTime.gravandoOnAlarmes = False
                                                        self.camRunTime.newVideo = True
                                                        self.camRunTime.releaseVideoOnAlarmes = True
                                                        #suspend_screensaver()


                                                #end if isIdInsideRegion

                                            #end if prob_threshold_returned


                                    #end loop in Regions
                                #se nao houver regiao configurada, enviar um alarme generico
                                else:
                                    log.info('Sem regiao configurada')

                                    #evitar emails seguidos para mesmo objeto
                                    if self.camRunTime.listObjectMailAlerted.count(objectID) == 0:
                                        log.info('Enviando alerta por email')
                                        
                                        #60% acuracia padrao 
                                        if self.camRunTime.prob_threshold_returned >= 60:

                                            self.camRunTime.tEmptyEnd = time.time()
                                            self.camRunTime.tEmpty = self.camRunTime.tEmptyEnd - self.camRunTime.tEmptyStart

                                            self.camRunTime.tEmptyStart = time.time()

                                            #enquanto tiver objetos dentro da regiao o video eh gravado, independente do alarme
                                             
                                            if self.camRunTime.statusConfig.data["isRecordingOnAlarmes"] == 'True':
                                                self.camRunTime.gravandoOnAlarmes = True
                                            

                                            #checando alarmes 
                                            d = utils.getDate()
                                            weekDay = d['weekDay']
                                            #print('weekDay {}'.format(weekDay))
                                            minute = int(d['minute'])
                                            hour = int(d['hourOnly'])

                                            currentMinutes = (hour * 60) + minute
                                            
                                            log.info('Enviando alerta por email')

                                            if utils.checkInternetAccess():

                                                log.info('Alerta enviado ID[' + str(objectID) + ']')
                                                threadEmail = Thread(target=sendMailAlert, args=(emailConfig['name'],
                                                                                                   self.camRunTime.emailConfig['to'],
                                                                                                   self.camRunTime.emailConfig['subject'],
                                                                                                   self.camRunTime.emailConfig['port'],
                                                                                                   self.camRunTime.emailConfig['smtp'],
                                                                                                   self.camRunTime.emailConfig['user'],
                                                                                                   frame_no_label_email,
                                                                                                   str(box[6]),
                                                                                                   'câmera (sem região definida)'))
                                                threadEmail.start()
                                                self.camRunTime.listObjectMailAlerted.append(objectID)
                                            else:
                                                alertaNaoEnviado = [self.camRunTime.emailConfig['name'],
                                                                      self.camRunTime.emailConfig['to'],
                                                                      self.camRunTime.emailConfig['subject'],
                                                                      self.camRunTime.emailConfig['port'],
                                                                      self.camRunTime.emailConfig['smtp'],
                                                                      self.camRunTime.emailConfig['user'],
                                                                      frame_no_label_email,
                                                                      str(box[6]),
                                                                      'câmera (sem região definida)', 
                                                                      objectID]

                                                self.camRunTime.pilhaAlertasNaoEnviados.append(alertaNaoEnviado)
                                                
                                                self.camRunTime.listObjectMailAlerted.append(objectID)

                                                log.critical('Sem conexao com a Internet - Alarmes serão enviados assim que houver conexao')
                                                log.critical('Numero de alarmes não enviados até o momento: {:d}'.format(len(self.camRunTime.pilhaAlertasNaoEnviados)))




                            #end loop objectTracking.items()
                    #end loop for box listObjects

                self.camRunTime.tEmptyEnd = time.time()
                self.camRunTime.tEmpty = self.camRunTime.tEmptyEnd - self.camRunTime.tEmptyStart
                #print('tEmpty end loop {}'.format(tEmpty))

                self.camRunTime.timeGravandoAll = time.time() - self.camRunTime.timeGravandoAllInit
                
                if not utils.isDiskFull(self.camRunTime.diskMinUsage):

                    if self.camRunTime.spaceMaxDirVideosOnAlarme == 0 or ( self.camRunTime.spaceMaxDirVideosOnAlarme >= utils.getDirUsedSpace(self.camRunTime.statusConfig.data["dirVideosOnAlarmes"]) ):

                        if self.camRunTime.newVideo and self.camRunTime.gravandoOnAlarmes and (self.camRunTime.STOP_ALL == False):
                        
                            if self.camRunTime.out_video is not None:
                               self.camRunTime.out_video.release()
                               self.camRunTime.out_video = None
                               self.camRunTime.releaseVideoOnAlarmes = False

                            #grava video novo se tiver um objeto novo na cena
                            hora = utils.getDate()['hour'].replace(':','-')
                            nameVideo = self.camRunTime.dir_video_trigger_on_alarmes + '/' + hora + '.avi'
                            
                            #if out_video is not None:
                            #h = nchw[2]
                            #w = nchw[3]
                            self.camRunTime.out_video = cv.VideoWriter(nameVideo, fourcc, FPS, (w,h))
                            self.camRunTime.out_video.write(frame_no_label)
                            self.camRunTime.newVideo = False

                        
                        #if gravando:
                        if self.camRunTime.gravandoOnAlarmes and (self.camRunTime.STOP_ALL == False):
                            if self.camRunTime.out_video is not None:
                                self.camRunTime.out_video.write(frame_no_label)

                    #espaço maximo na pasta VideosOnAlarmes atingido 
                    else:
                        #avisar por email 1x a cada X tempo ? 
                        if not self.camRunTime.emailSentFullVideosOnAlarmes:  
                            
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


                    if self.camRunTime.spaceMaxDirVideosAllTime == 0 or ( self.camRunTime.spaceMaxDirVideosAllTime >= utils.getDirUsedSpace(self.camRunTime.statusConfig.data["dirVideosAllTime"]) ):
                    
                        if self.camRunTime.gravandoAllTime and (self.camRunTime.STOP_ALL == False):
                            if self.camRunTime.out_video_all_time is not None:
                                self.camRunTime.out_video_all_time.write(frame_no_label)
                        
                        
                        if self.camRunTime.gravandoAllTime and (self.camRunTime.timeGravandoAll >= self.camRunTime.GRAVANDO_TIME) and (self.camRunTime.STOP_ALL == False):

                            if self.camRunTime.out_video_all_time is not None:
                                 self.camRunTime.out_video_all_time.release()
                                 self.camRunTime.out_video_all_time = None
                            
                            #if out_video_all_time is not None:
                            
                            hora = utils.getDate()['hour'].replace(':','-')
                            self.camRunTime.nameVideoAllTime = dir_video_trigger_all_time + '/' + hora + '.avi'
                            
                            #if out_video_all_time is not None:
                            #h = nchw[2]
                            #w = nchw[3]
                            self.camRunTime.out_video_all_time = cv.VideoWriter(nameVideoAllTime, fourcc, FPS, (w,h))
                            self.camRunTime.out_video_all_time.write(frame_no_label)

                            self.camRunTime.timeGravandoAllInit = time.time()
                                

                    else:
                        
                        if not self.camRunTime.emailSentFullVideosAllTime:  
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
                            self.camRunTime.emailSentFullVideosAllTime = True
                            #avisar por email 1x a cada X tempo ? 

                #disco cheio 
                else:

                    if not self.camRunTime.emailSentDiskFull:  
                        if self.camRunTime.eraseOldestFiles:
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
                    if self.camRunTime.eraseOldestFiles:

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
                                    self.camRunTime.emailSentdirVideosOnAlarmesEmpty = True

                    # ou então parar de gravar novos videos
                    elif self.camRunTime.stopSaveNewVideos:
                        self.camRunTime.gravandoAllTime = False
                        self.camRunTime.gravandoOnAlarmes = False


                #cv.imshow('frame', frame_screen)
                self.change_pixmap_signal.emit(frame_screen)

                self.camRunTime.end = time.time()

                self.camRunTime.renderTime = (self.camRunTime.end-self.camRunTime.start)*1000
                self.camRunTime.FPS = 1000/self.camRunTime.renderTime
                #print('render time: {:10.2f} ms'.format(renderTime))
                #print('FPS: {:10.2f} ms'.format(FPS))

                self.camRunTime.timeSessionEnd = time.time() 
                self.camRunTime.timeSession = self.camRunTime.timeSessionEnd - self.camRunTime.timeSessionInit
                
                #log.info('timeSession: {}'.format(timeSession))

                if self.camRunTime.timeSession >= self.camRunTime.CHECK_SESSION:

                    session = {self.camRunTime.login['user'], self.camRunTime.login['token']}

                    conexao = utils.checkInternetAccess()

                    if conexao: 

                        log.debug('Conexao com a Internet estabelecida')
                        self.camRunTime.STOP_ALL = False

                        while (len(self.camRunTime.pilhaAlertasNaoEnviados) > 0) and (self.camRunTime.STOP_ALL == False):  
                            #enviando alerta de emails anteriores

                            alertaEmail = self.camRunTime.pilhaAlertasNaoEnviados.popleft()

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
                        self.camRunTime.sessionStatus, self.camRunTime.error = checkSessionPv(self.camRunTime.login)
                        self.camRunTime.timeInternetOffStart = time.time() 

                        if self.camRunTime.error == 'servidorOut':
                            log.critical('Servidor não respondendo. Ignorando checkSession')
                            self.camRunTime.sessionStatus = True
                       
                        elif self.camRunTime.sessionStatus == False:
                            log.warning('sessionStatus: {}'.format(self.camRunTime.sessionStatus))
                            log.warning('stopWatchDog chamado')
                            utils.stopWatchDog()


                    else:
                        log.critical("Sem internet - sessao não checada")
                        log.critical("sessionStatus: {}".format(self.camRunTime.sessionStatus))
                       
                        if (time.time() - self.camRunTime.timeInternetOffStart) >= self.camRunTime.INTERNET_OFF: 
                            
                            STOP_ALL = True 
                            #release dos videos
                            if self.camRunTime.out_video is not None:
                               self.camRunTime.out_video.release()
                               self.camRunTime.out_video = None
                               self.camRunTime.releaseVideoOnAlarmes = False
                            
                            if self.camRunTime.out_video_all_time is not None:
                                 self.camRunTime.out_video_all_time.release()
                                 self.camRunTime.out_video_all_time = None
                                 self.camRunTime.releaseVideoAllTime = False


                            log.critical('Tempo maximo sem Internet permitido esgotado - Portao Virtual ficará inativo')
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Information)
                            msg.setWindowTitle("Sem conexão com a Internet")
                            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                            msg.setText("Tempo maximo de 3 horas sem conexão com a Internet atingido - Portao Virtual ficará inativo, mostrando somente as imagens")
                            msg.exec()
                            #desativar funcoes

                        #emitir mensagem de aviso
                        self.camRunTime.sessionStatus = True

                    self.camRunTime.timeSessionInit = time.time()

                
                self.camRunTime.listObjects.clear()
                #listObjectsTracking.clear()

                #chamando callbackButtonRegioes  
                if cv.waitKey(1) & 0xFF == ord('c'):
                    self.camRunTime.pausaConfig = True
                    callbackButtonRegioes(None, ret)
                
                if cv.waitKey(1) & 0xFF == ord('q'):
                    utils.stopWatchDog()
                    break

            else:
                if not self.camRunTime.conectado:
                    log.warning('Reconectando em 5 segundos...')
                    #init_video = False
                    time.sleep(5)
                    self.camRunTime.ipCam, self.camRunTime.error = utils.camSource(source)
                    self.camRunTime.ipCam.set(3, RES_X)
                    self.camRunTime.ipCam.set(4, RES_Y)
                    #ipCam = utils.camSource(source)
                else:
                    log.warning('Reconectando em 5 segundos...')
                    self.camRunTime.initOpenVino() 
                    time.sleep(5)

    def stop(self):
        #"""Sets run flag to False and waits for thread to finish"""
        if self.camRunTime.out_video is not None:
            log.warning('Fim da captura de video out_video_all_time')
            self.camRunTime.out_video.release()

        if self.camRunTime.out_video_all_time is not None:
            log.warning('Fim da captura de video out_video_all_time')
            self.camRunTime.out_video_all_time.release()


        if ipCam and cv is not None:
            log.info('ipCam release and cv.destroyAllWindows') 
            ipCam.release()
            cv.destroyAllWindows()

        self._run_flag = False
        self.wait()






