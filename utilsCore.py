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
    #minute = data[3].split(":")[1]
    #hourOnly = data[3].split(":")[0]
    #weekDay = data[0].lower()
    data = {'day':data[2], 'month':data[1],'hour':data[3], 'year':data[4], 'weekDay':data[0].lower(), 'minute':data[3].split(":")[1], 'hourOnly':data[3].split(":")[0]}
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
        "alarm":[
                {
                        "name": "alarm1",
                        "time"              : {'start':'8:00', 'end':'21:00'},
                        "days"              : {'mon':'True', 'tue':'true','wed':'true', 'thu':'true', 'fri':'true','sat':'true','sun':'true'},
                },
                {
                        "name": "alarm2",
                        "time"              : {'start':'8:00', 'end':'21:00'},
                        "days"              : {'mon':'True', 'tue':'true','wed':'true', 'thu':'true', 'fri':'true','sat':'true','sun':'true'},
                }
        ],
        "objectType"        : {'person':'true', 'car':'true', 'bike':'true', 'dog':'true'},
        "prob_threshold"    : 0.70,
        "pointsPolygon"     : []
    }

    regions = list()

    def getRegions(self):
        return self.regions

    def isRegionsEmpty(self):
        return True if (len(self.regions) == 0) else False

    def isAlarmEmpty(self, regionName):
        status = False 

        #print('regionName : {}'.format(regionName))

        for r in self.regions:
            #print('nameRegion {}'.format(r.get("nameRegion")))
            if r.get("nameRegion") == regionName:
                status = (len(r.get('alarm')) == 0)


        return status


    def setConfig(self, isRecording, isOpenVino,
                      dnnModel, openVinoModel, emailConfig, dirVideos, camSource, openVinoDevice, prob_threshold):
        self.data["isRecording"]              = isRecording
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

    def addRegion(self, nameRegion, alarm, objectType, prob_threshold, pointsPolygon):


        region = {
            "nameRegion"     : nameRegion,
            "alarm"          : alarm,
            "objectType"     : objectType,
            "prob_threshold" : prob_threshold,
            "pointsPolygon"  : pointsPolygon
        }

        #self.regions["regions"].append(self.region)
        self.regions.append(region)

        self.saveRegionFile()
        #self.printRegions()

    def addAlarm(self, idRegion, alarm):
        self.regions[idRegion].get('alarm').append(alarm)
        self.saveRegionFile()
        #self.printRegions()
        print('Alarme inserido com sucesso')
        #TO-DO try catch toleranca a falhas


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
        try:
            self.regions = json.load(open(file,'r'))
        except OSError as ex:

                print('Arquivo de Regioes inexistente - será criado um novo arquivo') 
        else:
            print('Arquivo de regiões lido com sucesso')
            #self.printRegions()


    def deleteAlarm(self, regionName, alarmName):
        #print('regionName : {}'.format(regionName))
        #print('alarmName: {}'.format(alarmName))

        indexRegion = 0
        indexAlarm = 0

        for r in self.regions:
            #print('nameRegion {}'.format(r.get("nameRegion")))
            if r.get("nameRegion") == regionName:
                for a in r.get('alarm'):
                    #print('name alarm: {}'.format(a.get("name")))
                    if a.get('name') == alarmName:
                        del self.regions[indexRegion].get('alarm')[indexAlarm]
                        #print('Alarm removed: {}'.format(alarmName))
                    indexAlarm = indexAlarm+1
               # return True

            indexRegion = indexRegion+1
        #return False

        print("Alarm '{}' removido com sucesso".format(alarmName))
        #self.saveConfigFile()
        self.saveRegionFile()



    def deleteRegion(self, nameRegion='regions1'):
        i = 0
        #print('Region {} to be removed'.format(nameRegion))

        for r in self.regions:
            #print('nameRegion {}'.format(r.get("nameRegion")))
            if r.get("nameRegion") == nameRegion:
                del self.regions[i]
                #print('Region {} removed i: {}'.format(nameRegion, i))
                #return True

            i = i+1
        #return False
        self.saveRegionFile()
        print("Regiao '{}' removido com sucesso".format(nameRegion))




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

                print('             ')
                print('nameRegion:            {}'.format(r.get('nameRegion')))
                print('isEmailAlert:          {}'.format(r.get('isEmailAlert')))
                print('isSoundAlert:          {}'.format(r.get('isSoundAlert')))
                print('Prob_threshold:        {}'.format(r.get('prob_threshold')))
                print('PointsPolygon:         {}'.format(r.get('pointsPolygon')))
                for a in r["alarm"]:
                    print('Alarm Name:            {}'.format(a.get('name')))
                    print('Alarm Time start:      {}:{}'.format(a.get('time').get('start').get('hour'),a.get('time').get('start').get('min') ) )

                    print('Alarm Time end:      {}:{}'.format(a.get('time').get('end').get('hour'), a.get('time').get('end').get('min')))
                    print('Alarm Days:')
                    print('  Monday:        {}'.format(a.get('days').get('mon')))
                    print('  Tuesday:       {}'.format(a.get('days').get('tue')))
                    print('  Wednesday:     {}'.format(a.get('days').get('wed')))
                    print('  Thrusday:      {}'.format(a.get('days').get('thu')))
                    print('  Friday:        {}'.format(a.get('days').get('fri')))
                    print('  Saturday:      {}'.format(a.get('days').get('sat')))
                    print('  Sunday:        {}'.format(a.get('days').get('sun')))
                    print('             ')

    def saveRegionFile(self, file = 'regions.json'):
        print('Salvando arquivo de regiones: ' + os.getcwd() + '/' + file)
        try:
            json.dump(self.regions, open(file, 'w'), indent=4)

        except OSError as ex:

            print('Erro ao salvar arquivo {}'.format(file))

        else:
            print('Arquivo {} salvo'.format(file))


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
##
#t = {"start":"7:00", "end":"12:00"}
#t2 = {"start":"10:00", "end":"15:00"}
#
#days = {'mon':'False', 'tue':'False','wed':'False', 'thu':'False', 'fri':'False','sat':'False','sun':'False'}
##alarm = []
#objectType = {'person':'teste', 'car':'teste', 'bike':'teste', 'dog':'teste'}
#alarm1 = {"name":"alarm1", "time":t, "days":days}
#alarm2 = {"name":"alarm2", "time":t2, "days":days}
#alarms = [alarm1, alarm2]
#for a in alarms:
#    print(str(a["name"]))
#    print(str(a["time"]["start"]))
#
#points = [[[15,15],[15,65],[65,15],[65,65]]]
##
#status.addRegion("teste", "true", "true", alarms, objectType, 0.45, points)
#status.addRegion("teste2", "true2", "true2", t, days, objectType, 0.45, points)
##
#status.printRegions()
#status.deleteRegion(nameRegion="teste")
##
#status.saveRegionFile('region.teste.json')
#status2 = StatusConfig(regionsFile='region.teste.json')
#status.regions
#status.regions["regioes"][1]



