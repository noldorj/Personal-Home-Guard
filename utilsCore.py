import json
import os
import pygame
import cv2 as cv
import time

def camSource(source = 'webcam'):
    if source == 'webcam':
        print('imagem da WebCam')
        return cv.VideoCapture(0)
    else:
        print('imagem de camera rstp')
        return cv.VideoCapture(source)

def getDate():
    data = time.asctime().split(" ")
    #para dias com um digito
    if data.count("") > 0:
        data.remove("")
    data = {'day':data[2], 'month':data[1],'hour':data[3], 'year':data[4]  }
    return data

def createDirectory(dirVideos):

    date = getDate()
    month_dir = '/' + date['month'] + '-' + date['year']
    month_dir
    today_dir = '/' + date['day']
    current_dir =  dirVideos
    #current_dir = os.getcwd() + '/video_alarmes'
#    current_dir = '/Users/ijferrei/video_alarmes'
    status = False
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

class StatusConfig:


    data = {
            "isRecording"       : "True",
            "isEmailAlert"      : "True",
            "isGateSelected"    : "False",
            "isSoundAlert"      : "True",
            "isOpenVino"        : "True",
            "camSource"         :  "webcam",
            "prob_threshold"    :  0.60,
            # aponta para pastas dentro de dlModels
            "dnnModelPb"        : "./dlModels/ssd-mobilenet/frozen_inference_graph_v1_coco_2017_11_17.pb",
            "dnnModelPbTxt"     : "./dlModels/ssd-mobilenet/ssd_mobilenet_v1_coco_2017_11_17.pbtxt",
            "openVinoModelXml"  : "./computer_vision_sdk/deployment_tools/intel_models/person-vehicle-bike-detection-crossroad-0078/FP32/person-vehicle-bike-detection-crossroad-0078.xml",
            "openVinoModelBin"  : "./computer_vision_sdk/deployment_tools/intel_models/person-vehicle-bike-detection-crossroad-0078/FP32/person-vehicle-bike-detection-crossroad-0078.bin",
            "openVinoDevice"    : "CPU",
        #    dnnModel = {'pb':'dlModels/frozen_inference_graph_v1_coco_2017_11_17.pb',
        #                'pbtxt':'dlModels/ssd_mobilenet_v1_coco_2017_11_17.pbtxt'}

        "emailConfig"    : {'port':'587', 'smtp':'smtp.gmail.com','user':'user@user.com', 'password':'password', 'subject':'Alarme PV',
                           'to':'destiny@server.com'},

            "dirVideos"      : "/home/igor/videos_alarmes"
    }

    def setConfig(self, isRecording, isEmailAlert, isGateSelected, isSoundAlert, isOpenVino,
                      dnnModel, openVinoModel, emailConfig, dirVideos, camSource, openVinoDevice, prob_threshold):
        self.data["isRecording"]              = isRecording
        self.data["isEmailAlert"]             = isEmailAlert
        self.data["isGateSelected"]           = isGateSelected
        self.data["isSoundAlert"]             = isSoundAlert
        self.data["camSource"]                = camSource 
        self.data["prob_threshold"]           = prob_threshold 
        self.data["isOpenVino"]               = isOpenVino
        self.data["dnnModelPb"]               = dnnModelPb
        self.data["dnnModelPbTxt"]            = dnnModelPbTxt
        self.data["openVinoDevice"]           = openVinoDevice
        self.data["openVinoModel"]            = openVinoModel 
        self.data["dirVideos"]                = dirVideos
        self.data["emailConfig"]["port"]      = emailConfig["port"]
        self.data["emailConfig"]["smtp"]      = emailConfig["smtp"]
        self.data["emailConfig"]["user"]      = emailConfig["user"]
        self.data["emailConfig"]["password"]  = emailConfig["password"]
        self.data["emailConfig"]["subject"]   = emailConfig["subject"]
        self.data["emailConfig"]["to"]        = emailConfig["to"]


#    def __init__(self,isRecording, isEmailAlert, isGateSelected, isSoundAlert,
#                 dnnModel, emailConfig, dirVideos):

    def __init__(self, configFile):
        #configuracoes setadas pelo arquivo sobrescrevem as configuracoes padroes
        self.readConfigFile(configFile)

    def readConfigFile(self, file = 'config.json'):

        print('Lendo arquivo de configuração: ' + os.getcwd() + '/' + file)
        self.data = json.load(open(file,'r'))
        self.printConfig()



    def printConfig(self):
        print('--- Config status  ---')
        print('isRecording:       {}'.format(self.data.get('isRecording')))
        print('isEmailAlert:      {}'.format(self.data.get('isEmailAlert')))
        print('isGateSelected:    {}'.format(self.data.get('isGateSelected')))
        print('isSoundAlert:      {}'.format(self.data.get('isSoundAlert')))
        print('prob_threshold:    {}'.format(self.data.get('prob_threshold')))
        print('camSource:         {}'.format(self.data.get('camSource')))
        print('isOpenVino:        {}'.format(self.data.get('isOpenVino')))
        print('dnnModelPb:        {}'.format(self.data.get('dnnModelPb')))
        print('dnnModelPbTxt:     {}'.format(self.data.get('dnnModelPbTxt')))
        print('openVinoModelXml:  {}'.format(self.data.get('openVinoModelXml')))
        print('openVinoModelBin:  {}'.format(self.data.get('openVinoModelBin')))
        print('emailConfig/user:  {}'.format(self.data.get('emailConfig').get('user')))
        print('emailConfig/smtp:  {}'.format(self.data.get('emailConfig').get('smtp')))
        print('emailConfig/port:  {}'.format(self.data.get('emailConfig').get('port')))
        print('dirVideos:         {}'.format(self.data.get('dirVideos')))


    def saveConfigFile(self, file = 'config.json'):

        # print('Salvando arquivo de configuração: ' + os.getcwd() + '/' + file)
        json.dump(self.data, open(file,'w'), indent=4)


def playSound():
   # campainha = pyglet.media.load('campainha.wav')
   # campainha.play()
    print('Campainha tocada: ' + os.getcwd())
    pygame.init()
    pygame.mixer.music.load('campainha.mp3')
    pygame.mixer.music.play(0)
