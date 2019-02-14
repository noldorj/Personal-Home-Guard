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

    region = {
        "nameRegion"        : "garagem",
        "isEmailAlert"      : "True",
        "isSoundAlert"      : "True",
        "time"              : {'start':'8:00', 'end':'21:00'},
        "days"              : {'mon':'True', 'tues':'true','wed':'true', 'thurs':'true', 'fri':'true','sat':'true','sun':'true'},
        "objectType"        : {'person':'true', 'car':'true', 'bike':'true', 'dog':'true'},
        "prob_threshold"    : 0.70,
        "pointsPolygon"     : []
    }

    regions = list()

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

    def addRegion(self, nameRegion, isEmailAlert, isSoundAlert, time, days, objectType, prob_threshold, pointsPolygon):

        self.region["nameRegion"]               = nameRegion
        self.region["isEmailAlert"]             = isEmailAlert
        self.region["isSoundAlert"]             = isSoundAlert
        self.region["time"]["start"]            = time["start"]
        self.region["time"]["end"]              = time["end"]
        self.region["days"]["mon"]              = days["mon"]
        self.region["days"]["tues"]             = days["tues"]
        self.region["days"]["wed"]              = days["wed"]
        self.region["days"]["thurs"]            = days["thurs"]
        self.region["days"]["fri"]              = days["fri"]
        self.region["days"]["sat"]              = days["sat"]
        self.region["days"]["sun"]              = days["sun"]
        self.region["objectType"]["person"]     = objectType["person"]
        self.region["objectType"]["car"]        = objectType["car"]
        self.region["objectType"]["bike"]       = objectType["bike"]
        self.region["objectType"]["dog"]        = objectType["dog"]
        self.region["prob_threshold"]           = prob_threshold
        self.region["pointsPolygon"]            = pointsPolygon

        self.regions["regions"].append(self.region)


    def __init__(self, configFile='config.json', regionsFile='regions.json'):
        #configuracoes setadas pelo arquivo sobrescrevem as configuracoes padroes
        self.readConfigFile(configFile)
        self.readRegionsFile(regionsFile)

    def readConfigFile(self, file = 'config.json'):
        print('Lendo arquivo de configuração: ' + os.getcwd() + '/' + file)
        self.data = json.load(open(file,'r'))
        self.printConfig()

    def readRegionsFile(self, file = 'regions.json'):
        print('Lendo arquivo de regiões: ' + os.getcwd() + '/' + file)
        self.regions = json.load(open(file,'r'))
        self.printRegions()
    
    def deleteRegion(self, nameRegion='regions1'):
        i = 0
        print('Region {} to be removed'.format(nameRegion))
        
        for r in self.regions["regions"]:
            print('nameRegion {}'.format(r.get("nameRegion")))
            if r.get("nameRegion") == nameRegion:                
                del self.regions["regions"][i]
                print('Region {} removed i: {}'.format(nameRegion, i))
                return True            
            
            i = i+1
        return False
        


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
        
        
    def printRegions(self):
            print('                                      ')
            print('--- Regions status  ---')
            print('# regions: {}'.format(len(self.regions["regions"])))
            for r in self.regions["regions"]:
                
                print('nameRegion:            {}'.format(r.get('nameRegion')))
                print('isEmailAlert:          {}'.format(r.get('isEmailAlert')))
                print('isSoundAlert:          {}'.format(r.get('isSoundAlert')))
                print('Prob_threshold:        {}'.format(r.get('prob_threshold')))   
                print('Alarm Time start:      {}'.format(r.get('time').get('start')))
                print('Alarm Time end:        {}'.format(r.get('time').get('end')))
                print('PointsPolygon:         {}'.format(r.get('pointsPolygon')))   
                print('Alarm Days:')
                print('  Monday:        {}'.format(r.get('days').get('mon')))                
                print('  Tuesday:       {}'.format(r.get('days').get('tues')))                
                print('  Wednesday:     {}'.format(r.get('days').get('wed')))                
                print('  Thrusday:      {}'.format(r.get('days').get('thurs')))                
                print('  Friday:        {}'.format(r.get('days').get('fri')))                
                print('  Saturday:      {}'.format(r.get('days').get('sat')))                
                print('  Sunday:        {}'.format(r.get('days').get('sun')))                                   
                print('----------------------------------------------------------------')

    def saveRegionFile(self, file = 'region.json'):
        print('Salvando arquivo de regiones: ' + os.getcwd() + '/' + file)
        json.dump(self.regions, open(file, 'w'), indent=4)
    
    
    def saveConfigFile(self, file = 'config.json'):
        print('Salvando arquivo de configuração: ' + os.getcwd() + '/' + file)
        json.dump(self.data, open(file,'w'), indent=4)


def playSound():
   # campainha = pyglet.media.load('campainha.wav')
   # campainha.play()
    print('Campainha tocada: ' + os.getcwd())
    pygame.init()
    pygame.mixer.music.load('campainha.mp3')
    pygame.mixer.music.play(0)
    

#status = StatusConfig()
#
#t = {"start":"7:00", "end":"12:00"}
#days = {'mon':'False', 'tues':'False','wed':'False', 'thurs':'False', 'fri':'False','sat':'False','sun':'False'}
#objectType = {'person':'teste', 'car':'teste', 'bike':'teste', 'dog':'teste'}
#points = [[[15,15],[15,65],[65,15],[65,65]]]
#
#status.addRegion("teste", "true", "true", t, days, objectType, 0.45, points)
#status.addRegion("teste2", "true2", "true2", t, days, objectType, 0.45, points)
#
#status.printRegions()
#status.deleteRegion(nameRegion="teste")
#
#status.saveRegionFile('region.teste.json')
#status2 = StatusConfig(regionsFile='region.teste.json')
#status.regions
#status.regions["regioes"][1]



