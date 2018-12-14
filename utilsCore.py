import json
import os
import pygame
import time

def getDate():
    data = time.asctime().split(" ")
    #para dias com um digito
    if data.count("") > 0:
        data.remove("")
    data = {'day':data[2], 'month':data[1],'hour':data[3], 'year':data[4]  }
    return data

def createDirectory():

    date = getDate()
    month_dir = '/' + date['month'] + '-' + date['year']
    month_dir
    today_dir = '/' + date['day']
    current_dir = os.getcwd() + '/video_alarmes'
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
            "isRecording"    : "true",
            "isEmailAlert"   : "true",
            "isGateSelected" : "false",
            "isSoundAlert"   : "true",
            "dnnModel"       : "ssd_mobilenet",
        #    dnnModel = {'pb':'dlModels/frozen_inference_graph_v1_coco_2017_11_17.pb',
        #                'pbtxt':'dlModels/ssd_mobilenet_v1_coco_2017_11_17.pbtxt'}

            "emailConfig"    : {'user':'user@user.com', 'password':'password', 'subject':'Alarme PV',
                           'to':'destiny@server.com'},

            "dirVideos"      : "../videos_alarmes"
    }

#    def __init__(self,isRecording, isEmailAlert, isGateSelected, isSoundAlert,
#                 dnnModel, emailConfig, dirVideos):

#    def __init__(self):

    def readConfigFile(self, file = 'config.json'):

        print('Lendo arquivo de configuração: ' + os.getcwd() + '/' + file)
        data = json.load(open(file,'r'))

        print('--- Config status  ---')
        print('isRecording: ' + data.get('isRecording'))
        print('isEmailAlert: ' + data.get('isEmailAlert'))
        print('isGateSelected: ' + data.get('isGateSelected'))
        print('isSoundAlert: ' + data.get('isSoundAlert'))
        print('dnnModel: ' + data.get('dnnModel'))
        print('emailConfig / user : ' + data.get('emailConfig').get('user'))
        print('dirVideos: ' + data.get('dirVideos'))


    def saveConfigFile(self, file = 'config.json'):

        print('Salvando arquivo de configuração: ' + os.getcwd() + '/' + file)
        json.dump(data, open(file,'w'), indent=4)


def playSound():
   # campainha = pyglet.media.load('campainha.wav')
   # campainha.play()
    print('Campainha tocada: ' + os.getcwd())
    pygame.init()
    pygame.mixer.music.load('campainha.mp3')
    pygame.mixer.music.play(0)


# Add the basic infomation about the cam security system like
# which object or person was detectec, if the email alert is active,
# if the virtual gate is activate, if the record videos is actitive etc.
#def footerCam(frame, statusConfig):
