import json
import os

class StatusConfig:

    data = {
            "isRecording"    : "false",
            "isEmailAlert"   : "false",
            "isGateSelected" : "false",
            "isSoundAlert"   : "false",
            "dnnModel"       : ["ssd_mobilenet","yolo-v2"],
        #    dnnModel = {'pb':'dlModels/frozen_inference_graph_v1_coco_2017_11_17.pb',
        #                'pbtxt':'dlModels/ssd_mobilenet_v1_coco_2017_11_17.pbtxt'}

            "emailConfig"    : {'user':'user@user.com', 'password':'password', 'subject':'Alarme PV',
                           'to':'destiny@server.com'},

            "dirVideos"      : "../videos_alarmes"
    }

#    def __init__(self,isRecording, isEmailAlert, isGateSelected, isSoundAlert,
#                 dnnModel, emailConfig, dirVideos):

#    def __init__(self):


#        self.isRecording = isRecording
#        self.isEmailAlert = isEmailAlert
#        self.isGateSelected = isGateSelected
#        self.isSoundAlert = isSoundAlert
#        self.dnnModel = dnnModel
#        self.emailConfig = emailConfig
#        self.dirVideos = dirVideos

    def saveConfigFile(self, file = 'config.json'):
        print('Salvando arquivo de configuração: ' + os.getcwd() + '/' + file)
        json.dump(data, open(file,'w'))



# Add the basic infomation about the cam security system like
# which object or person was detectec, if the email alert is active,
# if the virtual gate is activate, if the record videos is actitive etc.

def footerCam(frame, statusConfig):


