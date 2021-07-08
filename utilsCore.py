import cv2 as cv
#import pygame
import json
import os
import time
import logging as log
import sys
import shutil
from glob import glob
from datetime import datetime
import subprocess
import time
import locale
import simplejson as json
import secrets
import psutil
from pbkdf2 import PBKDF2

import winsound


from cryptography.fernet import Fernet

import http.client as httplib

OS_PLATFORM = 'windows'

if sys.platform == 'linux':
    OS_PLATFORM = 'linux'


#locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

#locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')
#timezone = pytz.timezone("America/Sao_Paulo")

locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
#locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    

#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', filename='pv.log')
#log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)

def getProcessId(name, path):
    listP = []
    for proc in psutil.process_iter():
        if proc.name() == name and proc.cwd() == path:            
            log.info('getProcessId:: Pid: {:d}'.format(proc.pid))
            log.info('getProcessId:: name: {}'.format(proc.name()))
            log.info('getProcessId:: Path: {}'.format(proc.cwd()))
            listP.append([proc.pid, proc.cwd()])
    return listP


def killProcessId(pid):
    log.info('killProcessId::')
    for proc in psutil.process_iter():
        if proc.pid == pid :            
            log.info('killProcessId:: Pid: {:d}'.format(proc.pid))
            log.info('killProcessId:: name: {}'.format(proc.name()))
            proc.kill()
            return True 
    return False 


def initWatchDog():

    DETACHED_PROCESS = 0x00000008
    log.info('initWatchDog...')

    
    if sys.platform == 'linux':    
        app = os.getcwd() + '/' + 'config/wd'
    else:
        log.info('Windows WatchDog')
        app = 'config/wd.exe'

    listP = getProcessId('wd.exe', os.getcwd())
    
    if  len(listP) == 0:
        try: 
            #subprocess.Popen(app, creationflags=DETACHED_PROCESS)
            #cmd = "<full filepath plus arguments of child process>"
            #cmds = shlex.split(app)
            #log.info('cmds: {}'.format(cmds))
            subprocess.Popen(app.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, start_new_session=True, close_fds=True)
            #p = subprocess.Popen(app.split(), shell=False)
            #(output, err) = p.communicate()
            #log.info("Command output: {}".format(output))
            #p_status = p.wait()
            #log.info('p_status: {}'.format(p_status))

        except Exception as e: 
            log.critical('initWatchDog:: Erro initWatchDog: {}'.format(e))
        else:
            listProc = getProcessId('wd.exe', os.getcwd())
            for proc in listP:
                pi = proc[0]
                pa = proc[1]
                log.info('initWatchDog:: WatchDog carregado. PID: {:d} ; Path: {}'.format(pi, pa))
    else:
        for proc in listP:
            pid = proc[0]
            path = proc[1]
            log.info('initWatchDog:: WatchDog rodando. Pid: {:d} ; Path: {}'.format(pid, path))


def stopWatchDog():
    log.info('stopWatchDog:: Encerrando Watchdog')

    if sys.platform == 'linux':    
        namePid = 'wd' 
    else:
        namePid = 'wd.exe' 

    listP = getProcessId(namePid, os.getcwd()) 
    
    for proc in listP:
        try:
            pid = proc[0]
            path = proc[1]
            log.info('\nstopWatchDog:: encerrando Pid: {:d} ; Path: {}'.format(pid, path))

            if OS_PLATFORM == 'linux':
                os.kill(pid, 9)
            else:
                #os.system("taskkill /f /pid " + str(pid))
                killProcessId(pid)
                #os.system("taskkill /f /im " + namePid)

        except Exception as e:
            log.error('stopWatchDog:: Erro matando processo: {:d}'.format(pid))
            log.error('stopWatchDog:: Error: {}'.format(e))
            killProcessId(pid)
        else:
            log.info('stopWatchDog:: WatchDog encerrado. PId: {:d}'.format(pid))

        #pid = getProcessId(namePid) 


def checkInternetAccess():

    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        log.info('Checando conexao...')
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        log.warning('Falha na conexao')
        conn.close()
        return False


def camSource(source = 'webcam'):
    status = True
    error = ''
    ipCam = None

    if source == 'webcam':        
        source = 0
        log.info('camSource:: WebCam')
        #ipCam = cv.VideoCapture(0)        
        #log.info('capturando da webcam')    

    try:
        log.info('camSource:: source: {}'.format(source))
        ipCam = cv.VideoCapture(source)
        
    except cv.error as e:
        status = False            
        log.critical('camSource:: error: {}'.format(e))        
        error = e
    else:       
        if ipCam.isOpened():
            log.info('camSource:: Imagem de camera ok')            
        else:
            if source == 0:
                error = 'webcam'
                log.info('camSource:: error webcam')
            else:
                error = 'rtsp'
                log.info('camSource:: error rtsp')
        
                

    return ipCam, error


def decrypt(token): 
     
    password = b'error'
    statusConfig = StatusConfig()
    
    key = b'x-LhW_rs81XBzuFLq9jgUFOcGbjDWwWXS5A7lpV0onQ='
    fernetKey = Fernet(key)
    
    #Fernet.generate_key()
    
        
    #token = statusConfig.dataLogin.get('passwd')
    
    try:
        password = fernetKey.decrypt(token.encode())

    except Exception as e:

        log.error('utils.decrypt: error: {}'.format(e))
    
    #log.info('decrypt passwd: {}'.format(password.decode()))
    
    return password.decode() 


def encrypt(password):
    
    token = 'error' 
    key = b'x-LhW_rs81XBzuFLq9jgUFOcGbjDWwWXS5A7lpV0onQ='    
    f = Fernet(key)

    try:
        token = f.encrypt(password.encode())    
    except Exception as e:
        
        log.error('utils.encrypt: error: {}'.format(e))
  
    return token


def getDirUsedSpace(start_path):

    total_size = 0

    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    #log.info('getDirUsed:used {:f}'.format(total_size))
    return (total_size / (2**30))

def getDiskUsedGb():
    statusConfig = StatusConfig()    
    particao = statusConfig.getDirVideosAllTime()
    particao = particao.split(':')
    if len(particao) > 1:
        particao = particao[0] + ':/'
    else:
        particao = '/'
    
    total, used, free = shutil.disk_usage(particao)
    return (used / (2**30))


def getNumDaysRecording():
    
    #cada dia consome +- 24 GB
    statusConfig = StatusConfig()    
    particao = statusConfig.getDirVideosAllTime()
    particao = particao.split(':')
    if len(particao) > 1:
        particao = particao[0] + ':/'
    else:
        particao = '/'
        
    total, used, free = shutil.disk_usage(particao)
    days = (free // (2**30)) / 24
    return int(days)


def getDiskUsageFreeGb():

    statusConfig = StatusConfig()    
    particao = statusConfig.getDirVideosAllTime()
    particao = particao.split(':')
    if len(particao) > 1:
        particao = particao[0] + ':/'
    else:
        particao = '/'

    total, used, free = shutil.disk_usage(particao)
    return (free / (2**30))


def getDiskUsageFree():

    statusConfig = StatusConfig()    
    particao = statusConfig.getDirVideosAllTime()
    particao = particao.split(':')
    if len(particao) > 1:
        particao = particao[0] + ':/'
    else:
        particao = '/'
    
    log.info('getDiskUsageFree:: particao: {}'.format(particao))    
    total, used, free = shutil.disk_usage(particao)
    #total, used, free = shutil.disk_usage("/")
    return int((free / total)*100)


def isDiskFull(diskMinUsage):
    
    statusConfig = StatusConfig()    
    particao = statusConfig.getDirVideosAllTime()
    particao = particao.split(':')
    if len(particao) > 1:
        particao = particao[0] + ':/'
    else:
        particao = '/'
        
        
    isFull = False 
    total, used, free = shutil.disk_usage(particao)

    if ((free / total)*100) <= float(diskMinUsage):
       
        isFull = True 

    return isFull


def freeDiskSpace(dirVideo):

     log.info('freeDiskSpace::')
     #locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

     #vai apagando um dia por vez até sobrar espaço
     #se não sobrar espaço, avisar o usuário que o disco está cheio por outros motivos
     
     statusConfig = StatusConfig()    
     monthList = []
     dirList = []
     yearList = []
     dirSorted = []
     daysSorted = []
     daysDir= []
     dayList = []
     
     totalLiberado = 0.0
     
     particao = dirVideo.split(':')
     
     if len(particao) == 1:        
        dirVideo = os.getcwd() + '/' + dirVideo       
     
     
     
     dirListFull = glob(dirVideo + '/*')
     #print('dirListFull : {}'.format(dirListFull))    
     
     for m in dirListFull:
        m = m.replace("\\","/")
        dirList.append(m.rsplit('/').pop().__str__())

     for y in dirList:
        y = y.replace("\\","/")
        yearList.append(y.rsplit('-').pop())
     
     for m in dirList:
        m = m.replace("\\","/")
        monthList.append(m.rsplit('-')[0])

     
     if (len(dirList) != 0):

        #dirSorted = sorted(dirList, key=lambda dirList: datetime.strftime(dirList,'%b-%Y'))
        dirSorted = sorted(dirList, key=lambda dirList: datetime.strptime(dirList,'%b-%Y'))

        daysDir = glob(dirVideo + '/' + dirSorted[0] + '/*')     
        
        # i = 0
        # for d in daysDir:
            # daysDir[i] = d.replace("\\","/")
            # i = i + 0
        
        
        for d in daysDir:
           #print('d: {}'.format(d))
           d = d.replace("\\","/")
           #print('d replaced: {}'.format(d))
           dayList.append(d.rsplit('/').pop())
            
        #print('dayList: {}'.format(dayList))

        daysSorted = sorted(dayList, key=lambda dayList: datetime.strptime(dayList,'%d'))
        
        #print('daysSorted: {}'.format(daysSorted))
        
        iDirSorted = 0 
        iDaysSorted = 0  

     
        while isDiskFull(statusConfig.getDiskMinUsage()) and (iDirSorted < len(dirSorted)):
               
            #proxima pasta a ser deletada
            if iDirSorted < len(dirSorted):
            
                if iDaysSorted < len(daysSorted):
                
                    oldestDir = dirVideo + '/' + dirSorted[iDirSorted] + '/' + daysSorted[iDaysSorted]                        
                    #print('dirVideo: {}'.format(dirVideo))
                    #oldestDir = oldestDir.replace("/","\\")
                    
                    #print('oldestDir: {}'.format(oldestDir))
                    # linux dirSpace = subprocess.check_output(['du','-sh', oldestDir]).split()[0].decode('utf-8')
                    #dirSpace = subprocess.check_output(['du','-sh', oldestDir]).split()[0].decode('utf-8')
                    dirSpace = 0
                    for filename in os.listdir(oldestDir):
                        dirSpace = os.path.getsize(os.path.join(oldestDir, filename))
                    #print('dirSpace: {}'.format(dirSpace))
                   
                    #deletar a pasta do ano/mes/dia mais antigo
                    try:
                        
                        shutil.rmtree(oldestDir)
                        
                    except OSError as e:
                        
                        log.critical('Diretorio nao encontrado')
                        log.critical("Error 1: %s : %s" % (oldestDir, e.strerror))
                        #se o diretorio foi apagado, pular para o proximo
                        iDirSorted = iDirSorted + 1
                        break

                        
                    else:
                        log.info('Diretorio {} removido. Foi liberado {} de espaço'.format(oldestDir, dirSpace))             
                        iDaysSorted = iDaysSorted + 1
                        #totalLiberado = totalLiberado + float(dirSpace)
                    
                else:
                    
                    log.info('Removendo diretorio que ficou vazaio')
                    #apagando o diretorio que ficou vazio
                    oldestDir = dirVideo + '/' + dirSorted[iDirSorted]
                    
                    iDirSorted = iDirSorted + 1
                    
                    try:
                        
                        shutil.rmtree(oldestDir)
                        
                    except OSError as e:
                        
                        log.critical('Diretorio nao encontrado')
                        log.crtical("Error 2: %s : %s" % (oldestDir, e.strerror))
                        break
                        
                    else:
                        log.info('Diretorio {} removido'.format(oldestDir))
            else:
               break
     else:
        #nao ha mais diretorios a serem apagados
        return False

       
     #log.info('Total liberado: {:f}'.format(totalLiberado))


def getDate():    
    
    #print (datetime.now().strftime('%a-%b-%d-%H:%M:%S-%Y'))
    
    #data = time.asctime().split(" ")
    data = datetime.now().strftime('%a-%b-%d-%H:%M:%S-%Y')
    
    data = data.split("-")
    
    month = data[1][0].upper() + data[1][1] + data[1][2]
    data = {'day':data[2], 'month':month,'hour':data[3], 'year':data[4], 'weekDay':data[0].lower(), 'minute':data[3].split(":")[1], 'hourOnly':data[3].split(":")[0]}
    #print('mes: {}'.format(month))
    #print('getDate data: {}'.format(data))
        
    # if data[0] == 'Mon': data[0] = 'Seg'
    # if data[0] == 'Tue': data[0] = 'Ter'
    # if data[0] == 'Wed': data[0] = 'Qua'
    # if data[0] == 'Thu': data[0] = 'Qui'
    # if data[0] == 'Fri': data[0] = 'Sex'
    # if data[0] == 'Sat': data[0] = 'Sab'
    # if data[0] == 'Sun': data[0] = 'Dom'
    
    # if data[1] == 'Jan': data[1] = 'Jan'
    # if data[1] == 'Feb': data[1] = 'Fev'
    # if data[1] == 'Mar': data[1] = 'Mar'
    # if data[1] == 'Apr': data[1] = 'Abr'
    # if data[1] == 'May': data[1] = 'Mai'
    # if data[1] == 'Jun': data[1] = 'Jun'
    # if data[1] == 'Jul': data[1] = 'Jul'
    # if data[1] == 'Aug': data[1] = 'Ago'
    # if data[1] == 'Sep': data[1] = 'Set'
    # if data[1] == 'Oct': data[1] = 'Out'
    # if data[1] == 'Nov': data[1] = 'Nov'
    # if data[1] == 'Dec': data[1] = 'Dez'
    
    
    #para dias com um digito
    # if data.count("") > 0:
        # data.remove("")
    #minute = data[3].split(":")[1]
    #hourOnly = data[3].split(":")[0]
    #weekDay = data[0].lower()
    #data = {'day':data[2], 'month':data[1],'hour':data[3], 'year':data[4], 'weekDay':data[0].lower(), 'minute':data[3].split(":")[1], 'hourOnly':data[3].split(":")[0]}
   
    #print('getDate data:' + str(data))
    
    return data


def createDirectory(dirVideos):

    #locale.setlocale(locale.LC_ALL, 'en_US.utf-8')

    date = getDate()
    month_dir = '/' + date['month'] + '-' + date['year']
    month_dir
    today_dir = '/' + date['day']
    current_dir =  dirVideos
    status = False
    status = False

    #checar se pasta do mes existe, ou cria-la
    try:
        os.makedirs(current_dir + month_dir + today_dir)

    except OSError as ex:

        if ex.errno == 17:
            log.info('createDirectory:: Diretorio ' + current_dir + month_dir + today_dir + ' existente.')
            status = True
        else:
            log.error('createDirectory:: Erro ao criar o diretorio: ' + current_dir + month_dir + today_dir)
            log.error(ex.__str__())

    else:
        log.info("createDirectory:: Diretorio " + current_dir + month_dir + today_dir + " criado com sucesso")
        status = True

    dir_temp = current_dir + month_dir + today_dir

    return status, dir_temp


class StatusConfig:

    
    camListAtivas = list() 
    
    camListEncontradas = list() 
    
    dataLogin = {
    
        "user"             : "nome@email.com",
        "passwd"           : "senha",
        "loginAutomatico"  : "False",
        "autoStart"        : "False"
    }


    data = {
            "isRecordingAllTime"    : "False",
            "isRecordingOnAlarmes"  : "True",
            "isOpenVino"            : "True",
            "camSource"             : "webcam",
            "prob_threshold"        : 0.60,
            # aponta para pastas dentro de dlModels
            "dnnModelPb"        : "./dlModels/ssd-mobilenet/frozen_inference_graph_v1_coco_2017_11_17.pb",
            "dnnModelPbTxt"     : "./dlModels/ssd-mobilenet/ssd_mobilenet_v1_coco_2017_11_17.pbtxt",
            "openVinoModelXml"  : "./computer_vision_sdk/deployment_tools/intel_models/person-vehicle-bike-detection-crossroad-0078/FP32/person-vehicle-bike-detection-crossroad-0078.xml",
            "openVinoCpuExtension" : "/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_avx2.so",
            "openVinoPluginDir" : "/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64",
            "openVinoModelBin"  : "./computer_vision_sdk/deployment_tools/intel_models/person-vehicle-bike-detection-crossroad-0078/FP32/person-vehicle-bike-detection-crossroad-0078.bin",
            "openVinoDevice"    : "CPU",
            "desativarAlarmes"  : "False",
            "emailConfig"    : [ {'port':'587', 
                              'smtp':'smtp.gmail.com',
                              'user':'user@user.com', 
                              'password':'password', 
                              'subject':'Alarme PV',
                              'to':'destiny@server.com'}],
            "dirVideos"      : "/home/igor/videos_alarmes",
            "camListAtivas" : []
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
    listEmails = list()

    def getActiveDevice(self):

        for m in self.data.get('openVinoModels'):
            if m.get('isActive') == "True":
                return m.get('openVinoDevice'), m.get('openVinoModelXml'), m.get('openVinoModelBin'), self.data["openVinoCpuExtension"], self.data["openVinoPluginDir"], m.get('name')

    def getDiskMinUsage(self):
        return self.data["storageConfig"]["diskMinUsage"]

    def getDiskMaxUsage(self):
        return self.data["diskMaxUsage"]
    
    def getCpuExtension(self):
        return self.data["openVinoCpuExtension"]
    
    def getPluginDir(self):
        return self.data["openVinoPluginDir"]
    
    def getDirVideosOnAlarmes(self):
        return self.data["dirVideosOnAlarmes"]
    
    def getDirVideosAllTime(self):
        return self.data["dirVideosAllTime"]
    
    def getEmailConfig(self):
        return self.data["emailConfig"]

    def getDesativarAlarmes(self):
        return self.data["desativarAlarmes"]
    
    def getPrimeiroUso(self):
        return self.data["primeiroUso"]
    
    def getLoginAutomatico(self):
        return self.dataLogin["loginAutomatico"]

    def getRegions(self):
        return self.regions

    def getRegion(self, name):
        region = None
        for r in self.regions:
            if r.get("nameRegion") == name:
                region = r

        return region

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

    def checkNameRegion(self, name):
        status = False
        for m in self.regions:
            if m.get('nameRegion') == name:
                status = True
        return status
   
    def addOpenVinoModels(self, isActive, name, openVinoModelXml, openVinoModelBin, openVinoCpuExtension, openVinoPluginDir, openVinoDevice):
        model = {
                    "isActive"         :isActive,
                    "name"             :name,
                    "openVinoModelXml" :openVinoModelXml,
                    "openVinoModelBin" :openVinoModelBin,
                    "openVinoDevice"   :openVinoDevice
        }

        self.data["openVinoCpuExtension"] = openVinoCpuExtension
        self.data["openVinoPluginDir"] = openVinoPluginDir
        
        #se ja existe, apenas edita os dados
        edit = False
        i = 0
        for m in self.data.get('openVinoModels'):
            if m.get('name') == name:
                self.data.get('openVinoModels')[i] = model
                edit = True
                break
            else:
                i = i+1

        if not edit:
            self.data.get('openVinoModels').append(model)

        self.saveConfigFile()


    def addStorageConfig(self, diskMaxUsage, diskMinUsage, spaceMaxDirVideosOnAlarme, spaceMaxDirVideosAllTime, eraseOldestFiles, stopSaveNewVideos):

        storageConfig = {
                "diskMaxUsage": diskMaxUsage,
                "diskMinUsage": diskMinUsage,
                "spaceMaxDirVideosAllTime": spaceMaxDirVideosAllTime,
                "spaceMaxDirVideosOnAlarme": spaceMaxDirVideosOnAlarme,
                "eraseOldestFiles": eraseOldestFiles,
                "stopSaveNewVideos": stopSaveNewVideos
                } 

        self.data["storageConfig"] = storageConfig

        self.saveConfigFile()

    def setUserNameLoginConfig(self, userName):
    
        self.dataLogin['user'] = userName
        self.saveConfigLogin()
    
    
    def addLoginConfig(self, userName, userPasswd, salvarLogin, loginAutomatico, autoStart):

        self.dataLogin['user'] = userName
        self.dataLogin['passwd'] = userPasswd
        self.dataLogin['salvarLogin'] = salvarLogin 
        self.dataLogin['loginAutomatico'] = loginAutomatico 
        self.dataLogin['autoStart'] = autoStart 

        self.saveConfigLogin()
        
    def getUserLogin(self):
        if len(self.dataLogin['user']) != 0:
            return self.dataLogin['user']
        else:
            return None
    
    def setPrimeiroUso(self, status):
        self.data['primeiroUso'] = status 
        self.saveConfigFile()


    def setLoginAutomatico(self, status):

        self.dataLogin['loginAutomatico'] = status 
        self.saveConfigLogin()
        
    def setAtalhoDesktop(self, status):
        self.dataLogin['atalhoDesktop'] = status 
        self.saveConfigLogin()
    
    def setLoginAutoStart(self, status):

        self.dataLogin['autoStart'] = status 
        self.saveConfigLogin()
    
    def setDesativarAlarmes(self, status):

        self.data['desativarAlarmes'] = status 
        self.saveConfigFile()
    
    
    def setLoginAutomatico(self, status):

        self.dataLogin['loginAutomatico'] = status 
        self.saveConfigLogin()

    def setConfigGravacao(self, isRecordingAllTime, isRecordingOnAlarmes, dirVideosAllTime, dirVideosOnAlarmes, camSource, diskMinUsage):
        self.data["isRecordingAllTime"] = isRecordingAllTime
        self.data["isRecordingOnAlarmes"] = isRecordingOnAlarmes
        self.data["dirVideosAllTime"] = dirVideosAllTime
        self.data["dirVideosOnAlarmes"] = dirVideosOnAlarmes
        self.data["camSource"] = camSource        
        self.data["diskMinUsage"] = diskMinUsage
        
        self.saveConfigFile()
    
    def setRtspConfig(self, camSource):
        self.data["camSource"] = camSource

    def addConfigGeral(self, name, servidorEmail, user, password, subject, to, isRecordingAllTime, isRecordingOnAlarmes, dirVideosAllTime, dirVideosOnAlarmes, camSource, diskMinUsage):
        
        if servidorEmail == 'Gmail':
            port = '587'
            smtp = 'smtp.gmail.com'
        
        elif servidorEmail == 'Outlook':
            port = '587'
            smtp = 'smtp.office365.com'
            
        elif servidorEmail == 'Yahoo':
            port = '995'
            smtp = 'smtp.mail.yahoo.com'
        
            
        email = {'name':name,
                 'servidorEmail':servidorEmail,
                 'port':port,
                 'smtp':smtp,
                 'user':user,
                 'password':password,
                 'subject':subject,
                 'to':to
                }

        self.data["isRecordingAllTime"] = isRecordingAllTime
        self.data["isRecordingOnAlarmes"] = isRecordingOnAlarmes
        self.data["dirVideosAllTime"] = dirVideosAllTime
        self.data["dirVideosOnAlarmes"] = dirVideosOnAlarmes
        self.data["camSource"] = camSource
        self.data["emailConfig"] = email
        self.data["diskMaxUsage"] = "85" 
        self.data["diskMinUsage"] = diskMinUsage

        self.saveConfigFile()

    def setConfig(self, isRecordingAllTime, isRecordingOnAlarmes, isOpenVino,
                      dnnModel, openVinoModel, emailConfig, dirVideos, camSource, openVinoDevice, prob_threshold):
        self.data["isRecordingAllTime"]       = isRecordingAllTime
        self.data["isRecordingOnAlarmes"]     = isRecordingOnAlarmes
        self.data["camSource"]                = camSource
        self.data["prob_threshold"]           = prob_threshold
        self.data["isOpenVino"]               = isOpenVino
        self.data["dnnModelPb"]               = dnnModelPb
        self.data["dnnModelPbTxt"]            = dnnModelPbTxt
        self.data["openVinoDevice"]           = openVinoDevice
        self.data["openVinoModel"]            = openVinoModel
        self.data["openVinoCpuExtension"]     = openVinoCpuExtension
        self.data["dirVideosOnAlarmes"]       = dirVideosOnAlarmes
        self.data["emailConfig"]              = emailConfig #list of emails
        self.data["diskMaxUsage"]             = diskMaxUsage 
        self.data["diskMinUsage"]             = diskMinUsage

        #self.data["emailConfig"]["port"]      = emailConfig["port"]
        #self.data["emailConfig"]["smtp"]      = emailConfig["smtp"]
        #self.data["emailConfig"]["user"]      = emailConfig["user"]
        #self.data["emailConfig"]["password"]  = emailConfig["password"]
        #self.data["emailConfig"]["subject"]   = emailConfig["subject"]
        #self.data["emailConfig"]["to"]        = emailConfig["to"]

    def zerarListCamEncontradasConfig(self):
        self.data["camListEncontradas"] = [] 
        self.saveConfigFile()
    
    def zerarListCamAtivasConfig(self):
        self.data["camListAtivas"] = [] 
        self.saveConfigFile()
    
    def addListCamEncontradasConfig(self, listCam):
        self.data["camListEncontradas"] = listCam 
        self.saveConfigFile()

    def addListCamAtivasConfig(self, listCam):
        self.data["camListAtivas"] = listCam
        self.saveConfigFile()
    
    def getListCamEncontradas(self):
        return self.data["camListEncontradas"]
    
    def getListCamAtivas(self):
        return self.data["camListAtivas"]

    
    def getCamEmUsoConfig(self):
        camEmuso = None
        for cam in self.data['camListAtivas']:
            if cam['emUso'] == 'True':
                camEmuso = cam                
                break
        
        return camEmuso 


    
    def addCamAtivaConfig(self, idCam, ip, mac, port, user, passwd, channel, source, emUso):

        cam = {
            "idCam"          : idCam,
            "ip"             : ip,
            "mac"            : mac,
            "user"           : user,
            "passwd"         : passwd,
            "channel"        : channel,
            "source"         : source,
            "emUso"          : emUso,
        }

        #self.dataCam.append(cam)
        self.data["camListAtivas"] = self.dataCam 
        self.saveConfigFile()

    def addCamEncontradaConfig(self, nome, idCam, ip, mac, port, user, passwd, channel, source):

        cam = {
            "nome"           : nome,
            "idCam"          : idCam,
            "ip"             : ip,
            "mac"            : mac,
            "user"           : user,
            "passwd"         : passwd,
            "channel"        : channel,
            "source"         : source,
            "emUso"          : 'False',
        }

        
        self.data["camListAtivas"].append(cam)
        self.saveConfigFile()

    def addRegion(self, nameRegion, alarm, objectType, prob_threshold, pointsPolygon):

        region = {
            "nameRegion"     : nameRegion,
            "alarm"          : alarm,
            "objectType"     : objectType,
            "prob_threshold" : prob_threshold,
            "pointsPolygon"  : pointsPolygon
        }

        edit = False
        i = 0
        for r in self.regions:
            #salvar apenas as informações da regiao, e não do alarme
            if r.get('nameRegion') == nameRegion:
                self.regions[i]['objectType']       = objectType
                self.regions[i]['prob_threshold']   = prob_threshold 
                edit = True
                break
            else:
                i = i+1

        if not edit:
            self.regions.append(region)

        self.saveRegionFile()

        
    def addAlarm(self, idRegion, alarm):

        log.info('addAlarm::')
        edit = False
        i = 0
        #print('addAlarm:: idRegion: {:d}'.format(idRegion))
        #print('addAlarm:: regionsLen: {:d}'.format(len(self.regions)))
        
        if len(self.regions) > 0:
            if idRegion <= (len(self.regions) - 1):            
                for a in self.regions[idRegion].get('alarm'):                            
                    if a.get('name') == alarm['name']:                
                        #print('edit true')
                        self.regions[idRegion].get('alarm')[i] = alarm
                        edit = True
                        break
                    else:
                        i = i+1
            
            if not edit:
                self.regions[idRegion].get('alarm').append(alarm)

            self.saveRegionFile()
        #TO-DO try catch toleranca a falhas


    def __init__(self, configFile='config/config.json', regionsFile='config/regions.json', configLogin='config/lconfig.json'):

        #configuracoes setadas pelo arquivo sobrescrevem as configuracoes padroes
        self.readConfigFile(configFile)
        self.readRegionsFile(regionsFile)
        self.readConfigLogin(configLogin)

    def readConfigLogin(self, fileName = 'config/lconfig.json'):
        #log.info('Lendo arquivo de configuração: ' + os.getcwd() + '/' + fileName)
        self.dataLogin = json.load(open(fileName,'r'))


    def readConfigFile(self, fileName = 'config/config.json'):
        #log.info('Lendo arquivo de configuração: ' + os.getcwd() + '/' + fileName)
        self.data = json.load(open(fileName,'r'))

    def readRegionsFile(self, fileName = 'config/regions.json'):
        log.info('Lendo arquivo de regiões: ' + os.getcwd() + '/' + fileName)
        try:
            self.regions = json.load(open(fileName,'r'))
        except OSError as ex:

            log.critical('Arquivo de Regioes inexistente - será criado um novo arquivo') 
        else:
            log.info('Arquivo de regiões lido com sucesso')


    def deleteAlarm(self, regionName, alarmName):

        indexRegion = 0
        indexAlarm = 0

        for r in self.regions:
            if r.get("nameRegion") == regionName:
                for a in r.get('alarm'):
                    if a.get('name') == alarmName:
                        del self.regions[indexRegion].get('alarm')[indexAlarm]
                    indexAlarm = indexAlarm+1
               # return True

            indexRegion = indexRegion+1
        #return False

        #self.saveConfigFile()
        self.saveRegionFile()

    def checkDuplicatedActiveModels(self):
        i = 0
        status = True
        for m in self.data.get('openVinoModels'):
            if m.get('isActive') == "True":
                i = i + 1

        if i > 1:
            status = False

        return status

    def checkActiveModel(self):

        status = False

        for m in self.data.get('openVinoModels'):
            if m.get('isActive') == "True":
                status = True
                break

        return status


    def deleteModel(self, modelName):
        status = False
        i = 0

        if self.checkActiveModel() and len(self.data.get('openVinoModels')) == 1:
                log.info('WARNING: deve haver ao menos 1 modelo ativo')
                status = False
        else:
            for m in self.data.get('openVinoModels'):
                if m.get('name') == modelName:
                    log.info('deletando {}'.format(self.data.get('openVinoModels')[i].get('name')))
                    del self.data.get('openVinoModels')[i]
                    status = True
                else:
                    i = i+1

        self.saveConfigFile()
        return status

    def deleteRegion(self, nameRegion='regions1'):
        i = 0
        for r in self.regions:
            if r.get("nameRegion") == nameRegion:
                del self.regions[i]
                self.saveRegionFile()
                log.info("Regiao '{}' removido com sucesso".format(nameRegion))

            i = i+1
        #return False


    def printConfig(self):
        print('--- Config status  ---')
        print('isRecordingAllTime:      {}'.format(self.data.get('isRecordingAllTime')))
        print('isRecordingOnAlarmes:    {}'.format(self.data.get('isRecordingOnAlarmes')))
        print('isEmailAlert:            {}'.format(self.data.get('isEmailAlert')))
        print('isGateSelected:          {}'.format(self.data.get('isGateSelected')))
        print('isSoundAlert:            {}'.format(self.data.get('isSoundAlert')))
        print('prob_threshold:          {}'.format(self.data.get('prob_threshold')))
        print('camSource:               {}'.format(self.data.get('camSource')))
        print('isOpenVino:              {}'.format(self.data.get('isOpenVino')))
        print('dnnModelPb:              {}'.format(self.data.get('dnnModelPb')))
        print('dnnModelPbTxt:           {}'.format(self.data.get('dnnModelPbTxt')))
        print('openVinoModelXml:        {}'.format(self.data.get('openVinoModelXml')))
        print('openVinoModelBin:        {}'.format(self.data.get('openVinoModelBin')))
        print('openVinoCpuExtension:    {}'.format(self.data.get('openVinoCpuExtension')))
        print('openVinoPluginDir:       {}'.format(self.data.get('openVinoPluginDir')))
        #TODO printar lista de emails
        print('emailConfig/user:        {}'.format(self.data.get('emailConfig').get('user')))
        print('emailConfig/smtp:        {}'.format(self.data.get('emailConfig').get('smtp')))
        print('emailConfig/port:        {}'.format(self.data.get('emailConfig').get('port')))
        print('dirVideosOnAlarmes:      {}'.format(self.data.get('dirVideosOnAlarmes')))


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

    def saveRegionFile(self, file = 'config/regions.json'):
        log.info('Salvando arquivo de regiones: ' + os.getcwd() + '/' + file)
        try:
            json.dump(self.regions, open(file, 'w'), indent=4)

        except OSError as ex:

            log.critical('Erro ao salvar arquivo {}'.format(file))

        else:
            log.info('Arquivo {} salvo'.format(file))


    def saveConfigFile(self, fileName = 'config/config.json'):
        log.info('Salvando arquivo de configuração: {}/{}'.format(os.getcwd(), fileName))
        #json.dump(self.data, open(file,'w'), indent=4)
        
        try:
            fp = open(fileName,"w")
            fp.write(json.dumps(self.data, indent = 4))
        finally:
            fp.close()

        log.info('Salvando arquivo de configuração: {}/{}'.format(os.getcwd(), fileName))

    def saveConfigLogin(self, fileName = 'config/lconfig.json'):
        
        #try:
        #    fp = open("passwords.json","r")
        #    obj = json.load(fp)
        #except:
        #    fp = open("passwords.json","r")
        #    obj = json.load(fp)
        #finally:
        #    fp.close()
        try:
            fp = open(fileName,"w")
            fp.write(json.dumps(self.dataLogin, indent = 4))
        finally:
            fp.close()

        log.info('Salvando arquivo de configuração: {}/{}'.format(os.getcwd(), fileName))
        #json.dump(self.dataLogin, open(file,'w'), indent=4)


def playSound():
    
    log.info('utilsCore:: campainha tocada')
    # winsound.PlaySound('filename', flag)
    winsound.PlaySound('config/campainha.wav', winsound.SND_FILENAME)	

    #pygame.init()
    
    #pygame.mixer.music.load('config/campainha.mp3')
    #pygame.mixer.init()
    #pygame.mixer.music.play(0)

