#from initFormConfig import FormProc
import logging as log
from objectTracking.pyimagesearch.centroidtracker import CentroidTracker
import utilsCore as utils
from rtsp_discover.rtsp_discover import CamFinder


import numpy as np
import cv2 as cv
import sys
import time
import secrets

from collections import deque


class CamRunTime():

    camFinder = CamFinder()

    OS_PLATFORM = 'windows'
    #variaveis globais
    diskFullWarned = False
    diskFullVideosOnAlarmes = False
    diskFullVideosAllTimeWarned = False

    emailSentFullVideosOnAlarmes = False
    emailSentFullVideosAllTime = False
    emailSentDiskFull = False
    emailSentdirVideosAllTimeEmpty = False
    emailSentdirVideosOnAlarmesEmpty = False    
    
    timeInternetOffStart = None
    pilhaAlertasNaoEnviados = deque() 
    listCamEncontradas = []
    listCamAtivas = []
    fourcc = None
    conectado = None
    conexao = False
    frame = None
    rtspStatus = True
    fernetKey = None

    #CHECK_SESSION = 300 # checar sessao a cada 5 min
    CHECK_SESSION = 20 # checar sessao a cada 5 min
    #GRAVANDO_TIME = 300 #gravar videos de 5min 
    GRAVANDO_TIME = 300 #gravar videos de 5min 

    LOGIN_AUTOMATICO = False

    #INTERNET_OFF = 60 #3 horas apos queda de internet para o programa perder as funcoes
    INTERNET_OFF = 7200 #3 horas apos queda de internet para o programa perder as funcoes
    STOP_ALL = False

    #720p: 1280 x 720
    #480p: 854 x 480
    RES_X = 854 
    RES_Y = 480 

    posConfigPv = 255

    gravandoAllTime = False
    gravandoOnAlarmes = False
    

    #tempo sem objetos detectados
    tEmptyStart = time.time()

    counter = 0
    tEmpty = 0
    tEmptyEnd = 0
    tEmptyStart = 0

    timeGravandoAll = 0
    timeGravandoAllInit = 0
    end = 0
    start = 0

    stopSound = False
    initOpenVinoStatus = True

    nameVideo  = 'firstVideo'
    nameVideoAllTime  = 'firstVideo'
    newVideo = True
    releaseVideoOnAlarmes = False 
    releaseVideoAllTime = False 
    h = RES_Y
    w = RES_X
    #objects = None
    #FPS = ipCam.get(cv.CAP_PROP_FPS) #30.0 #frames per second
    FPS = 4  #de acordo com o manual da mibo ic5 intelbras

    #primeiro objeto é enviado
    listObjectMailAlerted = []
    listObjectSoundAlerted = []
    listObjectVideoRecorded = []
    out_video = None
    out_video_all_time = None

    init_video = False 
    pausaConfig = False

    statusPasswd = False
    statusLicence = False

    statusConfig = None
    pb = None
    pbtxt = None
    regions = None
    emailConfig = None
    portaoVirtualSelecionado = False 
    status_dir_criado_on_alarmes = None
    status_dir_criado_all_time = None
    dir_video_trigger_on_alarmes = None
    dir_video_trigger_all_time = None
    source = None
    ipCam = None
    error = ''
    prob_threshold = 60.0 
    #list de objetos identificados pela CNN
    listObjects = []
    #lista de objetos detectados da rede neural
    detection =[]
    #lista de boxes detectados
    listRectanglesDetected = []
    #lista de objetos traqueados
    listObjectsTracking = []
    #linhas e colunas do video (resolucao)
    rows = None
    cols = None
    next_frame = None
    nchw = []
    exec_net = None
    out_blob = None
    input_blob = None
    cur_request_id, next_request_id, render_time = 0, 0, 0
    prob_threshold_returned = 0
    #colors = np.random.uniform(0, 255, size=(len(classes), 3))
    tSound, tSoundEnd, tSoundLimit, tSoundStart = 0, 0, 0, 0
    # initialize our centroid tracker and frame dimensions
    ct = CentroidTracker()
    (H, W) = (None, None)
    listObjectDetected = list()
    idObjeto = 0
    drawing = False     # true if mouse is pressed
    mode = True         # if True, draw rectangle.
    ix, iy = -1, -1
    #ref_point = []
    ref_point_polygon = list()
    #crop = False
    cropPolygon = False
    #showGate = False
    #regiaoPortao = None
    hora = None
    current_data_dir = None
    isOpenVino = True
    device = 'CPU'
    openVinoModelXml = None 
    openVinoModelBin = None
    openVinoCpuExtension = None 
    openVinoPluginDir = None 
    openVinoModelName = None

    login = None 
    sessionStatus = True
    token = None

    #variaveis do disco
    diskMinUsage = 15
    diskMaxUsage = 85
    spaceMaxDirVideosOnAlarme = 0 #zero significa sem limites de utilizacao do disco 
    spaceMaxDirVideosAllTime = 0  #zero significa sem limites de utilizacao do disco 
    eraseOldestFiles = True 
    stopSaveNewVideos = False
    
    dirVideosOnAlarmesUsedSpace = None
    dirVideosAllTimeUsedSpace = None
    isDiskFull = None
    diskUsageFree = None
    diskUsageFreeGb = None    
    numDaysRecording = None

    def init(self):

        log.debug(' ')
        log.debug('initConfig')
        log.debug(' ')
        print('camRunTime init')

        if sys.platform == 'linux':
                self.OS_PLATFORM = 'linux'

        #global statusConfig, pb, pbtxt, regions, emailConfig, portaoVirtualSelecionado
        #global status_dir_criado_all_time, status_dir_criado_all_time, dir_video_trigger_on_alarmes, dir_video_trigger_all_time, source, ipCam, prob_threshold, hora, current_data_dir, isOpenVino
        #global device, openVinoModelXml, openVinoModelBin, openVinoCpuExtension, openVinoPluginDir, openVinoModelName, gravandoAllTime 
        #global spaceMaxDirVideosAllTime, spaceMaxDirVideosOnAlarme, eraseOldestFiles, stopSaveNewVideos, diskMaxUsage, diskMinUsage, rtspStatus, LOGIN_AUTOMATICO
        #global listCamAtivas, listCamEncontradas
        
        self.current_data_dir = utils.getDate()
        self.current_data_dir = [self.current_data_dir.get('day'), self.current_data_dir.get('month')]
        self.hora = utils.getDate()['hour'].replace(':','-')
        
        self.statusConfig = utils.StatusConfig()

        self.LOGIN_AUTOMATICO = True if self.statusConfig.getLoginAutomatico() == 'True' else False
        
        self.token = secrets.token_urlsafe(20)
        email = self.statusConfig.dataLogin['user']
        passwd = utils.decrypt(self.statusConfig.dataLogin['passwd'])        
        self.login = {'user':utils.encrypt(email), 'passwd':utils.encrypt(passwd), 'token':utils.encrypt(self.token)}
        
        
        self.gravandoAllTime = True if self.statusConfig.data["isRecordingAllTime"] == 'True' else False
        self.gravandoOnAlarmes = True if self.statusConfig.data["isRecordingOnAlarmes"] == 'True' else False
        self.diskMinUsage = int(self.statusConfig.data["storageConfig"]["diskMinUsage"])
        
        self.isOpenVino = self.statusConfig.data["isOpenVino"] == 'True'

        self.listCamAtivas = self.statusConfig.getListCamAtivas()

        self.listCamEncontradas = self.statusConfig.getListCamEncontradas()

        self.spaceMaxDirVideosOnAlarme = float(self.statusConfig.data["storageConfig"]["spaceMaxDirVideosOnAlarme"])  
        self.spaceMaxDirVideosAllTime = float(self.statusConfig.data["storageConfig"]["spaceMaxDirVideosAllTime"])  
        self.eraseOldestFiles = True if self.statusConfig.data["storageConfig"]["eraseOldestFiles"] == 'True' else False 
        self.stopSaveNewVideos = True if self.statusConfig.data["storageConfig"]["stopSaveNewVideos"] == 'True' else False 
        
        #if isOpenVino:
        #    import pluginOpenVino as pOpenVino

        #device = statusConfig.data["openVinoDevice"]
        self.device, self.openVinoModelXml, self.openVinoModelBin, self.openVinoCpuExtension, self.openVinoPluginDir, self.openVinoModelName  = self.statusConfig.getActiveDevice()

        
        # dnnMOdel for TensorFlow Object Detection API
        self.pb = self.statusConfig.data["dnnModelPb"] 
        self.pbtxt = self.statusConfig.data["dnnModelPbTxt"] 
        
        #Carregando regioes salvas
        self.regions = self.statusConfig.getRegions()
        self.emailConfig = self.statusConfig.getEmailConfig()
        
        #se existirem regioes ja selecionadas, o portao virtual é mostrado
        #if len(regions) > 0:
        #    portaoVirtualSelecionado = True
        self.portaoVirtualSelecionado = True
        
        #Criando diretorio para salvar videos de alarmes
        self.status_dir_criado_on_alarmes, self.dir_video_trigger_on_alarmes = utils.createDirectory(self.statusConfig.data["dirVideosOnAlarmes"])

        self.status_dir_criado_all_time, self.dir_video_trigger_all_time = utils.createDirectory(self.statusConfig.data["dirVideosAllTime"])
        
        
        #origem do stream do video
        self.source = self.statusConfig.data["camSource"]
        log.debug('source: {}'.format(self.source))
        self.ipCam, self.error = utils.camSource(self.source)

        #fourcc = cv.VideoWriter_fourcc(*'X264')
        #for linux x264 need to recompile opencv mannually
        self.fourcc = cv.VideoWriter_fourcc(*'X''V''I''D') #menor tamanho de arquivo
        #fourcc = cv.VideoWriter_fourcc('M','J','P','G')
        #fourcc = cv.VideoWriter_fourcc(*'MP4V')
        
        self.dirVideosOnAlarmesUsedSpace = utils.getDirUsedSpace(self.statusConfig.data["dirVideosOnAlarmes"])
        self.isDiskFull = utils.isDiskFull(self.diskMinUsage) 
        self.diskUsageFree = utils.getDiskUsageFree() 
        self.diskUsageFreeGb = utils.getDiskUsageFreeGb()
        self.dirVideosAllTimeUsedSpace = utils.getDirUsedSpace(self.statusConfig.data['dirVideosOnAlarmes'])
        self.numDaysRecording = utils.getNumDaysRecording()                     

        if self.error != '':
            self.ipCam = None
            self.rtspStatus = False
            log.critical('Erro camSource: {}'.format(self.error))
            print('Erro camSource: {}'.format(self.error))
            #self.uiConfig.lblStatus.setText('Erro de conexao da camera. Tente configurar o endereço RTSP, e clique em "Salvar"')
            #self.uiConfig.lblStatusProcurarCam.setText('Erro de conexao da camera. Tente configurar uma nova câmera ou fazer uma nova varredura por câmeras clicando em "Procurar Câmeras". ')
            
            #checar se houve mudança de IP
            camEmUso = self.statusConfig.getCamEmUsoConfig()

            self.camListEncontradas, self.camListAtivas = self.camFinder.start()
            

            #checar se o mac address camEmUso vs nova cam ativa
            for cam in self.camListAtivas:
                if cam.get('mac') == camEmUso.get('mac'):
                    if cam.get('ip') != camEmUso.get('ip'):
                        
                        print('Camera em uso mudou de IP')
                        log.debug('Camera em uso mudou de IP')
                        log.debug('Camera em uso IP: {}'.format(camEmUso.get('ip')))
                        log.debug('Novo IP: {}'.format(cam.get('ip')))
                        
                        self.ipCam, self.error = utils.camSource(cam.get('source'))

                        if self.error != '':
                            self.ipCam = None
                            self.rtspStatus = False
                            log.critical('Erro camSource: {}'.format(error))
                            #ui.lblStatus.setText('Falha em localizar novo IP automaticamente. Tente configurar o endereço RTSP, e clique em "Salvar"')
                            #ui.lblStatusProcurarCam.setText('Falha em localizar o novo IP automaticamente. Tente configurar uma nova câmera ou fazer uma nova varredura por câmeras clicando em "Procurar Câmeras". ')
                        else:

                            self.statusConfig.setRtspConfig(cam.get('source'))
                            self.statusConfig.addListCamAtivasConfig(listCamAtivas)
                            self.statusConfig.addListCamEncontradasConfig(listCamEncontradas)
                            #ui.txtUrlRstp.setText(cam.get('source'))

                            self.rtspStatus = True 
                            self.ipCam.set(3, RES_X)
                            self.ipCam.set(4, RES_Y)
                            log.debug('Conexao com camera restabelecida.')
                            #ui.lblStatus.setText('Conexão com a camera estabelecida! Feche a janela para inciar o Portão Virtual')
                            #ui.lblStatusProcurarCam.setText('Conexão com a câmera estabelecida! Feche a janela para inciar o Portão Virtual')
                            break



            #checar se o mac address camEmUso vs nova cam encontrada 
            for cam in self.camListEncontradas:
                if cam.get('mac') == camEmUso.get('mac'):
                    if cam.get('ip') != camEmUso.get('ip'):
                        print('Camera em uso mudou de IP')
                        print('Camera em uso IP: {}'.format(camEmUso.get('ip')))
                        print('Novo IP: {}'.format(cam.get('ip')))
                        log.debug('Camera em uso mudou de IP')
                        log.debug('Camera em uso IP: {}'.format(camEmUso.get('ip')))
                        log.debug('Novo IP: {}'.format(cam.get('ip')))
                        
                        #ipCam, error = utils.camSource(source)

                        #ui.lblStatus.setText('Câmera previamente configurada trocou de IP, localizamos o novo IP com sucesso. Porém a senha, porta ou canal precisam ser novamente configurados !')
                        #ui.lblStatusProcurarCam.setText('Câmera previamente configurada trocou de IP, localizamos o novo IP com sucesso. Porém a senha, porta ou canal precisam ser novamente configurados !')
                        break 

        else:
            self.rtspStatus = True 
            self.ipCam.set(3, self.RES_X)
            self.ipCam.set(4, self.RES_Y)
            log.debug('Conexao com camera restabelecida.')
            #ui.lblStatus.setText('Conexão com a camera estabelecida! Feche a janela para inciar o Portão Virtual')
            #ui.lblStatusProcurarCam.setText('Conexão com a câmera estabelecida! Feche a janela para inciar o Portão Virtual')

        self.prob_threshold = float(self.statusConfig.data["prob_threshold"])
