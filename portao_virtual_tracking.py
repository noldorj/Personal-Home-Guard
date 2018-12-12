#
import cv2 as cv
import numpy as np
from datetime import date
import time
from objectTracking.pyimagesearch.centroidtracker import CentroidTracker
from imutils.video import VideoStream
import numpy as np
#import imutils
import os
from Utils_tracking import sendMailAlert
from Utils_tracking import saveImageBox
import utilsCore as utils

#import tensorflow as tf


classes = ["background", "pessoa", "bicileta", "carro", "moto",
    "airplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant",
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

#lista de objetos detectados da rede neural
detection =[]
#lista de boxes detectados
listRectanglesDetected = []
#lista de objetos traqueados
listObjectsTracking = []
#linhas e colunas do video (resolucao)
rows = None
cols = None

colors = np.random.uniform(0, 255, size=(len(classes), 3))

# Read the graph.
pb = 'dlModels/frozen_inference_graph_v1_coco_2017_11_17.pb'
pbtxt = 'dlModels/ssd_mobilenet_v1_coco_2017_11_17.pbtxt'

cvNet = cv.dnn.readNetFromTensorflow(pb, pbtxt)
# initialize our centroid tracker and frame dimensions
ct = CentroidTracker()
(H, W) = (None, None)

#diretorio dos videos dos alarmes
dir_video_trigger = './'

#cvNet = cv.dnn.readNetFromTensorflow('frozen_inference_graph_v1_coco_2017_11_17.pb', 'ssd_mobilenet_v1_coco_2017_11_17.pbtxt')
#cv.VideoCapture("rtsp://admin:WWYZRL@192.168.0.197/live/mpeg4:554")

listObjectDetected = list()

idObjeto = 0

class objectDetected():

    linkFoto = "link para foto"
    linkVideo = "link para video"
    tipo = 'tipo'
    hora = 'hora'
    mes = 'mes'
    ano = 'ano'

    def __init__(self, idObjeto, tipo, hora, dia, mes, ano):

        #atributos
        self.idObjeto = idObjeto
        self.tipo = tipo   #pessoa, cachorro, carro, etc.
        self.hora = hora
        self.dia = dia
        self.mes = mes
        self.ano = ano

    def getTipo():
        return self.tipo



def getDate():
    data = time.asctime().split(" ")
    #para dias com um digito
    if data.count("") > 0:
        data.remove("")
    data = {'day':data[2], 'month':data[1],'hour':data[3], 'year':data[4]  }
    return data


def camSource(source = 'webcam'):
    if source == 'webcam':
        print('imagem da WebCam')
        return cv.VideoCapture(0)
    else:
        print('imagem de camera rstp')
        return cv.VideoCapture(source)




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
        cvNet.setInput(cv.dnn.blobFromImage(img, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        cvOut = cvNet.forward()


        for detection in cvOut[0,0,:,:]:

            score = float(detection[2])
            if score > 0.40:

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

                    boxTracking = (left, top, right, bottom)

                    listObjectsTracking.append(boxTracking)

                    listRectanglesDetected.append(box)

#                else:
#                    print('Objecto desconhecido: ' + classes[idx])

    else:
        print('\n frame lost')

    return listRectanglesDetected


drawing = False     # true if mouse is pressed
mode = True         # if True, draw rectangle.
ix, iy = -1, -1

# now let's initialize the list of reference point
ref_point = []
crop = False
portaoVirtualSelecionado = False
showGate = False
regiaoPortao = None
sel_rect_endpoint = []

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

        # draw a rectangle around the region of interest
#        cv.rectangle(frame, ref_point[0], sel_rect_endpoint[0], (100, 255, 0), 2)
#        print('W: ', ref_point[1][0])
#        print('H: ', ref_point[1][1])
#        cv.imshow("frame", frame)
#        portaoVirtualSelecionado = True


def createDirectory():

    date = getDate()
    month_dir = '/' + date['month'] + '-' + date['year']
    month_dir
    today_dir = '/' + date['day']
    current_dir = os.getcwd() + '/video_alarmes'
#    current_dir = '/Users/ijferrei/video_alarmes'
    status = False

    #checar se pasta do mes existe, ou cria-la
    try:
        os.makedirs(current_dir + month_dir + today_dir)

    except OSError as ex:

        if ex.errno == 17:
            print('Diretorio ' + current_dir + month_dir + today_dir + ' existente.')
            status = True
        else:
            print('Erro ao criar o diretorio: ' + current_dir + month_dir + today_dir)
            print(ex.__str__())

    else:
        print("Diretorio " + current_dir + month_dir + today_dir + " criado com sucesso")
        status = True

    dir_temp = current_dir + month_dir + today_dir

    return status, dir_temp


status_dir_criado, dir_video_trigger = createDirectory()



# funcao que grava momento em que a pessoa foi identificada

#source = "rtsp://admin:WWYZRL@192.168.0.197/live/mpeg4:554"
source = 'webcam'
ipCam = camSource(source)


cv.namedWindow('frame')
cv.setMouseCallback('frame', shape_selection)

objDetectado = False

#fourcc = cv.VideoWriter_fourcc(*'X264')
#for linux x264 need to recompile opencv mannually
fourcc = cv.VideoWriter_fourcc(*'XVID')


hora = getDate()['hour'].replace(':','-')

#TO-DO: tem que pegar do arquivo de texto
current_data_dir = getDate()
current_data_dir.pop('hour')


#

statusConfig = utils.StatusConfig()
timer_without_object = 0
start_time = 0
gravando = False
newVideo = True
objects = None
FPS = 30.0 #frames per second
enviarAlerta = True
novo_alerta = True
isSoundAlert = True #todo pegar status de arquivo de configuracao

#primeiro objeto é enviado
listObjectMailAlerted = []

out_video = None
cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, FPS, (1280,720))


while True:

    conectado, frame = ipCam.read()
    conectado, frame_no_label = ipCam.read()
    conectado, frame_no_label_email = ipCam.read()



    if (conectado and frame is not None):



        objects = ct.update(listObjectsTracking)

        currentData = getDate()
        currentData.pop('hour')

        if current_data_dir != currentData:
            status_dir_criado, dir_video_trigger = createDirectory()
            current_data_dir = getDate()
            current_data_dir.pop('hour')


#        if frame is not None and conectado:

        #to select the Region of Interest
        if cv.waitKey(1) & 0xFF == ord('a'):
            enviarAlerta = not enviarAlerta
            if (enviarAlerta):
                print('Alerta por email ativado')
            else:
                print('Alerta por email desativado')

        #to select the Region of Interest
        if cv.waitKey(1) & 0xFF == ord('s'):

            if portaoVirtualSelecionado:
                print('Portao já selecionado')
                print('Selecione novo portao')
                portaoVirtualSelecionado = False


        if portaoVirtualSelecionado:
           cv.rectangle(frame, ref_point[0], ref_point[1], (0, 255, 0), 2)

        if crop and sel_rect_endpoint:
            cv.rectangle(frame, ref_point[0], sel_rect_endpoint[0], (0, 255, 0), 2)


        #passando o Frame selecionado do portao para deteccao
        listObjects = objectDetection(frame)

#        print('# Objetos: ' + str(len(listObjects)))

        if len(listObjects) == 0 and portaoVirtualSelecionado:

#            print('Sem objetos...')
            start_time = time.time()
#            print('start_time ' + str(start_time))
#            print('timer_without_object: ' + str(timer_without_object))
            gravando = False
            newVideo = True
            novo_alerta = False

            listObjects.clear()
            listObjectsTracking.clear()
            objects = ct.update(listObjectsTracking)


            if out_video is not None:
#                print('Video release')
                out_video.release()

#            if (timer_without_object - start_time) >= 5:
#                print('Gravando false')
#                gravando = False
#                start_time = 0
#                timer_without_object = 0
#                newVideo = True

#            else:
#                print('Gravando enquanto objeto some')
##                out_video = cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, 20.0, (1280,720))
#                out_video.write(frame)
#                gravando = True

        #se tem objetos detectados pela CNN
        else:

            #enquanto tiver objetos, grava
            gravando = True
            novo_alerta = True

            for box in listObjects:

                if portaoVirtualSelecionado:
#                    print('Checando portao virtual')

                    objectsTracking = ct.update(listObjectsTracking)

                    for (objectID, centroid) in objectsTracking.items():

#                        print('ref_point[0][0]: ', ref_point[0][0], 'ref_point[1][0]: ', ref_point[1][0], 'centroid[0]: ', centroid[0])
#                        print('ref_point[0][1]: ', ref_point[0][1], 'ref_point[1][1]: ', ref_point[1][1], 'centroid[0]: ', centroid[1])

                        #se o objeto estiver contido no portaoVirtual
                        if centroid[0] >= ref_point[0][0] and centroid[0] <= ref_point[1][0] \
                        and centroid[1] >= ref_point[0][1] and centroid[1] <= ref_point[1][1]:

#                            print("Objeto dentro do portao virtual")
#                            print('Desenhando objetos')


                            #desenhando o box e label
#                            cv.rectangle(frame, (int(box[0]), int(box[1]) ), (int(box[2]), int(box[3])), (23, 230, 210), thickness=2)
#                            top = int (box[1])
#                            y = top - 15 if top - 15 > 15 else top + 15
#                            cv.putText(frame, str(box[4]), (int(box[0]), int(y)),cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)


                            #desenhando o ID no centro do objeto
#                            text = "ID {}".format(objectID)
#                            cv.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
#                                cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
#                            cv.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

                            if listObjectMailAlerted.count(objectID) == 0:

                                if isSoundAlert:
                                    utils.playSound()

                                if enviarAlerta:

                                    print('Enviando alerta por email')

                                    #salvando foto para treinamento
                                    #crop no box
    #                               left, top, right, bottom
                                    frame_no_label = frame_no_label[int(box[1])-10:int(box[1]) + int(box[3]) , int(box[0])+10:int(box[2])]
    #                               cv.imshow("cropped", frame_no_label)
    #                               cv.waitKey(0)
                                    saveImageBox(frame_no_label, str(box[6]))
    #                               crop_img = img[y:y+h, x:x+w]

        #                           cv.imwrite(dir_video_trigger + '/foto_alerta.jpg',frame)'

                                    if (sendMailAlert('igorddf@gmail.com', 'igorddf@gmail.com', frame_no_label_email, str(box[6]))):

                                        print('Alerta enviado ID[' + str(objectID) + ']')
                                        print('...')

                                         #para evitar o envio de varios emails do mesmo reconhecimento
                                         #novo_alerta = False

                                    listObjectMailAlerted.append(objectID)

                            if gravando and newVideo:
                                  #grava video novo se tiver um objeto novo na cena
        #                                      if newVideo:
                                      #print('Gravando novo video')
                                  if out_video is not None:
                                      out_video.release()

                                  hora = getDate()['hour'].replace(':','-')
                                  out_video = cv.VideoWriter(dir_video_trigger + '/' + hora + '.avi', fourcc, FPS, (1280,720))
                                  out_video.write(frame)
                                  newVideo = False
        #
                            else:
                                out_video.write(frame)

        #    # update our centroid tracker using the computed set of bounding
        #    # box rectangles
        #    objects = ct.update(detection)
        #    # loop over the tracked objects
        #    for (objectID, centroid) in objects.items():
        #        # draw both the ID of the object and the centroid of the
        #        # object on the output frame
        #        text = "ID {}".format(objectID)
        #        cv.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
        #                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #        cv.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)


        #qq
        #    data = getDate()
        #    idObjeto = idObjeto + 1
        #    obj = objectDetected(idObjeto,classes[idx], data[3], data[0], data[1], data[3])
        #    listObjectDetected.append(obj)
        #    print('id: ' + str(idObjeto))
        #    print('tipo: ' + obj.tipo)
        #    print(len(detection))

        cv.imshow('frame', frame)

        listObjects.clear()
        listObjectsTracking.clear()
        objects.update()

        cv.waitKey(50)


        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    else:
        print('frame lost - while')
        if not conectado:
            print('Reconecting ...')
            ipCam = camSource(source)

if out_video is not None:
    out_video.release()

ipCam.release()
cv.destroyAllWindows()




