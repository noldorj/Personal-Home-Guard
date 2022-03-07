import cv2 as cv
#import pygame
import json
import os
import time
#import logging as log
import logging
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
from PyQt5 import QtTest

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import storage
from firebase_admin import db


import platform
import locale


from cryptography.fernet import Fernet

import http.client as httplib

OS_PLATFORM = 'windows'

if sys.platform == 'linux':
    OS_PLATFORM = 'linux'
else:
    import winsound
    
#log.root.setLevel(log.INFO)
#log.basicConfig()

#for handler in log.root.handlers[:]:
#    log.root.removeHandler(handler)

#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, handlers=[log.FileHandler('config/pv.log', 'w', 'utf-8')])
#log.getLogger('socketio').setLevel(log.ERROR)
#log.getLogger('engineio').setLevel(log.ERROR)

log = logging.getLogger('pv-log')
log.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('config/pv.log', 'w', 'utf-8')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter("[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
log.addHandler(ch)
log.addHandler(fh)


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

if not firebase_admin._apps:
    log.info('initFormConfig:: carregando Certificado Firebase')
    try:
        credential = credentials.Certificate(cred)
    except Exception as err:
        log.critical('initFormConfig:: Certificado não encontrado - Erro: {} '.format(err))
    else:        
        log.info('initFormConfig:: Inicializando Firebase')

        try:
            firebase_app_pv = firebase_admin.initialize_app(credential, {'storageBucket': 'pvalarmes-3f7ee.appspot.com', 'databaseURL': 'https://pvalarmes-3f7ee-default-rtdb.firebaseio.com/'})
        except Exception as err:
            print('Erro ao inicializar o Firebase: {}'.format(err))            
        else:
            print('utilscore:: Firebase inicializado com sucesso')



#locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

#locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')
#timezone = pytz.timezone("America/Sao_Paulo")

#locale.setlocale(locale.LC_ALL, 'en_US.utf-8')

def setLocaleWindows():

    plat = platform.platform()
    
    if 'Windows-7' in plat:
        try:
            for x in locale.windows_locale.values():
                if 'en_US' in x:
                    x.replace('_','-')
                    locale.setlocale(locale.LC_ALL, x)
                    break                    
                elif 'pt_BR' in x:                    
                    x.replace('_','-')
                    locale.setlocale(locale.LC_ALL, x)
                    break
                elif 'pt_PT' in x:                    
                    x.replace('_','-')
                    locale.setlocale(locale.LC_ALL, x)
                    break
                   
        except Exception as error:
            log.error('setLocaleWindows:: win7 error: {}'.format(error))
        else:
            log.info('setLocaleWindows setLocale ok win7')
    else:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except Exception as err:
            log.error('setLocaleWindows:: win10 error: {}'.format(error))
        else:
            log.info('setLocaleWindows setLocale ok win10')
            
        
        
            
if OS_PLATFORM == 'windows':
    setLocaleWindows()
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
    #print('token: {}'.format(token))
    #print('token decode: {}'.format(token.decode()))
    
    
    try:
        password = fernetKey.decrypt(token.encode())

    except Exception as e:
    
        log.error('::utilsCore.decrypt: error: {}'.format(e))
    
    
    
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

    #garantir um minimo de disco para funcionamento do sistema
    if float((free / total)*100) < 5.0:
        diskMinUsage = 5        
        logger = logging.getLogger()
        logger.disabled = True
        log.critical('isDiskFull:: desabilitando log')
    else:
        logger = logging.getLogger()
        logger.disabled = True
        log.critical('isDiskFull:: reabilitando log')
    
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

def getMonthDigit(month):

    if month == 'Jan': month = '01'
    if month == 'Feb': month = '02'
    if month == 'Mar': month = '03'
    if month == 'Apr': month = '04'
    if month == 'May': month = '05'
    if month == 'Jun': month = '06'
    if month == 'Jul': month = '07'
    if month == 'Aug': month = '08'
    if month == 'Sep': month = '09'
    if month == 'Oct': month = '10'
    if month == 'Nov': month = '11'
    if month == 'Dec': month = '12'
    
    return month

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
    
    firebase_app = None
    
    camListAtivas = list() 
    
    camListEncontradas = list() 
    
    
    dataLogin = {
    
        "user"             : "",
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
        "prob_threshold"    : 0.65,
        "timerAlerta"    : 0,
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
    
    def getDateSessionInit(self):
        return self.data["dateSessionInit"]
    
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
        
    def getTimeAlerta(self):
        return int(self.data["timerAlerta"])
    
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
        self.updateConfigFileNuvem()


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
        self.updateConfigFileNuvem()

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
    
    def setFirebaseApp(self, firebaseApp):
        self.firebase_app = firebaseApp
    
    def setPrimeiroUso(self, status):
        self.data['primeiroUso'] = status 
        self.saveConfigFile()
        self.updateConfigFileNuvem()


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
        self.updateConfigFileNuvem()
    
    
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
        self.updateConfigFileNuvem()
    
    def isNuvemRunning(self):
        
        log.info('isNuvemRunning::')
        #TO-DO inicializar readConfigFile adequadamente
        self.readConfigFile()
        #self.data = json.load(open('config/config.json','r'))        
        
        #print('isNuvemRunning:: nuvemConfig: {}'.format(self.data["nuvemConfig"]["isRunning"]))
        return (self.data["nuvemConfig"]["isRunning"] == "True")
    
    def getStoragePlan(self):
        return self.data["nuvemConfig"]["storagePlan"]
    
    def setNuvemConfig(self, isRunning ):
        log.info('setNuvemConfig::')
        log.info('setNuvemConfig: {}'.format(isRunning))
        
        nuvemConfig = {
            "isRunning" : isRunning,
            "storagePlan"   : 0
        }        
        self.data["nuvemConfig"] = nuvemConfig
        self.saveConfigFile()
        self.updateConfigFileNuvem()

    def setRtspConfig(self, camSource):
        self.data["camSource"] = camSource
        self.saveConfigFile()
        self.updateConfigFileNuvem()
        
    def setDateSessionInit(self):
        date = getDate()
        date = date['year'] + '-' + getMonthDigit(date['month']) + '-' + date['day'] + ' ' + date['hour']
        print('date: {}'.format(date))
        self.data["dateSessionInit"] = date
        self.saveConfigFile()
        self.updateConfigFileNuvem()

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
        self.updateConfigFileNuvem()

    def setConfig(self, isRecordingAllTime, isRecordingOnAlarmes, isOpenVino,
                      dnnModel, openVinoModel, emailConfig, dirVideos, camSource, openVinoDevice, prob_threshold, timerAlerta):
        self.data["isRecordingAllTime"]       = isRecordingAllTime
        self.data["isRecordingOnAlarmes"]     = isRecordingOnAlarmes
        self.data["camSource"]                = camSource
        self.data["prob_threshold"]           = prob_threshold
        self.data["timerAlerta"]              = timerAlerta
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
        self.updateConfigFileNuvem()
    
    def addListCamEncontradasConfig(self, listCam):
        if listCam:
            self.data["camListEncontradas"] = listCam 
        else:
            self.data["camListEncontradas"] = []
        
        self.saveConfigFile()
        self.updateConfigFileNuvem()

    def addListCamAtivasConfig(self, listCam):
        if len(listCam) > 0:
            self.data["camListAtivas"] = listCam
        else:
            self.data["camListAtivas"] = []
            
        self.saveConfigFile()
        self.updateConfigFileNuvem()
    
    def getListCamEncontradas(self):
        
        #print('camListEncontradas: {}'.format(self.data["camListEncontradas"]))
        listCam = []
        try:
            listCam = self.data["camListEncontradas"]
        except:
            log.info('getListCamEncontradas:: sem cameras encontradas')
        else:
        
            if len(listCam) > 0:
                return self.data["camListEncontradas"]
            else:
                self.data["camListEncontradas"] = []
                self.saveConfigFile()
        self.updateConfigFileNuvem()
           
    
    def getListCamAtivas(self):
        
        listCam = []
        try:
            listCam = self.data["camListAtivas"]
        except:
            log.info('getListCamAtivas:: sem cameras ativas')
        else:
        
            if len(listCam) > 0:
                return self.data["camListAtivas"]
            else:
                self.data["camListAtivas"] = []
                self.saveConfigFile()
        self.updateConfigFileNuvem()

    
    def getCamEmUsoConfig(self):
        camEmuso = None
        for cam in self.data['camListAtivas']:
            if cam is not None:
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
        self.updateConfigFileNuvem()

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
        self.updateConfigFileNuvem()

    def addRegion(self, nameRegion, alarm, objectType, prob_threshold, pointsPolygon, timerAlerta):

        log.info('addRegion:: salvando a regiao: {}'.format(nameRegion))
        region = {
            "nameRegion"     : nameRegion,
            "alarm"          : alarm,
            "objectType"     : objectType,
            "prob_threshold" : prob_threshold,
            "pointsPolygon"  : pointsPolygon,
            "timerAlerta"    : timerAlerta
        }

        edit = False
        i = 0
        for r in self.regions:
            #salvar apenas as informações da regiao, e não do alarme
            if r.get('nameRegion') == nameRegion:
                self.regions[i]['objectType']       = objectType
                self.regions[i]['prob_threshold']   = prob_threshold 
                self.regions[i]['timerAlerta']      = timerAlerta 
                edit = True
                break
            else:
                i = i+1

        if not edit:
            self.regions.append(region)

        self.saveRegionFile()

        
    def addAlarm(self, idRegion, alarm):

        log.info('addAlarm:: salvando alarme')
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
        log.info('utilsCore:: __init__ statusConfig')
        self.readConfigFile(configFile)
        self.readRegionsFile(regionsFile)
        self.readConfigLogin(configLogin)
    
    def initFirebaseAdmin(self):
        if not firebase_admin._apps:            
            print('initFirebaseAdmin:: firebase nao inicializado')
            try:
                credential = credentials.Certificate(cred)
            except Exception as err:
                log.critical('initFormConfig:: Certificado não encontrado - Erro: {} '.format(err))
            else:        
                log.info('initFirebaseAdmin:: Inicializando Firebase')

            try:
                firebase_app_pv = firebase_admin.initialize_app(credential, {'storageBucket': 'pvalarmes-3f7ee.appspot.com', 'databaseURL': 'https://pvalarmes-3f7ee-default-rtdb.firebaseio.com/'})
            except Exception as err:
                print('initFirebaseAdmin:: Erro ao inicializar o Firebase: {}'.format(err))            
            else:
                print('initFirebaseAdmin:: Firebase inicializado com sucesso')
    
    def readConfigLogin(self, fileName = 'config/lconfig.json'):
        #log.info('readConfigLogin:: Lendo arquivo de configuração: ' + os.getcwd() + '/' + fileName)
        
        self.dataLogin = json.load(open(fileName,'r'))
        #print('dataLogin local: {}'.format(self.dataLogin))
        #print(' ')
        #print(' ')
        
        user = self.getUserLogin()
        userId = user.replace('.','_')
        userId = userId.replace('@','_')
        
        if userId != '':
        
            self.initFirebaseAdmin()
            
            try:
                ref = db.reference('/users/' + userId + '/configLogin')
            except Exception as e:
                print('readConfigLogin:: erro getting configLogin: {}'.format(e))
            else:            
                self.dataLogin = ref.get()
                #print('dataLogin firebase: {}'.format(ref.get()))
        


    def readConfigFile(self, fileName = 'config/config.json'):
        #log.info('Lendo arquivo de configuração: ' + os.getcwd() + '/' + fileName)
        
        
        log.info('readConfigFile::')
        #print('readConfigFile::')
        
        try:
            self.data = json.load(open(fileName,'r'))        
            
        except Exception as e:            
            print('readConfigFile:: error: {}'.format(e))
            
        else:
            log.info('readConfigFile:: lendo config.json ok')
        
        
        self.dataLogin = json.load(open('config/lconfig.json','r'))
        
        user = self.getUserLogin()
        userId = user.replace('.','_')
        userId = userId.replace('@','_')
        
        if checkInternetAccess():
        
            if userId != '':
            
                self.initFirebaseAdmin()
                
                try:
                    ref = db.reference('/users/' + userId + '/config')
                except Exception as e:
                    log.error('readConfigFile:: error getting config: {}'.format(e))
                else:                            
                    try:
                        self.data = ref.get()
                    except Exception as e:
                        log.error('readConfigFile:: erro sync com Firebase config-  ref.get() error: {}'.format(e))
                    else:
                        self.saveConfigFile()
                    #print('dataLogin firebase: {}'.format(ref.get()))
        else:
            log.error('readConfigFile:: Sem internet! impossivel sincronizar dados de config com Firebase ')
            print('readConfigFile:: Sem conexao com a internet - impossivel sincronizar dados de Config com o Firebase')

    def readRegionsFile(self, fileName = 'config/regions.json'):
        #log.info('readRegionsFile:: Lendo arquivo de regiões: ' + os.getcwd() + '/' + fileName)
        try:
            self.regions = json.load(open(fileName,'r'))
        except OSError as ex:

            log.critical('readRegionsFile:: Arquivo de Regioes inexistente - será criado um novo arquivo') 
        else:
            log.info('readRegionsFile:: Arquivo de regiões lido com sucesso')
            
        self.dataLogin = json.load(open('config/lconfig.json','r'))
        
        user = self.getUserLogin()
        userId = user.replace('.','_')
        userId = userId.replace('@','_')
        
        if userId != '':
        
            self.initFirebaseAdmin()
            
            try:
                ref = db.reference('/users/' + userId + '/regions')
            except Exception as e:
                log.error('readRegionsFile:: erro getting config: {}'.format(e))
            else:            
                if not ref.get():
                    #print('region vazia firebase')
                    self.regions = list()
                else:
                    self.regions = ref.get()
                    self.saveRegionFile()
                
                #print('regions firebase: {}'.format(ref.get()))


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
        self.updateConfigFileNuvem()

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
        self.updateConfigFileNuvem()
        return status

    def deleteRegion(self, nameRegion='regions1'):
        log.info('deleteRegion:: pressed')
        print('deleteRegion')
        i = 0
        for r in self.regions:
            if r.get("nameRegion") == nameRegion:
                del self.regions[i]
                self.saveRegionFile()
                print('regiao deletada')
                log.info("deleteRegion:: Regiao '{}' removido com sucesso".format(nameRegion))

            i = i+1
        #return False
        self.saveRegionFile()
        


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
        
        log.info('saveRegionFile:: Salvando arquivo de regioes: ' + os.getcwd() + '/' + file)
        
        #salvando na Nuvem Firebase
        #Estrutura para salvar no Realtime DAtabase 
        user = self.getUserLogin()
        userId = user.replace('.','_')
        userId = userId.replace('@','_')
            
        self.initFirebaseAdmin()
        
        ref = db.reference('/users/' + userId + '/regions')
    
        statusFirebase = False       
       
        
        i = 1
        while statusFirebase is False:
            log.info('saveRegionFile:: Savando dataLogin no Firebase tentativa [{}]'.format(i))
            try:
                ref.set(self.regions)
            except Exception as e:
                log.critical('saveRegionFile:: Erro salvar Config status no Firebase DB')                
                i = i + 1
                QtTest.QTest.qWait(5000)
                #time.sleep(0.5)
            else:
                statusFirebase = True
                i = 0

        
        try:
            log.info('saveRegionFile:: salvando regiao localmente')
            json.dump(self.regions, open(file, 'w'), indent=4)

        except OSError as ex:

            log.critical('Erro ao salvar arquivo {}'.format(file))

        else:
            log.info('Arquivo {} salvo'.format(file))


    def updateConfigFileNuvem(self):    
        
        print('updateConfigFileNuvem:: ')
        log.info('updateConfigFileNuvem::')
        
        #json.dump(self.data, open(file,'w'), indent=4)
        
        #salvando na Nuvem Firebase
        #Estrutura para salvar no Realtime DAtabase 
        user = self.getUserLogin()
        userId = user.replace('.','_')
        userId = userId.replace('@','_')        
        
        ref = db.reference('/users/' + userId + '/config')
    
        statusFirebase = False
        
        i = 1
        while not statusFirebase:
            log.info('updateConfigFileNuvem:: Savando config status no Firebase tentativa [{}]'.format(i))
            print('updateConfigFileNuvem:: Savando config status no Firebase tentativa [{}]'.format(i))
            try:
                ref.set(self.data)
            except Exception as e:
                log.critical('updateConfigFileNuvem:: Erro salvar Config status no Firebase DB')
                i = i + 1
                #time.sleep(0.5)
                QtTest.QTest.qWait(5000)
            else:
                statusFirebase = True
                log.info('updateConfigFileNuvem:: statusFirebase true')
                i = 0
    
    
    def saveConfigFile(self, fileName = 'config/config.json'):
        
        #print('saveConfigFile:: ')
        #salvando configfile localmente
        try:
            fp = open(fileName,"w")
            fp.write(json.dumps(self.data, indent = 4))
        finally:
            fp.close()

        log.info('saveConfigFile:: Salvando arquivo de configuração: {}/{}'.format(os.getcwd(), fileName))

    def saveConfigLogin(self, fileName = 'config/lconfig.json'):
        
        log.info('saveConfigLogin:: Salvando arquivo de configuração: {}/{}'.format(os.getcwd(), fileName))
        
        #try:
        #    fp = open("passwords.json","r")
        #    obj = json.load(fp)
        #except:
        #    fp = open("passwords.json","r")
        #    obj = json.load(fp)
        #finally:
        #    fp.close()
        
        #salvando na Nuvem Firebase
        #Estrutura para salvar no Realtime DAtabase 
        user = self.getUserLogin()
        userId = user.replace('.','_')
        userId = userId.replace('@','_')    
        
        ref = db.reference('/users/' + userId + '/configLogin')
    
        statusFirebase = False
        
        i = 1
        while statusFirebase is False:
            log.info('saveConfigLogin:: Savando dataLogin no Firebase tentativa [{}]'.format(i))
            try:
                ref.set(self.dataLogin)
            except Exception as e:
                log.critical('saveConfigLogin:: Erro salvar Config status no Firebase DB')
                i = i + 1
                QtTest.QTest.qWait(5000)
                #time.sleep(0.5)
            else:
                statusFirebase = True
                i = 0
        
        
        try:
            fp = open(fileName,"w")
            fp.write(json.dumps(self.dataLogin, indent = 4))
        finally:
            fp.close()

        log.info('Salvando arquivo de configuração: {}/{}'.format(os.getcwd(), fileName))
        #json.dump(self.dataLogin, open(file,'w'), indent=4)


def playSound():    
    
    log.info('utilsCore:: campainha tocada')
    
    if OS_PLATFORM == 'linux':
        import pygame
        pygame.init()        
        pygame.mixer.music.load('config/campainha.mp3')
        pygame.mixer.init()
        pygame.mixer.music.play(0)
    else:
        # winsound.PlaySound('filename', flag)
        winsound.PlaySound('config/campainha.wav', winsound.SND_FILENAME)

