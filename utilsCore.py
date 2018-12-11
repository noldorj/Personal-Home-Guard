import json
import os
import pyglet

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
    campainha = pyglet.resource.media('campainha.wav')
    campainha.play()
    print('Campainha tocada: ' + os.getcwd())



# Add the basic infomation about the cam security system like
# which object or person was detectec, if the email alert is active,
# if the virtual gate is activate, if the record videos is actitive etc.
#def footerCam(frame, statusConfig):
