import cv2 as cv
import numpy as np
#from datetime import date
import time
from objectTracking.pyimagesearch.centroidtracker import CentroidTracker
from Utils_tracking import sendMailAlert
from Utils_tracking import sendAlertApp

from Utils_tracking import saveImageBox
import utilsCore as utils
import logging as log
import sys
from collections import deque
import os
import subprocess
import getpass
import shutil
from rtsp_discover.rtsp_discover import CamFinder
#import ffmpeg
from threading import Thread
from objectDetectionTensorFlow import objectDetection 
from objectDetectionTensorFlow import objectDetectionYolo
import secrets
import psutil
#import pluginOpenVino as pOpenVino
from utilsCore import checkInternetAccess
from matplotlib.path import Path
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from checkLicence.sendingData import checkSessionPv

import firebase_admin
from firebase_admin import credentials

#import tensorflow as tf

#cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, FPS, (1280,720))




class InferenceCore(QThread):

    change_pixmap_signal = pyqtSignal(np.ndarray)
    #updateStorageInfo = pyqtSignal()
    #storageFull = pyqtSignal()
    warningSessionLoss = pyqtSignal()
    warningSessionLossFirst = pyqtSignal()
    webCamWarning = pyqtSignal()
    camEmptyWarning = pyqtSignal()
    camRunTime = None
    #isDiskFull = False
    
    cred = {
      "type": "service_account",
      "project_id": "pvalarmes-3f7ee",
      "private_key_id": "4563d30a50f6b0e7dcc46291396761e2a62b2198",
      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDD1w6dONroiO/4\nyK/4nRqkTFPOa1FnNzbHHkKv5QwHN2KxezVY4dB75LuKfwC2lTwbBB182kLYABDZ\nw/qAWV96j6qDKPVK5BBs75xJixeuMTY3Cz0ChA74wIp4eC2iXws91zvJiDIC3Ox/\nNdEKKIuYtOagh6o8P7UOE1S/k3ywNe2u5SN7e5CNnqHW2iGR4P+RocNuV3WfeTSV\n7OEVMlOomA8z6nvBMU36B+KQL/XSP5pPPXd3kHl38OG0EFGGUPzCBc8vSFSdabWk\nDAmgHlk1TYZjOeasMSNBhjZDbmadtRl3OAE2KrykQV4YXdcVuMOnh9O86sP/U83x\nTjof5CLdAgMBAAECggEAA/OBk7n7LrBemRghdsRirnhsw3AmXQz/4a4SXd6i6r1b\nFCYeeivaKzm+7+kmkEh8BTaEyslTimyb6mzaD79d3gjqgYlww4FM9Im0D0bLZEQR\najRjl3qnG600zf/succtoKKITgVdrvGaoulozYnqYRsbQRdjn6IQateIgPH+lMaE\ntveBBQqu+AELnYxr5sDgbtdCeFbXFL6sTjxssl3hNQPTCcJisuOnqxX/2RhJyR3Z\nVhtqSHQcuM5TtJkV0qjK0gjmTNGAZaCaNjj0oTWbBAvIlOzYzFYkUq8XUvO//Lra\nG61FmijqrpTQs/CVMRhoEM/OuXZCfR/Hnd4XeDWVKQKBgQDuLRuwEvr6OsIHIxUZ\n1ZJIXvjFBPBo69s0dnNM966ia6Jo9RewAyAc6uVcG8Pw8TSOb0OXz2gSNp5312Kn\nANc25OFSaGTt9kKG6omD/ILZ+TvhzORD+pgSybPLM5EPW69Bs+Rwrh6tHVnMc06w\nDGMJk4Xp1QvtKTEcdCHs2ai7iQKBgQDSfuOK03sE1pw0v6ti/RB7hipQJObMgPBr\nfzf1QDQ/8tl4DalSu1YnYWLpwhTSOGIhnbaE1MG1P0eRtjDNqZwkebrbaOGFHxgc\ntFjHh/j3fDFF9/nSSUEJubbTy9hRmUZk/tYNOqXp95X0uTAKZWztxytKao9S3aJh\nZyh2EVFztQKBgQDUNaytvLuRqDioU0HBuuCTSssr/7KUSVEN9VvV//jBDlWuXnG0\niZRbL48b+kEitEa3gbsfz9RSJggbjvR/B+i5KET6P7ltrDSqMN5Fkv6jZ8VK8luP\nlf9Y/g4Lxu5AWNhWGgo3u2vponUYDMTXZrH3HlH6fbAaptDzISX4+hW0wQKBgQCV\nrquJzca98wpTLDToiEIPRKGUKhmBNPNBzc5x9Lzy+HMSPsy4SwUBrevThDKgJn4J\nn4fpvw0cIKp5AFCF/uVMvs9UNKmhqzHPP6OeB5/QBR1YvvSER5kbHFfZFix2IgN/\n0ANQlvLihC+7PXDfA67JCwdKvKm8aGSO1PddtgTwvQKBgQC63E2CwORx9KtYeBgI\nRbWnCVUb67K3WCS9bu5Yd5Gfc5IXBQChUg19645wNW7Vqxo1YiAbDO0SobOOn7iL\nIlOy2xWj+klRFMk6MoZ5rNcUJD6xAcq7K8mOORk3uVQ2ccbuq8MTrx3BL7FV+UqO\niw54w17h/4bR1e96Y0eM5ojCWw==\n-----END PRIVATE KEY-----\n",
      "client_email": "firebase-adminsdk-slpxb@pvalarmes-3f7ee.iam.gserviceaccount.com",
      "client_id": "106587989855928727506",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-slpxb%40pvalarmes-3f7ee.iam.gserviceaccount.com"
    }



    def __init__(self):
        super().__init__()
        self._run_flag = True
        log.info('InferenceCore:: __init__')              
        
        log.info('InferenceCore:: carregando Certificado Firebase')
        try:
            credential = credentials.Certificate(self.cred)
        except Exception as err:
            log.critical('InferenceCore:: Certificado não encontrado - Erro: {} '.format(err))
        else:        
            log.info('InferenceCore:: Inicializando Firebase')
        
            try:
                firebase_admin.initialize_app(credential, {'storageBucket': 'pvalarmes-3f7ee.appspot.com'})
            except Exception as err:
                log.critical('Erro ao inicializar o Firebase: {}'.format(err))            
            else:
                log.info('Firebase inicializado com sucesso')
        
        
    def setCamRunTime(self, camRunTime):
        log.info('::setCamRunTime')
        self.camRunTime = camRunTime
        #print('setCamRunTime:: nameCam: {}'.format(self.camRunTime.nameCam))

    def isIdInsideRegion(self, centroid, ref_point_polygon):
        path = Path(ref_point_polygon)
        mask = path.contains_points([(centroid[0], centroid[1])])
        return mask

    def setPointSelection(self, x, y):
        self.camRunTime.ref_point_polygon.append([x, y])
        #self.camRunTime.cropPolygon = True


    def polygonSelection(self, event, x, y, flags, param):         

        if event == cv.EVENT_LBUTTONDBLCLK and not self.camRunTime.portaoVirtualSelecionado:  
            
            self.camRunTime.ref_point_polygon.append([x, y])
            self.camRunTime.cropPolygon = True

        elif not self.camRunTime.portaoVirtualSelecionado and flags == 0:

            self.camRunTime.portaoVirtualSelecionado = True

    def initOpenVino(self):
        
        
        ### ---------------  OpenVino Init ----------------- ###
        
        if self.camRunTime.isOpenVino:

            log.info('initOpenVino')            
        
            if self.camRunTime.ipCam is not None:
                self.camRunTime.ret, self.camRunTime.frame = self.camRunTime.ipCam.read()                
                self.camRunTime.ret, self.camRunTime.next_frame = self.camRunTime.ipCam.read()
            
            if self.camRunTime.frame is not None:
                self.camRunTime.frame = cv.resize(self.camRunTime.frame, (self.camRunTime.RES_X, self.camRunTime.RES_Y))             
                self.camRunTime.next_frame = cv.resize(self.camRunTime.next_frame, (self.camRunTime.RES_X, self.camRunTime.RES_Y)) 
        
            self.camRunTime.cvNetTensorFlow = None
            
            log.info('inferenceCore:: Tentando carregar Openvino')
            try:
                self.camRunTime.nchw, self.camRunTime.exec_net, self.camRunTime.input_blob, self.camRunTime.out_blob = \
                    pOpenVino.initOpenVino(self.camRunTime.device, self.camRunTime.openVinoModelXml, \
                    self.camRunTime.openVinoModelBin, self.camRunTime.openVinoCpuExtension, self.camRunTime.openVinoPluginDir)
        
            except:
                
                log.critical('inferenceCore:: Erro ao iniciar OpenVino - checar arquivo de configuracao')                
                self.camRunTime.initOpenVinoStatus = False
                
                log.critical('inferenceCore:: Tentando carregar TensorFlow')                
                try:                    
                    self.camRunTime.cvNetTensorFlow = cv.dnn.readNetFromTensorflow(self.camRunTime.pb, self.camRunTime.pbtxt)
                    self.camRunTime.cvNetTensorFlow = cv.dnn.readNetFromTensorflow(self.camRunTime.pb, self.camRunTime.pbtxt)                                        
                  
                except Exception as err:
                    log.critical('inferenceCore:: Erro ao carregar TensorFlow apos falha do Openvino - Erro: {}'.format(err))                    
                    self.camRunTime.init_video = False                    
                else:
                    log.info("inferenceCore:: TensorFlow carregado")
                    self.camRunTime.init_video = True                    
                
                
            else:
                log.info('inferenceCore:: Openvino carregado')
                self.camRunTime.initOpenVinoStatus = True
                self.camRunTime.init_video = True
                log.info(' ')
                self.camRunTime.cur_request_id = 0
                self.camRunTime.next_request_id = 1
                self.camRunTime.render_time = 0
        
        else:
            log.info("inferenceCore:: OpenCV DNN")
            self.camRunTime.init_video = True
            self.camRunTime.initOpenVinoStatus = False
            
            log.info('inferenceCore:: Tentando carregar TensorFlow')                
            try:

                #self.camRunTime.cvNetTensorFlow = cv.dnn.readNet(self.camRunTime.pb + '.bin', self.camRunTime.pb + '.xml')
                self.camRunTime.cvNetTensorFlow = cv.dnn.readNet(self.camRunTime.pb + '.weights', self.camRunTime.pb + '.cfg')
                self.camRunTime.cvNetTensorFlow.setPreferableBackend(cv.dnn.DNN_BACKEND_INFERENCE_ENGINE)
                self.camRunTime.cvNetTensorFlow.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
              
            except Exception as err:
                log.critical('inferenceCore:: Erro ao carregar TensorFlow Erro: {}'.format(err))
                self.camRunTime.init_video = False                    
            else:
                log.info("inferenceCore:: TensorFlow carregado")
                self.camRunTime.init_video = True 
            
        
        if self.camRunTime.ipCam is not None:
            (self.camRunTime.conectado, self.camRunTime.frame) = self.camRunTime.ipCam.read()
        
        if self.camRunTime.frame is not None:
            self.camRunTime.frame = cv.resize(self.camRunTime.frame, (self.camRunTime.RES_X, self.camRunTime.RES_Y)) 
            self.camRunTime.w  = self.camRunTime.frame.shape[0]
            self.camRunTime.h = self.camRunTime.frame.shape[1]

        self.camRunTime.timeSessionInit = time.time()
        self.camRunTime.timeGravandoAllInit = time.time()
        self.camRunTime.timeInternetOffStart = time.time()
        
        self.camRunTime.hora = utils.getDate()['hour'].replace(':','-')
        self.camRunTime.nameVideoAllTime = self.camRunTime.dir_video_trigger_all_time + '/' + self.camRunTime.hora + '.avi'
        
        
        self.camRunTime.out_video_all_time = cv.VideoWriter(self.camRunTime.nameVideoAllTime, self.camRunTime.fourcc, self.camRunTime.FPS, (self.camRunTime.w, self.camRunTime.h))

    def run(self):
    
        
        log.info('inferenceCore:: run')
        self.initOpenVino()        
        
        

        while True:
        
            # print('init_video: {}'.format(self.camRunTime.init_video))
            # print('sessionStatus: {}'.format(self.camRunTime.sessionStatus))
            # print('rtspStatus: {}'.format(self.camRunTime.rtspStatus))
            # print('conectado: {}'.format(self.camRunTime.conectado))
            
            # print(' ')
        
            if self.camRunTime.init_video and self.camRunTime.sessionStatus and self.camRunTime.rtspStatus :
            
                
                #print('...')            

                #if counter == 0:
                #    startFps = time.time()

                self.camRunTime.start = time.time()
                #log.info('while')
                

                if self.camRunTime.ipCam is not None:
                    self.camRunTime.conectado, self.camRunTime.frame = self.camRunTime.ipCam.read()
                    self.camRunTime.conectado, frame = self.camRunTime.ipCam.read()
                
                if self.camRunTime.frame is not None:
                    self.camRunTime.frame = cv.resize(self.camRunTime.frame, (self.camRunTime.RES_X, self.camRunTime.RES_Y)) 
                            

                
                #if (self.camRunTime.conectado) and (self.camRunTime.frame is not None) and (self.camRunTime.next_frame is not None):
                if (self.camRunTime.conectado) and (self.camRunTime.frame is not None):
                    
                    try:
                        frame_no_label = self.camRunTime.frame.copy()                
                        frame_screen = self.camRunTime.frame.copy()                
                        frame_no_label_email = self.camRunTime.frame.copy()
                    except:
                        log.error('inferenceCore:: erro copiar frame')

                    #objects = ct.update(rects = listObjectsTracking)

                    self.camRunTime.currentData = utils.getDate()
                    self.camRunTime.currentData = [self.camRunTime.currentData.get('day'), self.camRunTime.currentData.get('month')]

                    if self.camRunTime.current_data_dir != self.camRunTime.currentData:
                        self.camRunTime.status_dir_criado_on_alarmes, self.camRunTime.dir_video_trigger_on_alarmes = utils.createDirectory(self.camRunTime.statusConfig.data["dirVideosOnAlarmes"])
                        self.camRunTime.status_dir_criado_all_time, self.camRunTime.dir_video_trigger_all_time = utils.createDirectory(self.camRunTime.statusConfig.data["dirVideosAllTime"])
                        self.camRunTime.current_data_dir = utils.getDate()
                        self.camRunTime.current_data_dir = [self.camRunTime.current_data_dir.get('day'), self.camRunTime.current_data_dir.get('month')]

                    #desenhando regioes
                    for r in self.camRunTime.regions:
                         pts = np.array(r.get("pointsPolygon"), np.int32)
                         pts = pts.reshape((-1,1,2))
                         cv.polylines(frame_screen,[pts],True,(0,0,255), 2)

                    if self.camRunTime.cropPolygon:
                        #log.info('if cropPolygon')
                        pts = np.array(self.camRunTime.ref_point_polygon, np.int32)
                        pts = pts.reshape((-1,1,2))
                        cv.polylines(frame_screen,[pts],True,(0,0,255), 2)


                    #passando o Frame selecionado do portao para deteccao somente se o portao virtual estiver selecionado                
                    if self.camRunTime.portaoVirtualSelecionado and (self.camRunTime.STOP_ALL == False):
                        #print('iniciando detecção')

                        #se eh openVino e este foi inicializado corretamente 
                        ### ---------------  OpenVino Get Objects ----------------- ###
                        if self.camRunTime.isOpenVino and self.camRunTime.initOpenVinoStatus:
                        

                            #print('pOpenVino.getListBoxDetected')
                            self.camRunTime.ret, listReturn  = pOpenVino.getListBoxDetected(self.camRunTime.ipCam, self.camRunTime.device, self.camRunTime.frame,
                                               self.camRunTime.next_frame, self.camRunTime.nchw, self.camRunTime.exec_net, self.camRunTime.out_blob,
                                               self.camRunTime.input_blob, self.camRunTime.cur_request_id, self.camRunTime.next_request_id, 
                                               self.camRunTime.prob_threshold, self.camRunTime.RES_X, self.camRunTime.RES_Y)

                            if self.camRunTime.ret:
                                #print('self.camRunTime.ret')
                                self.camRunTime.frame = self.camRunTime.next_frame
                                self.camRunTime.frame, self.camRunTime.next_frame, self.camRunTime.cur_request_id, \
                                self.camRunTime.next_request_id, self.camRunTime.listObjects, self.camRunTime.listObjectsTracking, \
                                self.camRunTime.prob_threshold_returned  = listReturn[0], listReturn[1], listReturn[2], listReturn[3], listReturn[4], listReturn[5], listReturn[6]

                                self.camRunTime.cur_request_id, self.camRunTime.next_request_id = self.camRunTime.next_request_id, self.camRunTime.cur_request_id

                        else:
                            #chamada para a CNN do OpenCV - TensorFlow Object Detection API 
                            #log.info("inferenceCore:: TensorFlow openCV API")
                            
                            self.camRunTime.frame = cv.resize(self.camRunTime.frame, (self.camRunTime.RES_X, self.camRunTime.RES_Y))                                
                                
                            self.camRunTime.listObjects, self.camRunTime.listObjectsTracking  = objectDetectionYolo(self.camRunTime.frame, self.camRunTime.cvNetTensorFlow)
                            # self.camRunTime.listObjects, self.camRunTime.listObjectTradking  = objectDetection(self.camRunTime.frame, \
                                                                                               # self.camRunTime.idObjeto, self.camRunTime.listRectanglesDetected, \
                                                                                               # self.camRunTime.detection,  self.camRunTime.rows, \
                                                                                               # self.camRunTime.cols, self.camRunTime.cvNetTensorFlow)

                    #sem detecção de objetos
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
                        #print('objetos detectados')

                        #objectsTracking = ct.update(listObjectsTracking)

                        for box in self.camRunTime.listObjects:
                        
                            #print('box objectsTracking: {}'.format(box))
                            #print(' ')

                            if self.camRunTime.portaoVirtualSelecionado:

                                #objetos com ID e centro de massa
                                self.camRunTime.objectsTracking = self.camRunTime.ct.update(self.camRunTime.listObjectsTracking)

                                for (objectID, centroid) in self.camRunTime.objectsTracking.items():

                                    # ajustando posicao do centroid 

                                    #desenhando o box e label
                                    #cv.rectangle(frame_screen, (int(box[0]), int(box[1]) ), (int(box[2]), int(box[3])), (23, 230, 210), thickness=2)
                                    cv.rectangle(frame_screen, (box[0], box[1] ), (box[2], box[3]), (23, 230, 210), thickness=2)
                                    
                                    
                                    top = box[1]
                                    y = top - 15 if top - 15 > 15 else top + 15
                                    cv.putText(frame_screen, str(box[4]), (int(box[0]), int(y)),cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
                                    text = "ID {}".format(objectID)
                                    cv.putText(frame_screen, text, (centroid[0] - 10, centroid[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                    cv.circle(frame_screen, (centroid[0], centroid[1]), 3, (0, 255, 0), -1)

                                    #checando tipo objeto
                                    typeObject = str(box[6])
                                    
                                    self.camRunTime.prob_threshold_returned = box[7]

                                    #checando para varias regioes
                                    if len(self.camRunTime.regions) != 0:
                                        for r in self.camRunTime.regions:                                           

                                            if r.get('objectType').get(typeObject) == "True":

                                                if self.camRunTime.prob_threshold_returned >= int(r.get('prob_threshold')):

                                                    #evitar regioes que foram inseridas sem determinar o box pela GUI
                                                    if len(r.get('pointsPolygon')) >= 3:
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

                                                                        if self.camRunTime.tSoundLimit > 0:

                                                                            self.camRunTime.tSoundEnd = time.time()
                                                                            self.camRunTime.tSound = self.camRunTime.tSoundEnd - self.camRunTime.tSoundStart

                                                                            if self.camRunTime.tSound < self.camRunTime.tSoundLimit:
                                                                                self.camRunTime.stopSound = True
                                                                            else:
                                                                                self.camRunTime.stopSound = False
                                                                                self.camRunTime.tSoundLimit = 0

                                                                        if a.get('isSoundAlert') == "True" and not self.camRunTime.stopSound:
                                                                            
                                                                            #evitar campainhas seguidas para mesmo objeto
                                                                            if self.camRunTime.listObjectSoundAlerted.count(objectID) == 0:
                                                                                log.info('inferenceCore:: campainha tocada')
                                                                                utils.playSound()
                                                                                self.camRunTime.listObjectSoundAlerted.append(objectID)

                                                                        if a.get('isEmailAlert') == "True":

                                                                            #evitar emails seguidos para mesmo objeto
                                                                            if self.camRunTime.listObjectMailAlerted.count(objectID) == 0:

                                                                                log.info('inferenceCore:: Enviando alerta por email')
                                                                                #salvando foto para treinamento
                                                                                #crop no box
                                                                                #left, top, right, bottom
                                                                                #frame_no_label = frame_no_label[int(box[1])-10:int(box[1]) + int(box[3]) , int(box[0])+10:int(box[2])]
                                                                                #saveImageBox(frame_no_label, str(box[6]))

                                                                                if utils.checkInternetAccess():

                                                                                    
                                                                                    if self.camRunTime.configEmailStatus and not self.camRunTime.desativarAlarmes:
                                                                                        log.info('inferenceCore:: Alerta enviado ID[' + str(objectID) + ']' + 'Tipo: ' + str(typeObject))
                                                                                        threadEmail = Thread(target=sendMailAlert, args=(self.camRunTime.emailConfig['name'],
                                                                                                                                           self.camRunTime.emailConfig['to'],
                                                                                                                                           self.camRunTime.emailConfig['subject'],
                                                                                                                                           self.camRunTime.emailConfig['servidorEmail'],
                                                                                                                                           self.camRunTime.emailConfig['user'],
                                                                                                                                           frame_no_label_email,
                                                                                                                                           str(typeObject), #tipo de objeto detectado
                                                                                                                                           r.get('nameRegion'),
                                                                                                                                           self.camRunTime.nameCam))
                                                                                        #print('inferenceCore:: threadEmail nameCam: {}'.format(self.camRunTime.nameCam))
                                                                                        threadEmail.start()
                                                                                    else:
                                                                                        log.critical('inferenceCore:: configEmailStatus: '.format(self.camRunTime.configEmailStatus))
                                                                                        
                                                                                        
                                                                                    #mensagem ao app é enviado de qualquer forma
                                                                                    threadAlertApp = Thread(target=sendAlertApp, args=(self.camRunTime.statusConfig.getUserLogin(),
                                                                                                                                           frame_no_label_email,
                                                                                                                                           str(typeObject), #tipo de objeto detectado
                                                                                                                                           r.get('nameRegion'),
                                                                                                                                           self.camRunTime.nameCam))
                                                                                    threadAlertApp.start()
                                                                                        
                                                                                        
                                                                                        
                                                                                    
                                                                                    
                                                                                    
                                                                                    self.camRunTime.listObjectMailAlerted.append(objectID)
                                                                                else:
                                                                                    alertaNaoEnviado = [self.camRunTime.emailConfig['name'],
                                                                                                          self.camRunTime.emailConfig['to'],
                                                                                                          self.camRunTime.emailConfig['subject'],
                                                                                                          self.camRunTime.emailConfig['servidorEmail'],
                                                                                                          self.camRunTime.emailConfig['user'],
                                                                                                          frame_no_label_email,
                                                                                                          str(typeObject),
                                                                                                          r.get('nameRegion'),
                                                                                                          self.camRunTime.nameCam]

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
                                        #log.info('camRunTime:: Objeto detectado sem regiao configurada')

                                        #evitar emails seguidos para mesmo objeto
                                        if self.camRunTime.listObjectMailAlerted.count(objectID) == 0:
                                            
                                            
                                            #60% acuracia padrao 
                                            if self.camRunTime.prob_threshold_returned >= 60:

                                                self.camRunTime.tEmptyEnd = time.time()
                                                self.camRunTime.tEmpty = self.camRunTime.tEmptyEnd - self.camRunTime.tEmptyStart

                                                self.camRunTime.tEmptyStart = time.time()

                                                #enquanto tiver objetos dentro da regiao o video eh gravado, independente do alarme
                                                 
                                                if self.camRunTime.statusConfig.data["isRecordingOnAlarmes"] == 'True':
                                                    self.camRunTime.gravandoOnAlarmes = True
                                                                                               
                                                
                                                log.info('inferenceCore:: Enviando alerta por email - sem regiao configurada')

                                                if utils.checkInternetAccess():
                                                    
                                                    if self.camRunTime.configEmailStatus and not self.camRunTime.desativarAlarmes:
                                                        log.info('inferenceCore:: Alerta enviado ID[' + str(objectID) + ']')
                                                        threadEmail = Thread(target=sendMailAlert, args=(self.camRunTime.emailConfig['name'],
                                                                                                           self.camRunTime.emailConfig['to'],
                                                                                                           self.camRunTime.emailConfig['subject'],
                                                                                                           self.camRunTime.emailConfig['servidorEmail'],
                                                                                                           self.camRunTime.emailConfig['user'],
                                                                                                           frame_no_label_email,
                                                                                                           str(typeObject),
                                                                                                           '(sem região definida)',
                                                                                                           self.camRunTime.nameCam))
                                                        threadEmail.start()
                                                    else:
                                                        log.critical('inferenceCore:: configEmailStatus: '.format(self.camRunTime.configEmailStatus))
                                                        
                                                        
                                                    log.info('inferenceCore:: Enviando alerta para o App - sem regiao configurada')
                                                    threadAlertApp = Thread(target=sendAlertApp, args=(self.camRunTime.statusConfig.getUserLogin(),
                                                           frame_no_label_email,
                                                           str(typeObject), #tipo de objeto detectado
                                                           r.get('nameRegion'),
                                                           self.camRunTime.nameCam))
                                                    threadAlertApp.start()
                                                        
                                                        
                                                    
                                                    
                                                    self.camRunTime.listObjectMailAlerted.append(objectID)
                                                else:
                                                    alertaNaoEnviado = [self.camRunTime.emailConfig['name'],
                                                                          self.camRunTime.emailConfig['to'],
                                                                          self.camRunTime.emailConfig['subject'],
                                                                          self.camRunTime.emailConfig['servidorEmail'],
                                                                          self.camRunTime.emailConfig['user'],
                                                                          frame_no_label_email,
                                                                          str(typeObject),
                                                                          "(sem região definida)",                                                                       
                                                                          self.camRunTime.nameCam]

                                                    self.camRunTime.pilhaAlertasNaoEnviados.append(alertaNaoEnviado)
                                                    
                                                    self.camRunTime.listObjectMailAlerted.append(objectID)

                                                    log.critical('inferenceCore:: Sem conexao com a Internet - Alarmes serão enviados assim que houver conexao')
                                                    log.critical('inferenceCore:: Numero de alarmes não enviados até o momento: {:d}'.format(len(self.camRunTime.pilhaAlertasNaoEnviados)))




                                #end loop objectTracking.items()
                        #end loop for box listObjects

                    self.camRunTime.tEmptyEnd = time.time()
                    self.camRunTime.tEmpty = self.camRunTime.tEmptyEnd - self.camRunTime.tEmptyStart
                    #print('tEmpty end loop {}'.format(self.camRunTime.tEmpty))

                    self.camRunTime.timeGravandoAll = time.time() - self.camRunTime.timeGravandoAllInit
                    
                    
                    if not self.camRunTime.isDiskFull:
                   
                        
                        if self.camRunTime.spaceMaxDirVideosOnAlarme == 0 or ( self.camRunTime.spaceMaxDirVideosOnAlarme >= self.camRunTime.dirVideosOnAlarmesUsedSpace ):

                            if self.camRunTime.newVideo and self.camRunTime.gravandoOnAlarmes and (self.camRunTime.STOP_ALL == False):
                            
                                if self.camRunTime.out_video is not None:
                                   self.camRunTime.out_video.release()
                                   self.camRunTime.out_video = None
                                   self.camRunTime.releaseVideoOnAlarmes = False

                                #grava video novo se tiver um objeto novo na cena
                                hora = utils.getDate()['hour'].replace(':','-')
                                self.camRunTime.nameVideo = self.camRunTime.dir_video_trigger_on_alarmes + '/' + hora + '.avi'
                                
                                #if out_video is not None:
                                #h = nchw[2]
                                #w = nchw[3]
                                self.camRunTime.out_video = cv.VideoWriter(self.camRunTime.nameVideo, self.camRunTime.fourcc, self.camRunTime.FPS, (self.camRunTime.w, self.camRunTime.h))
                                self.camRunTime.out_video.write(frame_no_label)
                                self.camRunTime.newVideo = False

                            
                            #if gravando:
                            if self.camRunTime.gravandoOnAlarmes and (self.camRunTime.STOP_ALL == False):
                                if self.camRunTime.out_video is not None:
                                    #print('gravandoOnAlarmes')
                                    self.camRunTime.out_video.write(frame_no_label)

                       


                        if self.camRunTime.spaceMaxDirVideosAllTime == 0 or ( self.camRunTime.spaceMaxDirVideosAllTime >= self.camRunTime.dirVideosAllTimeUsedSpace ):                        
                            
                            if self.camRunTime.gravandoAllTime and (self.camRunTime.timeGravandoAll >= self.camRunTime.GRAVANDO_TIME) and (self.camRunTime.STOP_ALL == False):

                                if self.camRunTime.out_video_all_time is not None:
                                     self.camRunTime.out_video_all_time.release()
                                     self.camRunTime.out_video_all_time = None
                                
                                #if out_video_all_time is not None:
                                
                                hora = utils.getDate()['hour'].replace(':','-')
                                self.camRunTime.nameVideoAllTime = self.camRunTime.dir_video_trigger_all_time + '/' + hora + '.avi'
                                
                                #if out_video_all_time is not None:
                                #h = nchw[2]
                                #w = nchw[3]
                                
                                
                                self.camRunTime.out_video_all_time = cv.VideoWriter(self.camRunTime.nameVideoAllTime, self.camRunTime.fourcc, self.camRunTime.FPS, (self.camRunTime.w, self.camRunTime.h))
                                self.camRunTime.out_video_all_time.write(frame_no_label)

                                self.camRunTime.timeGravandoAllInit = time.time()
                                    
                        if self.camRunTime.gravandoAllTime and (self.camRunTime.STOP_ALL == False):
                            if self.camRunTime.out_video_all_time is not None:
                                #print('gravandoAllTime')
                                #print('out_video_all_time type: {}'.format(self.camRunTime.out_video_all_time))                            
                                self.camRunTime.out_video_all_time.write(frame_no_label)
                   

                    #disco cheio 
                    else:
                        #print('disco cheio')
                        # ou então parar de gravar novos videos
                        if self.camRunTime.stopSaveNewVideos:                        
                            self.camRunTime.gravandoAllTime = False
                            self.camRunTime.gravandoOnAlarmes = False
                            
                       
                        
                    
                    #end else disco cheio  
                                
                    self.change_pixmap_signal.emit(frame_screen)                    
                    #self.change_pixmap_signal.emit(self.camRunTime.frame)
                    #print('emit')

                    self.camRunTime.end = time.time()

                    
                    self.camRunTime.renderTime = (self.camRunTime.end - self.camRunTime.start)*1000
                    if (self.camRunTime.renderTime > 0):
                        self.camRunTime.FPS = 1000/self.camRunTime.renderTime
                    
                    #print('render time: {:10.2f} ms'.format(renderTime))
                    #print('FPS: {:10.2f} FPS'.format(self.camRunTime.FPS))

                    self.camRunTime.timeSessionEnd = time.time() 
                    self.camRunTime.timeSession = self.camRunTime.timeSessionEnd - self.camRunTime.timeSessionInit
                    
                    #log.info('timeSession: {}'.format(timeSession))

                    #print('ANTES testando sessao')
                    if self.camRunTime.timeSession >= self.camRunTime.CHECK_SESSION:
                        #print('timeSession > CHECK_SESSION')

                        #session = {self.camRunTime.login.get('user'), self.camRunTime.login.get('token')}

                        conexao = utils.checkInternetAccess()

                        if conexao: 

                            log.info(' ')
                            log.info('inferenceCore:: Conexao com a Internet estabelecida')
                            #print('Conexao com a Internet estabelecida')
                            self.camRunTime.STOP_ALL = False
                            
                            while (len(self.camRunTime.pilhaAlertasNaoEnviados) > 0) and (self.camRunTime.STOP_ALL == False):  
                            
                                if self.camRunTime.configEmailStatus and not self.camRunTime.desativarAlarmes:                            
                                    #enviando alerta de emails anteriores
                                    log.info('inferenceCore:: Enviando alerta de emails anteriores')

                                    alertaEmail = self.camRunTime.pilhaAlertasNaoEnviados.popleft()

                                    threadEmail = Thread(target=sendMailAlert, args=(alertaEmail[0],
                                    alertaEmail[1],
                                    alertaEmail[2],
                                    alertaEmail[3],
                                    alertaEmail[4],
                                    alertaEmail[5],
                                    alertaEmail[6],
                                    alertaEmail[7],
                                    alertaEmail[8],
                                    alertaEmail[9]))                                    
                                    
                                    log.info('inferenceCore:: Email de alerta durante perda de conexao enviado. pilha: {}'.format(len(pilhaAlertasNaoEnviados)))
                                    threadEmail.start()
                                else:
                                    log.critical('inferenceCore:: configEmailStatus: '.format(self.camRunTime.configEmailStatus))
                                
                                #Alertas pra o App sao enviados de qualquer forma
                                log.info('inferenceCore:: Lista de alertas devido a perda de conexao enviados ao App pilha: {}'.format(len(pilhaAlertasNaoEnviados)))
                                threadAlertApp = Thread(target=sendAlertApp, args=(self.camRunTime.statusConfig.getUserLogin(),
                                                           frame_no_label_email,
                                                           str(typeObject), #tipo de objeto detectado
                                                           r.get('nameRegion'),
                                                           self.camRunTime.nameCam))
                                threadAlertApp.start()
                                    
                                    
                                #print('Email de alerta durante perda de conexao enviado. pilha: {}'.format(len(pilhaAlertasNaoEnviados)))
                                    

                            
                             
                            #listObjectMailAlerted.append(alertaEmail[9])

                            #ativar funcoes                        
                            #self.camRunTime.sessionStatus, self.camRunTime.error = checkSessionPv(self.camRunT im h0 ek0.login)
                            #log.info('inferenceCore::TOKEN: {}'.format(utils.decrypt(self.camRunTime.login.get('token').decode())))
                            self.camRunTime.sessionStatus, self.camRunTime.error = checkSessionPv(self.camRunTime.login)
                            self.camRunTime.timeInternetOffStart = time.time() 
                            #self.updateStorageInfo.emit()
                            #print('sessionStatus: {}'.format(self.camRunTime.sessionStatus))

                            if self.camRunTime.error == 'servidorOut':
                                #print('Servidor não respondendo. Ignorando checkSession')
                                log.critical('inferenceCore:: Servidor não respondendo. Ignorando checkSession')
                                self.camRunTime.sessionStatus = True
                                self.camRunTime.errorSession = 0
                           
                            elif self.camRunTime.sessionStatus == False:
                                log.warning('inferenceCore:: sessionStatus: {}'.format(self.camRunTime.sessionStatus))
                                if self.camRunTime.errorSession == self.camRunTime.sessionErrorCount:
                                    self.warningSessionLoss.emit()                                
                                    log.warning('inferenceCore:: stopWatchDog chamado - erro de sessao pela 2a vez')
                                    utils.stopWatchDog()
                                else:
                                    self.camRunTime.errorSession = self.camRunTime.errorSession + 1
                                    log.warning('inferenceCore:: Erro de sessao pela {:d} vez'.format(self.camRunTime.errorSession))
                                    self.warningSessionLossFirst.emit()                                
                                    self.camRunTime.sessionStatus = True
                                    
                            elif self.camRunTime.sessionStatus == True:
                                self.camRunTime.errorSession = 0
                                log.info('inferenceCore:: Sessao de login ok')
                            


                        else:
                            log.critical(' ')
                            log.critical("inferenceCore:: Sem internet - sessao não checada")
                            log.critical("inferenceCore:: sessionStatus: {}".format(self.camRunTime.sessionStatus))
                           
                            if (time.time() - self.camRunTime.timeInternetOffStart) >= self.camRunTime.INTERNET_OFF: 
                                
                                self.camRunTime.STOP_ALL = True 
                                
                                #release dos videos
                                if self.camRunTime.out_video is not None:
                                   self.camRunTime.out_video.release()
                                   self.camRunTime.out_video = None
                                   self.camRunTime.releaseVideoOnAlarmes = False
                                
                                if self.camRunTime.out_video_all_time is not None:
                                     self.camRunTime.out_video_all_time.release()
                                     self.camRunTime.out_video_all_time = None
                                     self.camRunTime.releaseVideoAllTime = False


                                log.critical('inferenceCore:: Tempo maximo sem Internet permitido esgotado - Portao Virtual ficará inativo')
                                

                            #emitir mensagem de aviso
                            self.camRunTime.sessionStatus = True

                        self.camRunTime.timeSessionInit = time.time()

                    
                    self.camRunTime.listObjects.clear()                
                    
                    

                else:
                    if not self.camRunTime.conectado:
                        log.warning('inferenceCore:: Conectado False - Reconectando em 5 segundos...')
                        
                        self.source = self.camRunTime.statusConfig.data["camSource"]
                        #init_video = False
                        time.sleep(5)
                        if self.camRunTime.ipCam is not None:
                            self.camRunTime.ipCam, self.camRunTime.error = utils.camSource(self.camRunTime.source)
                            self.camRunTime.ipCam.set(3, self.camRunTime.RES_X)
                            self.camRunTime.ipCam.set(4, self.camRunTime.RES_Y)
                            
                            self.camRunTime.conectado, self.camRunTime.frame = self.camRunTime.ipCam.read()
                            self.camRunTime.ret, self.camRunTime.next_frame = self.camRunTime.ipCam.read()
                        #ipCam = utils.camSource(source)
                        
                    elif self.camRunTime.changeIpCam:
                        log.warning('inferenceCore:: changeIpCam True')
                        
                        #self.source = self.statusConfig.data["camSource"]
                        #print('self.camRunTime.source: {}'.format(self.camRunTime.source))
                        if self.camRunTime.ipCam is not None:
                            self.camRunTime.ipCam, self.camRunTime.error = utils.camSource(self.camRunTime.source)
                            self.camRunTime.ipCam.set(3, self.camRunTime.RES_X)
                            self.camRunTime.ipCam.set(4, self.camRunTime.RES_Y)
                            self.camRunTime.conectado, self.camRunTime.frame = self.camRunTime.ipCam.read()
                            self.camRunTime.ret, self.camRunTime.next_frame = self.camRunTime.ipCam.read()
                        self.changeIpCam = False
                        
                    elif self.camRunTime.errorWebcam:
                        log.info('inferenceCore:: webCamWarning.init()')
                        self.webCamWarning.emit()
                    
                    else:
                        log.warning('Reconectando em 5 segundos... - Reiniciando OpenVino')
                        #self.source = self.statusConfig.data["camSource"]
                        self.source = self.camRunTime.statusConfig.data["camSource"]
                        #print('Reconectando em 5 segundos... Iniciando OpenVino novamente')
                        self.initOpenVino() 
                        time.sleep(5)

            
            
            if self.camRunTime.errorWebcam:
                #log.info('inferenceCore:: webCamWarning.emit()')
                self.webCamWarning.emit()
            
            if self.camRunTime.camEmpty:
                #log.info('inferenceCore:: camEmptyWarning.emit()')
                self.camEmptyWarning.emit()
            
            #self.stop()
    
    def stop(self):
        #"""Sets run flag to False and waits for thread to finish"""
        #if self.camRunTime.out_video is not None:
        log.warning('Fim da captura de video out_video_all_time')
        if self.camRunTime.out_video is not None:
            self.camRunTime.out_video.release()
        
        if self.camRunTime.ipCam is not None:
            self.camRunTime.ipCam.release()
        
        cv.destroyAllWindows()
        self._run_flag = False
        #self.wait()

        # if self.camRunTime.out_video_all_time is not None:
            # log.warning('Fim da captura de video out_video_all_time')
            # self.camRunTime.out_video_all_time.release()


        # if self.camRunTime.ipCam and cv is not None:
            # log.info('ipCam release and cv.destroyAllWindows') 
            # self.camRunTime.ipCam.release()
            # cv.destroyAllWindows()

        
        






