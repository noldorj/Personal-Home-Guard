#from initFormConfig import FormProc
#import logging as log
import logging
from objectTracking.pyimagesearch.centroidtracker import CentroidTracker
import utilsCore as utils
from rtsp_discover.rtsp_discover import CamFinder
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt


import numpy as np
import cv2 as cv
import sys
import time
import secrets

from collections import deque

'''
log.root.setLevel(log.DEBUG)
log.basicConfig()

for handler in log.root.handlers[:]:
    log.root.removeHandler(handler)

log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, handlers=[log.FileHandler('config/pv.log', 'w', 'utf-8')])
log.getLogger('socketio').setLevel(log.ERROR)
log.getLogger('engineio').setLevel(log.ERROR)
'''

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


class CamRunTime():

    #camFinder = CamFinder(False)

    camRunTimeId = 0 
    configEmailStatus = False
    desativarAlarmes = False
    changeIpCam = False
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
    camEmpty = False
    fernetKey = None

    CHECK_SESSION = 300 # checar sessao a cada 5 min
    #CHECK_SESSION = 60 # checar sessao a cada 5 min    
    GRAVANDO_TIME = 300 #gravar videos de 5min 
    #GRAVANDO_TIME = 10 

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
    timeAlertaStart = 0 
    timeAlertaEnd = 0
    timeAlertaDelta = 0
    timeAlerta = 0 
    
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

    #init_video = False 
    init_video = True
    pausaConfig = False

    statusPasswd = False
    statusLicence = True

    statusConfig = None
    pb = None
    cvNetTensorFlow = None
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
    nameCam = 'Camera'
    error = ' '
    errorWebcam = False
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
    sessionErrorCount = 2 #numero maximo de erros na sessao
    errorSession = 0    
    token = ''
    #token = secrets.token_urlsafe(20)

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
    errorRtsp = False
    ipExterno = ''
    
    
    
    
            
    def setRtspError(self, status):
        log.info('camRunTime::setRtspError')
        self.errorRtsp = status

    def updateIpCam(self):
        log.info('camRunTime::updateIpCam')
        #origem do stream do video
        self.statusConfig = utils.StatusConfig()
        self.source = self.statusConfig.data["camSource"]
        
        
        self.ipCam, self.error = utils.camSource(self.source)
        log.info('camRunTime::updateIpCam camSource error: {}'.format(self.error))
        
        if self.error == 'rtsp':           
            
            self.errorRtsp = True
            self.rtspStatus = False 
            self.errorWebcam = False
            
        elif self.error == 'webcam':
            
            self.errorWebcam = True
            self.errorRtsp = True
            self.rtspStatus = False                         
        else:
            self.rtspStatus = True 
            self.errorWebcam = False
            self.errorRtsp = False
            self.ipCam.set(3, self.RES_X)            
            self.ipCam.set(4, self.RES_Y)
            #self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.RES_X)
            #self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.RES_Y)
            log.info('camRunTime::updateIpCam: Conexao com camera restabelecida.')            
            
            self.conectado = True            
            self.init_video = True
            self.frame = None
            self.next_frame = None
            self.changeIpCam = True
  

    def init(self):

        
        log.info(' ')
        log.info('camRunTime::initConfig')       
        log.info(' ')       
        
        self.camRunTimeId = secrets.token_urlsafe(5)
      

        if sys.platform == 'linux':
                self.OS_PLATFORM = 'linux'
      
        
        
        self.current_data_dir = utils.getDate()
        self.current_data_dir = [self.current_data_dir.get('day'), self.current_data_dir.get('month')]
        self.hora = utils.getDate()['hour'].replace(':','-')
        
        self.statusConfig = utils.StatusConfig()

        self.LOGIN_AUTOMATICO = True if self.statusConfig.getLoginAutomatico() == 'True' else False
        
        
        email = self.statusConfig.dataLogin['user']        
        
        if self.statusConfig.dataLogin['passwd'] == '':
            passwd = self.statusConfig.dataLogin['passwd']
        else:
            passwd = utils.decrypt(self.statusConfig.dataLogin['passwd'])
            
        self.login = {'user':utils.encrypt(email), 'passwd':utils.encrypt(passwd), 'token':utils.encrypt(self.token)}
        
        #log.info('camRunTime::init TOKEN: {}'.format(utils.decrypt(self.login.get('token').decode())))
       
        if self.statusConfig.isNuvemRunning() == "True":

            if self.statusConfig.getStoragePlan() > 0:            
            
                if self.statusConfig.data["isRecordingOnAlarmes"] == 'True':
                    self.gravandoOnAlarmes = True
                
                if self.statusConfig.data["isRecordingAllTime"] == 'True':                
                    self.gravandoAllTime = True
            else:
                self.gravandoAllTime = False
                self.gravandoOnAlarmes = False
                log.info('camRunTime::init: Rodando na Nuvem sem plano de storage')
                log.info('camRunTime::init: Desabilitando gravacao de videos')
        
        else:
            if self.statusConfig.data["isRecordingOnAlarmes"] == 'True':
                self.gravandoOnAlarmes = True
            else:
                self.gravandoOnAlarmes = False
                
            if self.statusConfig.data["isRecordingAllTime"] == 'True':                
                self.gravandoAllTime = True
            else:
                self.gravandoAllTime = False        
        
        
        
        self.diskMinUsage = int(float(self.statusConfig.data["storageConfig"]["diskMinUsage"]))
        
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
        #self.device, self.openVinoModelXml, self.openVinoModelBin, self.openVinoCpuExtension, self.openVinoPluginDir, self.openVinoModelName  = self.statusConfig.getActiveDevice()
        
        cam = self.statusConfig.getCamEmUsoConfig()        
        if cam is not None:
            self.nameCam = cam.get('nome')
        
        #print('camRunTime:: self.nameCam: {}'.format(self.nameCam))
        
        # dnnMOdel for TensorFlow Object Detection API
        self.pb = self.statusConfig.data["dnnModelPb"] 
        self.pbtxt = self.statusConfig.data["dnnModelPbTxt"] 
        
        #Carregando regioes salvas
        self.regions = self.statusConfig.getRegions()
        self.emailConfig = self.statusConfig.getEmailConfig()
        
        self.desativarAlarmes = self.statusConfig.getDesativarAlarmes()
        
        if self.emailConfig['name'] != '' and \
                self.emailConfig['port'] != '' and \
                self.emailConfig['smtp'] != '' and \
                self.emailConfig['user'] != '' and \
                self.emailConfig['password'] != '' and \
                self.emailConfig['subject'] != '' and \
                self.emailConfig['to'] != '':
            
            self.configEmailStatus = True
            log.info('camRunTime::init configEmailStatus:'.format(self.configEmailStatus))
            
        else:            
            self.configEmailStatus = False
            log.info('camRunTime::init configEmailStatus:'.format(self.configEmailStatus))
        
        
        
        #se existirem regioes ja selecionadas, o portao virtual é mostrado
        #if len(regions) > 0:
        #    portaoVirtualSelecionado = True
        self.portaoVirtualSelecionado = True
        
        #Criando diretorio para salvar videos de alarmes
        self.status_dir_criado_on_alarmes, self.dir_video_trigger_on_alarmes = utils.createDirectory(self.statusConfig.data["dirVideosOnAlarmes"])

        self.status_dir_criado_all_time, self.dir_video_trigger_all_time = utils.createDirectory(self.statusConfig.data["dirVideosAllTime"])
        
        
        #origem do stream do video
        self.source = self.statusConfig.data["camSource"]
        
        if self.source == '':
            self.error = 'camEmpty'
            self.camEmpty = True
            self.errorRtsp = False
            self.rtspStatus = False
            self.errorWebcam = False
        else:            
            self.ipCam, self.error = utils.camSource(self.source)
            self.camEmpty = False
            
        log.info('camRunTime::init:: camSource error: {}'.format(self.error))
        
        if self.error == 'rtsp':
            self.errorRtsp = True
            self.rtspStatus = False
            self.errorWebcam = False
            
        elif self.error == 'webcam':
            self.errorWebcam = True
            self.errorRtsp = True
            self.rtspStatus = False
            
        else:
            self.rtspStatus = True
            self.errorWebcam = False
            self.errorRtsp = False
            if self.ipCam is not None:
                self.ipCam.set(3, self.RES_X)
                self.ipCam.set(4, self.RES_Y)
            log.info('camRunTime::init:: Conexao com camera restabelecida.')     

        #self.fourcc = cv.VideoWriter_fourcc(*'X''2''6''4') erro
        #for linux x264 need to recompile opencv mannually
        #self.fourcc = cv.VideoWriter_fourcc(*'DIVX') #menor tamanho de arquivo
        
        
        
        #self.fourcc = cv.VideoWriter_fourcc(*'M','J','P','G')
        self.fourcc = cv.VideoWriter_fourcc(*'XVID') 
        #self.fourcc = cv.VideoWriter_fourcc(*'MP4V') #nao funciona windows        
        
        
        self.dirVideosOnAlarmesUsedSpace = utils.getDirUsedSpace(self.statusConfig.data["dirVideosOnAlarmes"])
        self.isDiskFull = utils.isDiskFull(self.diskMinUsage) 
        self.diskUsageFree = utils.getDiskUsageFree() 
        self.diskUsageFreeGb = utils.getDiskUsageFreeGb()
        self.dirVideosAllTimeUsedSpace = utils.getDirUsedSpace(self.statusConfig.data['dirVideosOnAlarmes'])
        self.numDaysRecording = utils.getNumDaysRecording()            

        self.prob_threshold = float(self.statusConfig.data["prob_threshold"])
