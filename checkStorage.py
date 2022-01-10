from utilsCore import StatusConfig
from inferenceCore import *
from Utils_tracking import sendMailAlert
from Utils_tracking import sendMail
from Utils_tracking import sendStorageAlert
from Utils_tracking import saveStorageInfoDb
from Utils_tracking import savePvStatusDb
from camRunTime import CamRunTime
import utilsCore as utils
import time
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
import psutil
import urllib.request
import logging as log

log.root.setLevel(log.DEBUG)
log.basicConfig()

for handler in log.root.handlers[:]:
    log.root.removeHandler(handler)

log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, handlers=[log.FileHandler('config/pv.log', 'w', 'utf-8')])
log.getLogger('socketio').setLevel(log.ERROR)
log.getLogger('engineio').setLevel(log.ERROR)


class CheckStorage(QThread):

    camRunTime = CamRunTime()
    statusConfig = None
    updateStorageInfo = pyqtSignal()
    warningHDCheio = pyqtSignal()
    CHECK_STORAGE_TIME = 300
    checkStorageRun = True
    ipExterno = ''

    def __init__(self, camRunTime):
        log.info('CheckStorage::init')
        super().__init__()
        self._run_flag = True
        self.camRunTime = camRunTime
        self.statusConfig = camRunTime.statusConfig
        
        
        
        try:
            self.ipExterno = urllib.request.urlopen('http://ident.me').read().decode('utf8')
            
        except: 
        
            log.error('self.ipExterno error')
            
        else:
            log.info('CheckStorage::__init__:: External IP: {}'.format(self.ipExterno)) 
        
            


    def run(self):
    
        log.info('CheckStorage::run')

        self.camRunTime.dirVideosOnAlarmesUsedSpace = utils.getDirUsedSpace(self.statusConfig.data["dirVideosOnAlarmes"])
        self.camRunTime.isDiskFull = utils.isDiskFull(self.camRunTime.diskMinUsage) 
        self.camRunTime.diskUsageFree = utils.getDiskUsageFree() 
        self.camRunTime.diskUsageFreeGb = utils.getDiskUsageFreeGb()
        self.camRunTime.dirVideosAllTimeUsedSpace = utils.getDirUsedSpace(self.statusConfig.data['dirVideosOnAlarmes'])
        self.camRunTime.numDaysRecording = utils.getNumDaysRecording()  

        
            
        while self.checkStorageRun:
        
            self.camRunTime.isDiskFull = utils.isDiskFull(self.camRunTime.diskMinUsage) 
            
            storageStatus = {
                'diskUsageFree'  : self.camRunTime.diskUsageFree, 
                'diskUsageFreeGb': self.camRunTime.diskUsageFreeGb,
                'dirVideosOnAlarmesUsedSpace' : self.camRunTime.dirVideosOnAlarmesUsedSpace,
                'dirVideosAllTimeUsedSpace' : self.camRunTime.dirVideosAllTimeUsedSpace, 
                'numDaysRecording' : self.camRunTime.numDaysRecording,
                'isDiskFull' : self.camRunTime.isDiskFull
            }        
            saveStorageInfoDb(self.statusConfig.getUserLogin(), storageStatus) 
            
            if self.camRunTime.nameCam is None:
                self.camRunTime.nameCam = 'nao configurada'                
           
            date = utils.getDate()
            lastCheckInternet = date['year'] + '-' + utils.getMonthDigit(date['month']) + '-' + date['day'] + ' ' + date['hour']
            
            pvStatus = {
            
                'cpuUsage': psutil.cpu_percent(),
                'ramUsage': psutil.virtual_memory().percent,
                'ramFree': psutil.virtual_memory().available * 100 / psutil.virtual_memory().total,
                'dateSessionInit': self.statusConfig.getDateSessionInit(),
                'camConexao' : self.camRunTime.conectado,
                'nomeCam' : self.camRunTime.nameCam,
                'lastCheckInternet' : lastCheckInternet,
                'ip' : self.ipExterno
            }
            
            self.camRunTime.ipExterno = self.ipExterno
            
            savePvStatusDb(self.statusConfig.getUserLogin(), pvStatus)            
            
        
            log.info('\n checkStorage:: checking')
            self.updateStorageInfo.emit()
            
            check = True
            
            if self.camRunTime.statusConfig.isNuvemRunning() and self.camRunTime.statusConfig.getStoragePlan() == 0:
                print('checkStorage:: rodando na nuvem sem plano de storage')
                check = False
            
            if check:              
            
                if not self.camRunTime.isDiskFull: 
                            
                    if self.camRunTime.spaceMaxDirVideosOnAlarme > 0 and self.camRunTime.spaceMaxDirVideosOnAlarme <= self.camRunTime.dirVideosOnAlarmesUsedSpace :
                    
                        #avisar por email 1x a cada X tempo ? 
                        log.info('CheckStorage:: Espaço maximo na pasta VideosOnAlarmes atingido')
                        if not self.camRunTime.emailSentFullVideosOnAlarmes:  
                            
                            data = utils.getDate()
                            data_email_sent = data['hour'] + ' - ' + data['day'] + '/' + data['month'] + '/' + data['year']
                            log.critical('CheckStorage:: Espaço maximo na pasta {} atingido'.format(self.camRunTime.statusConfig.data["dirVideosOnAlarmes"]))
                            threadEmail = Thread(target=sendMail, args=(
                                'Portão Virtual - Aviso Falta de Espaço - Pasta "Alarmes"',
                                'Espaço máximo na pasta " {} " atingido. \n\n \
                                Status do armazenamento - {} \n \
                                Espaço livre em disco em %       : {:3d}% \n \
                                Espaço livre em disco em GB      : {:3.2f} GB \n \
                                Espaço utilizado "Video Alarmes" : {:3.2f} GB \n \
                                Espaço utilizado "Video 24hs"    : {:3.2f} GB \n \
                                Número de dias estimados para gravação: {:3d} \n \
                                '.format(self.camRunTime.statusConfig.data["dirVideosOnAlarmes"],
                                    data_email_sent,
                                    self.camRunTime.diskUsageFree, 
                                    self.camRunTime.diskUsageFreeGb,
                                    self.camRunTime.dirVideosOnAlarmesUsedSpace,
                                    self.camRunTime.dirVideosAllTimeUsedSpace, 
                                    self.camRunTime.numDaysRecording
                                    )) )
                            
                            threadEmail.start()
                            self.camRunTime.emailSentFullVideosOnAlarmes = True
                            #avisar por email 1x a cada X tempo ? 
            
                    if self.camRunTime.spaceMaxDirVideosAllTime > 0 and ( self.camRunTime.spaceMaxDirVideosAllTime <= self.camRunTime.dirVideosAllTimeUsedSpace ):
                    
                        if not self.camRunTime.emailSentFullVideosAllTime:  
                                        log.critical('CheckStorage:: Espaço maximo na pasta {} atingido'.format(self.camRunTime.statusConfig.data["dirVideosAllTime"]))

                                        data = utils.getDate()
                                        data_email_sent = data['hour'] + ' - ' + data['day'] + '/' + data['month'] + '/' + data['year']
                                        threadEmail = Thread(target=sendMail, args=(

                                            'Portao Virtual - Falta de espaço  na pasta "Videos 24hs"',
                                            'Espaço maximo na pasta " {} " atingido. \n\n \
                                            Status do armazenamento - {} \n \
                                            Espaço livre em disco em %       : {:3d}% \n \
                                            Espaço livre em disco em GB      : {:3.2f}GB \n \
                                            Espaço utilizado "Video Alarmes" : {:3.2f}GB \n \
                                            Espaço utilizado "Video 24hs"    : {:3.2f}GB \n \
                                            Número de dias estimados para gravação: {:3d} \n \
                                            '.format(self.camRunTime.statusConfig.data["dirVideosAllTime"], 
                                                data_email_sent,
                                                self.camRunTime.diskUsageFree, 
                                                self.camRunTime.diskUsageFreeGb,
                                                self.camRunTime.dirVideosOnAlarmesUsedSpace,
                                                self.camRunTime.dirVideosAllTimeUsedSpace, 
                                                self.camRunTime.numDaysRecording
                                                )) )

                                        threadEmail.start()
                                        self.camRunTime.emailSentFullVideosAllTime = True
                                        #avisar por email 1x a cada X tempo ? 
            
                # disco cheio
                else:
                    
                    
                    log.info('checkStorage:: Disco cheio')
                    
                    if self.statusConfig.getDirVideosOnAlarmes() == "" or self.camRunTime.statusConfig.getDirVideosAllTime() == "":
                        log.info('checkStorage:: Não existem arquivos a serem apagados na pasta "Videos 24hs" ou "Videos Alarmes"')
                        
                        self.warningHDCheio.emit() 
                    else:
                    

                        if not self.camRunTime.emailSentDiskFull:
                        
                            if self.camRunTime.eraseOldestFiles:
                            
                                textEmail = 'Seu HD está cheio, como você configurou o Portão Virtual a deletar \
                                            os videos mais antigos, recomendamos que aumente seu espaço em disco \
                                            para não perder as gravações realizadas.'
                                            
                                if self.camRunTime.configEmailStatus:  
                                    threadEmailDiskFull = Thread(target=sendMail, args=('Portao Virtual - seu HD está cheio !', textEmail))
                                    threadEmailDiskFull.start()
                                
                                threadAppAlertDiskFull = Thread(target=sendStorageAlert, args=(self.statusConfig.getUserLogin(), 'PV Alert - Seu HD está cheio !',textEmail))
                                threadAppAlertDiskFull.start()
                                
                                self.camRunTime.emailSentDiskFull = True
                                
                                log.info('Email de disco cheio enviado - apagando videos antigos ')
                                #avisar por email 1x a cada X tempo ? 
                            else:
                                
                                textEmail = 'Seu HD está cheio, como você configurou o Portão Virtual a não \
                                            gravar videos novos, recomendamos que aumente seu espaço em disco \
                                            para poder novos videos quando ocorrer futuros alarmes.'

                                if self.camRunTime.configEmailStatus:  
                                    threadEmailDiskFull = Thread(target=sendMail, args=('Portao Virtual - seu HD está cheio !', textEmail))
                                    threadEmailDiskFull.start()
                                
                                threadAppAlertDiskFull = Thread(target=sendStorageAlert, args=(self.statusConfig.getUserLogin(), 'PV Alert - Seu HD está cheio !',textEmail))
                                threadAppAlertDiskFull.start()
                                
                                self.camRunTime.emailSentDiskFull = True
                                log.info('Email de disco cheio enviado - interromper novos videos')


                            # realmente apaga os videos mais antigos ? 
                            if self.camRunTime.eraseOldestFiles:
                                log.info('checkStorage:: eraseOldestFiles true')
                                if self.camRunTime.statusConfig.getDirVideosAllTime() == "":
                                    log.info('checkStorage:: Não existem arquivos a serem apagados na pasta "Videos 24hs"')
                                    
                                else:                          
                                
                                    log.info('checkStorage:: chamando freeDiskSpace')
                                    if utils.freeDiskSpace(self.camRunTime.statusConfig.getDirVideosAllTime()) == False:
                                    
                                        log.critical('checkStorage:: Diretorios de "Videos 24hs" já está vazio')
                                        if not self.camRunTime.emailSentdirVideosAllTimeEmpty:
                                            
                                            textEmail = 'Mesmo apagando a pasta "Videos 24hs", seu HD continua cheio ! \n\n Nossa sugestão é que você libere mais espaço para pode gravar os "Videos 24hs"'                                         
                                            
                                            if self.camRunTime.configEmailStatus:  
                                                threadEmailAllEmpty = Thread(target=sendMail, args=('Portao Virtual - pasta "Videos 24hs" apagada - seu HD está cheio !',textEmail))
                                                threadEmailAllEmpty.start()
                                            
                                            threadAppAlertAllEmpty = Thread(target=sendStorageAlert, args=(self.statusConfig.getUserLogin(), 'PV Alert - pasta "Videos 24hs" apagada - Disco cheio !',textEmail))
                                            threadAppAlertAllEmpty.start()
                                            self.camRunTime.emailSentdirVideosAllTimeEmpty = True
                                        

                            
                                #se ainda não tiver sido suficiente
                                if self.camRunTime.isDiskFull:
                                    log.info('checkStorage:: Apagando diretórios de Alarmes')
                                    #log.info('Dir: {}'.format(statusConfig.getDirVideosOnAlarmes()))
                                    if self.statusConfig.getDirVideosOnAlarmes() == "":
                                        log.info('checkStorage:: Não existem arquivos a serem apagados na pasta "Videos Alarmes"')
                                        
                                    else:
                                        if utils.freeDiskSpace(self.statusConfig.getDirVideosOnAlarmes()) == False:
                                            log.critical('Diretorios de "Vidos Alarme" já está vazio')

                                            if not self.camRunTime.emailSentdirVideosOnAlarmesEmpty:
                                                textEmail = 'Mesmo apagando a pasta "Videos Alarme", seu HD continua cheio ! \n\n  \
                                                         Nossa sugestão é que você libere mais espaço para pode gravar os "Videos Alarme"' 
                                                        
                                                if self.camRunTime.configEmailStatus:
                                                    threadEmailAlarmesEmpty = Thread(target=sendMail, args=('Portao Virtual - pasta "Videos Alarmes" apagada - seu HD está cheio !',textEmail))
                                                    threadEmailAlarmesEmpty.start()
                                                
                                                threadAppAlertEmpty = Thread(target=sendStorageAlert, args=(self.statusConfig.getUserLogin(), 'PV Alert - pasta "Videos Alarmes" apagada - Disco cheio !',textEmail))
                                                threadAppAlertEmpty.start()
                                                self.camRunTime.emailSentdirVideosOnAlarmesEmpty = True
                                        
                            
                        

                        
            log.info('checkStorage:: sleep')
            time.sleep(self.CHECK_STORAGE_TIME)    
        
    def stop(self):
        self.checkStorageRun = False
        self._run_flag = False
        self._running = False
        self.wait()
        log.info('CheckStorage:: stop')