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
import pluginOpenVino as pOpenVino
import logging as log

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

statusConfig = utils.StatusConfig('config.json.gpu.webcam')

# dnnMOdel for TensorFlow Object Detection API
pb = statusConfig.data["dnnModelPb"] 
pbtxt = statusConfig.data["dnnModelPbTxt"] 

#Criando diretorio para salvar videos de alarmes
status_dir_criado, dir_video_trigger = utils.createDirectory(statusConfig.data["dirVideos"])

#origem do stream do video
#source = "rtsp://admin:WWYZRL@192.168.5.101/live/mpeg4:554"
#source = 'webcam'
source = statusConfig.data["camSource"]
print('source: {}'.format(source))
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
portaoVirtualSelecionado = False
showGate = False
regiaoPortao = None
sel_rect_endpoint = []

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

        ref_point_polygon.append((x, y))
        #print(' ')
        #print('cv.EVENT_FLAG_CTRLKEY on')
        #print('size of ref_point_polygon: {}'.format(len(ref_point_polygon)))
        cropPolygon = True

    #elif not portaoVirtualSelecionado and event == cv.EVENT_LBUTTONUP and flags == cv.EVENT_FLAG_SHIFTKEY+1 and cropPolygon:
    elif not portaoVirtualSelecionado and flags == 0 and cropPolygon:

        #ref_point_polygon.append((x, y))
        #print(' ')
        print('cv.EVENT_FLAG_ALTKEY off')
        #print('size of ref_point_polygon: {}'.format(len(ref_point_polygon)))
        cropPolygon = False
        portaoVirtualSelecionado = True




def shape_selection(event, x, y, flags, param):
    # grab references to the global variables
    global ref_point, crop, portaoVirtualSelecionado, sel_rect_endpoint

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being performed
    if event == cv.EVENT_LBUTTONDOWN and not portaoVirtualSelecionado:
        ref_point = [(x, y)]
        crop = True
#        print('X: ', ref_point[0][0])
#        print('Y: ', ref_point[0][1])

    # check to see if the left mouse button was released
    elif event == cv.EVENT_LBUTTONUP and not portaoVirtualSelecionado:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        ref_point.append((x, y))
        crop = False
        # draw a rectangle around the region of interest
#        cv.rectangle(frame, ref_point[0], ref_point[1], (0, 255, 0), 2)
#        print('W: ', ref_point[1][0])
#        print('H: ', ref_point[1][1])qqq
#        cv.imshow("frame", frame)
        portaoVirtualSelecionado = True


    elif event == cv.EVENT_MOUSEMOVE and not portaoVirtualSelecionado:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        sel_rect_endpoint = [(x, y)]

cv.namedWindow('frame')
cv.setMouseCallback('frame', shape_selection)
cv.setMouseCallback('frame', polygonSelection)

objDetectado = False


hora = utils.getDate()['hour'].replace(':','-')

#TO-DO: tem que pegar do arquivo de texto
current_data_dir = utils.getDate()
current_data_dir.pop('hour')


#

#todo pegar status de arquivo de configuracao
#statusConfig = utils.StatusConfig()

timer_without_object = 0
start_time = 0
gravando = statusConfig.data["isRecording"] == 'True'
newVideo = True
objects = None
#FPS = ipCam.get(cv.CAP_PROP_FPS) #30.0 #frames per second
FPS = 8  #de acordo com o manual da mibo ic5 intelbras
enviarAlerta = statusConfig.data["isEmailAlert"] == 'True'
novo_alerta = True
isSoundAlert = statusConfig.data["isSoundAlert"] == 'True'

#primeiro objeto é enviado
listObjectMailAlerted = []

out_video = None

#fourcc = cv.VideoWriter_fourcc(*'X264')
#for linux x264 need to recompile opencv mannually
fourcc = cv.VideoWriter_fourcc(*'XVID')
#fourcc = cv.VideoWriter_fourcc('M','J','P','G')
cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, FPS, (1280,720))

isOpenVino = statusConfig.data["isOpenVino"] == 'True'
print('isOpenVino: {}'.format(isOpenVino))
device = statusConfig.data["openVinoDevice"]

posConfigPv = 255
#statusButtonEmail = None
def initInterface():

    #cv.createButton('Configurar Regioes', callbackButtonRegioes, None,cv.QT_PUSH_BUTTON)
    cv.createButton('Novo Portao', callbackAtivarPortao, None, cv.QT_PUSH_BUTTON)
    cv.createButton('Campainha', callbackCampainha, None, cv.QT_CHECKBOX, 1 if isSoundAlert else 0)
    #print('initInterface  -  enviarAlerta: {}'.format(enviarAlerta))
    cv.createButton('Enviar Email', callbackEnviarEmail, None, cv.QT_CHECKBOX, 1 if enviarAlerta else 0)

#def callbackTrackBar(self, ret):
#    print('callbackTrackBar')

def callbackButtonRegioes(self, ret):
    print('Button regioes')

def callbackAtivarPortao(ret, ret2):
    global portaoVirtualSelecionado
    #if portaoVirtualSelecionado:
    #    log.info('Portao já selecionado')

    portaoVirtualSelecionado = False
    #print('portaoVirtualSelecionado: {}'.format(portaoVirtualSelecionado))
    sel_rect_endpoint.clear()
    ref_point_polygon.clear()
    log.info('Selecione novo portao')

def callbackEnviarEmail(ret, ret2):
    global enviarAlerta 
    enviarAlerta = True if ret else False 
    print('enviarAlerta: {}'.format(enviarAlerta))
    #print('ret: {}'.format(ret))

def callbackCampainha(ret, ret2):
    global isSoundAlert
    isSoundAlert = True if ret else False 
    print('isSoundAlert: {}'.format(isSoundAlert))

initInterface()


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

while True:

    conectado, frame = ipCam.read()
    conectado, frame_no_label = ipCam.read()
    conectado, frame_no_label_email = ipCam.read()
    conectado, frame_screen = ipCam.read()

    if (conectado and frame is not None and next_frame is not None):


        objects = ct.update(rects = listObjectsTracking)

        currentData = utils.getDate()
        currentData.pop('hour')

        if current_data_dir != currentData:
            status_dir_criado, dir_video_trigger = utils.createDirectory(statusConfig.data["dirVideos"])
            current_data_dir = utils.getDate()
            current_data_dir.pop('hour')

#        if frame is not None and conectado:

        if portaoVirtualSelecionado:
           #cv.rectangle(frame_screen, ref_point[0], ref_point[1], (0, 255, 0), 2)

           pts = np.array(ref_point_polygon, np.int32)
           pts = pts.reshape((-1,1,2))
           cv.polylines(frame_screen,[pts],True,(0,255,255))


        if crop and sel_rect_endpoint:
            cv.rectangle(frame_screen, ref_point[0], sel_rect_endpoint[0], (0, 255, 0), 2)

        if cropPolygon:
            pts = np.array(ref_point_polygon, np.int32)
            pts = pts.reshape((-1,1,2))
            cv.polylines(frame_screen,[pts],True,(0,255,255))


        #passando o Frame selecionado do portao para deteccao somente se o portao virtual estiver selecionado
        if portaoVirtualSelecionado:

            if isOpenVino:
            ### ---------------  OpenVino Get Objects ----------------- ###
                #frame, next_frAme, cur_request_id, next_request_id, listObjects, listObjectsTracking  = pOpenVino.getListBoxDetected(ipCam, device, frame, next_frame, nchw, exec_net, out_blob, input_blob, cur_request_id, next_request_id, prob_threshold)

                ret, listReturn  = pOpenVino.getListBoxDetected(ipCam, device, frame, next_frame, nchw, exec_net, out_blob, input_blob, cur_request_id, next_request_id, prob_threshold)

                if ret:
                    frame = next_frame
                    frame, next_frAme, cur_request_id, next_request_id, listObjects, listObjectsTracking  = listReturn[0], listReturn[1], listReturn[2], listReturn[3], listReturn[4], listReturn[5]

                    cur_request_id, next_request_id = next_request_id, cur_request_id

            else:
                #chamada para a CNN do OpenCV - TensorFlow Object Detection API 
                log.info("CNN via TF Object Detection API")
                listObjects = objectDetection(frame)

        #print('# Objetos: ' + str(len(listObjects)))

        if len(listObjects) == 0 and portaoVirtualSelecionado: 
            #print('Sem objetos...')
            #start_time = time.time()
           #print('start_time ' + str(start_time))
           #print('timer_without_object: ' + str(timer_without_object))
            gravando = False
            newVideo = True
            novo_alerta = False

            listObjects.clear()
            listObjectsTracking.clear()
            objects = ct.update(listObjectsTracking)


            if out_video is not None:
                #print('Video release')
                out_video.release()

           # if (timer_without_object - start_time) >= 5:
           #     print('Gravando false')
           #     gravando = False
           #     start_time = 0
           #     timer_without_object = 0
           #     newVideo = True

           # else:
           #     print('Gravando enquanto objeto some')
           #     out_video = cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, 20.0, (1280,720))
           #     out_video.write(frame)
           #     gravando = True

        #se tem objetos detectados pela CNN
        else:

            #enquanto tiver objetos, grava
            gravando = True
            novo_alerta = True

            for box in listObjects:

                if portaoVirtualSelecionado:
                    #print('Checando portao virtual')

                    #box = left, top, right, bottom, label, idx, classe
                    #print('box inside pv: {}'.format(box))

                    objectsTracking = ct.update(listObjectsTracking)
                    #print('objectTracking size: {}'.format(len(objectsTracking)))

                    for (objectID, centroid) in objectsTracking.items():

                       #print('ref_point[0][0]: ', ref_point[0][0], 'ref_point[1][0]: ', ref_point[1][0], 'centroid[0]: ', centroid[0])
                       # print('ref_point[0][1]: ', ref_point[0][1], 'ref_point[1][1]: ', ref_point[1][1], 'centroid[0]: ', centroid[1])

                        #desenhando o box e label
                        cv.rectangle(frame_screen, (int(box[0]), int(box[1]) ), (int(box[2]), int(box[3])), (23, 230, 210), thickness=2)
                        top = int (box[1])
                        y = top - 15 if top - 15 > 15 else top + 15
                        cv.putText(frame_screen, str(box[4]), (int(box[0]), int(y)),cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
                        text = "ID {}".format(objectID)
                        cv.putText(frame_screen, text, (centroid[0] - 10, centroid[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        cv.circle(frame_screen, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)



                        #se o objeto estiver contido no portaoVirtual
                        #if centroid[0] >= ref_point[0][0] and centroid[0] <= ref_point[1][0] \
                        #and centroid[1] >= ref_point[0][1] and centroid[1] <= ref_point[1][1]:

                        #TODO check centroid[0]
                        if isIdInsideRegion(centroid, ref_point_polygon):

                            #print("Objeto dentro do portao virtual")
                           # print('Desenhando objetos')

                            #desenhando o box e label
                            #cv.rectangle(frame_screen, (int(box[0]), int(box[1]) ), (int(box[2]), int(box[3])), (23, 230, 210), thickness=2)
                            #top = int (box[1])
                            #y = top - 15 if top - 15 > 15 else top + 15
                            #cv.putText(frame_screen, str(box[4]), (int(box[0]), int(y)),cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)


                            #desenhando o ID no centro do objeto
                            #text = "ID {}".format(objectID)
                            #cv.putText(frame_screen, text, (centroid[0] - 10, centroid[1] - 10),
                            #    cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            #cv.circle(frame_screen, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

                            if listObjectMailAlerted.count(objectID) == 0:

                                if isSoundAlert:
                                    utils.playSound()

                                if enviarAlerta:

                                    print('Enviando alerta por email')

                                    #salvando foto para treinamento
                                    #crop no box
                                   #left, top, right, bottom
                                    frame_no_label = frame_no_label[int(box[1])-10:int(box[1]) + int(box[3]) , int(box[0])+10:int(box[2])]
                                    saveImageBox(frame_no_label, str(box[6]))

                       #cv.imwrite(dir_video_trigger + '/foto_alerta.jpg',frame)'

                                    if (sendMailAlert('igorddf@gmail.com', 'igorddf@gmail.com', frame_no_label_email, str(box[6]))):

                                        print('Alerta enviado ID[' + str(objectID) + ']')
                                        print('...')

                                         #para evitar o envio de varios emails do mesmo reconhecimento
                                         #novo_alerta = False

                                    listObjectMailAlerted.append(objectID)

                            if gravando and newVideo:
                                  #grava video novo se tiver um objeto novo na cena
                                  if out_video is not None:
                                      out_video.release()

                                  hora = utils.getDate()['hour'].replace(':','-')
                                  out_video = cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, FPS, (1280,720))
                                  out_video.write(frame_no_label)
                                  newVideo = False
#                                  cv.waitKey(100)

                            else:
                                out_video.write(frame_no_label)

        cv.imshow('frame', frame_screen)

        listObjects.clear()
        listObjectsTracking.clear()
        objects.update()

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

        #to select the Region of Interest
        if cv.waitKey(1) & 0xFF == ord('a'):
            enviarAlerta = not enviarAlerta
            if (enviarAlerta):
                print('Alerta por email ativado')
            else:
                print('Alerta por email desativado')

        #to select the Region of Interest
        if cv.waitKey(1) & 0xFF == ord('s'):

            #if portaoVirtualSelecionado:
            portaoVirtualSelecionado = False
            sel_rect_endpoint.clear()
            ref_point_polygon.clear()
            #print('Portao já selecionado')
            print('Selecione novo portao')

    else:
#        print('frame lost - while')
        if not conectado:
#            print('Reconecting ...')
            ipCam = utils.camSource(source)

if out_video is not None:
    out_video.release()

ipCam.release()
cv.destroyAllWindows()



