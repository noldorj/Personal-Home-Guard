
import utilsCore as utils
import logging as log

import socket
import sys
import time
import select
import errno
from socket import error as socket_error
import networkscan
from getmac import get_mac_address

from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal 

import os
import subprocess

#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, stream=sys.stdout)
#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", stream=sys.stdout, datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO)
#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', filename='pv.log', encoding='utf-8') 

class CamFinder(QThread):
        
    updateProgress = pyqtSignal(float, 'QVariantList', 'QVariantList', bool)    
    
    rtspError = False
    LIST_PORT = [554, 8554]
    LIST_IP = []
    OS_PLATFORM = 'windows'
    DESCRIBEPACKET = ""
    OPTIONSPACKET = ""
    TIMEOUT = 5
    LIST_CHANNEL = ['profile0', '', 'profile1', 'Streaming/Channels/01', 'h264?channel=1', 'onvif1']
    #'WWYZRL'
    LIST_PASSWORD = ['123456', '1234', '12345', '000000', '00000', 'admin', '9999', 'pass', 'none',
                     'service', '888888', '666666', 'fliradmin', 'system', 'jvc',
                     '1111', 'meinsm', '4321', '1111111', 'ikwd', 'supervisor',
                     'ubnt', 'wbox123', '']
                     
    LIST_USERNAME = ['admin', 'Admin', 'Administrator', 'root', 'service', '888888',
                     '666666', 'supervisor', 'ubnt']

    def __init__(self, rtspError):
        super().__init__()
        self._run_flag = True
        print('CamFinder __init__')
        print('rtspError: {}'.format(rtspError))
        self.rtspError = rtspError
        
        if sys.platform == 'linux':
            self.OS_PLATFORM = 'linux'
    
    def stop(self):
        self._run_flag = False
        self.wait()
    
    
    def is_Unauthorized(self, s):
        return '401 Unauthorized' in s


    def run(self):

        print('CamFinder run')
        #definindo IP Local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP_LOCAL = s.getsockname()[0]
        IP_LOCAL = IP_LOCAL.split('.')
        IP_LOCAL = IP_LOCAL[0] + '.' + IP_LOCAL[1] + '.' + IP_LOCAL[2]
        s.close()
        
        listCamEncontradas = []
        listCamAtivas = []
        dataDescribe = None
        idCam = 0
        
        self.updateProgress.emit(1, listCamEncontradas, listCamAtivas, False)
        
        
       
        #if OS_PLATFORM == 'linux':
        #    cmd = 'arp -a'
        #else:
        #    cmd = 'arp /a'
            
        myNetwork = IP_LOCAL + '.0/24' 
        myScan = networkscan.Networkscan(myNetwork)
        self.updateProgress.emit(3, listCamEncontradas, listCamAtivas, False)
        myScan.run()
        self.updateProgress.emit(6, listCamEncontradas, listCamAtivas, False)
        
        for ip in myScan.list_of_hosts_found:
            mac = get_mac_address(ip=ip)
            self.LIST_IP.append({'id':'0','nome':'nomeCam', 'ip':ip, 'mac':mac, 'port':'0', 'user':'user', 
                'passwd':'passwd', 'channel':'channel', 'source':'0', 'emUso':'False'})

        
        
        #for ipLocal in os.popen(cmd):     
        #    ipLocal = ipLocal.split(' ')
        #    if '[ether]' in ipLocal:
        #        ipLocal[1] = ipLocal[1].replace(')', '')
        #        LIST_IP.append({'ip':ipLocal[1].replace('(', ''),'mac':ipLocal[3] })

        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
        progressTotal = len(self.LIST_IP) * len(self.LIST_PORT)
        progressI = 1 
        print('progressTotal: {:d}'.format(progressTotal))
        print('LIST_IP:   {:d}'.format(len(self.LIST_IP)))
        print('LIST_PORT: {:d}'.format(len(self.LIST_PORT)))
        print('-------------- \n\n')
        
        for ip in self.LIST_IP: 
            
            if ip not in listCamAtivas:
                
                pktDescribe = self.describe(ip.get('ip'))
                
                for port in self.LIST_PORT:

                    if ip not in listCamAtivas:
               
                        log.debug('-------')
                        log.debug("IP: {}:{}".format(ip.get('ip'), str(port)))
                        
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                            s.settimeout(self.TIMEOUT)
                            s.connect((ip.get('ip'), port))
        
                        except socket.timeout:
                            log.debug("Timeout IP: {}:{}".format(ip.get('ip'), str(port)))
        
                        except socket.error as e:
                            if e.errno == errno.ECONNREFUSED:
                                log.debug('Conenction Refused IP: {}:{}'.format(ip.get('ip'), str(port)))
                                
                        else:
                                        
                            s.sendall(pktDescribe)            
                            dataDescribe = s.recv(1024)                    
                            
                            if dataDescribe is not None:
                                resp = dataDescribe.decode()
                                if (ip not in listCamAtivas):
                                    for passwd in self.LIST_PASSWORD:
                                        if (ip not in listCamAtivas):
                                            for user in self.LIST_USERNAME:
                                                if (ip not in listCamAtivas):
                                                    for channel in self.LIST_CHANNEL:                                                   
                                                        
                                                        if ip not in listCamAtivas:
                                                            
                                                            source = 'rtsp://' + user + ':' + passwd + '@' + ip.get('ip') + ':' + str(port) + '/' + channel 
                                                            ipCam, error = utils.camSource(source)                   
                                                            
                                                            if error != '':                                                                    
                                                                log.info('Erro camSource: {}'.format(error))

                                                                if ip not in listCamEncontradas and ip not in listCamAtivas: 

                                                                    ip['id'] = str(idCam)
                                                                    ip['nome'] = 'Cam_' + str(idCam)
                                                                    ip['port'] = str(port)                                                                    
                                                                    ip['user'] = user
                                                                    ip['passwd'] = passwd
                                                                    ip['channel'] = channel
                                                                    ip['source'] = source 
                                                                    listCamEncontradas.append(ip)
                                                                    idCam = idCam + 1

                                                            else:                                    
                                                                log.info('Cam ativa encontrada')
                                                                log.info('source: {}'.format(source))
                                                                log.info('Data: \n {}'.format(dataDescribe.decode()))
                                                                log.info(' ')

                                                                ip['id'] = str(idCam)
                                                                ip['nome'] = 'Cam_' + str(idCam)
                                                                ip['port'] = str(port)
                                                                ip['user'] = user
                                                                ip['passwd'] = passwd
                                                                ip['channel'] = channel
                                                                ip['source'] = source 
                                                                listCamAtivas.append(ip)                                    
                                                                idCam = idCam + 1
                                                    
                        self.updateProgress.emit((progressI/progressTotal)*100, listCamEncontradas, listCamAtivas, False)
                        progressI = progressI + 1
                        print('progressI: {:d}'.format(progressI))                            
                                            
                                    
                    s.close()
            # end for in LIST_PORT                            
                    
                    #print('progressI: {:f}'.format((progressI/ (len(self.LIST_PORT)*len(self.LIST_IP)) )*100))
                    
                
                #self.updateProgress.emit((progressI / progressTotal)*100, listCamEncontradas, listCamAtivas, False)
                #progressI = progressI + 1
                #print('progressI: {:d}'.format(progressI))
            #print('progressI: {:.2f}'.format((progressI/ (len(self.LIST_PORT)*len(self.LIST_IP)) )*100))
            
        if self.rtspError:
            print('self.rtspError rtsp_discovery')
            self.updateProgress.emit(100, listCamEncontradas, listCamAtivas, True)    
        else:
            self.updateProgress.emit(100, listCamEncontradas, listCamAtivas, False)    
        
        s.close()
        
        
        #return listCamEncontradas, listCamAtivas 

    def create_describe_packet(self, ip):
        #global DESCRIBEPACKET
        if len(self.DESCRIBEPACKET) <= 0:
            self.DESCRIBEPACKET = 'DESCRIBE rtsp://%s RTSP/1.0\r\n' % ip
            self.DESCRIBEPACKET += 'CSeq: 2\r\n'
        return self.DESCRIBEPACKET

    def create_options_packet(self):
        #global OPTIONSPACKET
        if len(self.OPTIONSPACKET) <= 0:
            self.OPTIONSPACKET = 'OPTIONS * RTSP/1.0\r\n'
            self.OPTIONSPACKET += 'CSeq: 1\r\n'
        return self.OPTIONSPACKET

    def describe(self, ip):
        return (self.create_describe_packet(ip) + "\r\n").encode()

    def options(self):
        return (self.create_options_packet() + "\r\n").encode()
        
        
    def getListCam(self):

            print('getListCam')
            #definindo IP Local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            IP_LOCAL = s.getsockname()[0]
            IP_LOCAL = IP_LOCAL.split('.')
            IP_LOCAL = IP_LOCAL[0] + '.' + IP_LOCAL[1] + '.' + IP_LOCAL[2]
            s.close()
            
            listCamEncontradas = []
            listCamAtivas = []
            dataDescribe = None
            idCam = 0
            
            self.updateProgress.emit(1, listCamEncontradas, listCamAtivas)
            
            
           
            #if OS_PLATFORM == 'linux':
            #    cmd = 'arp -a'
            #else:
            #    cmd = 'arp /a'
                
            myNetwork = IP_LOCAL + '.0/24' 
            myScan = networkscan.Networkscan(myNetwork)
            #self.updateProgress.emit(3, listCamEncontradas, listCamAtivas)
            myScan.run()
            #self.updateProgress.emit(6, listCamEncontradas, listCamAtivas)
            
            for ip in myScan.list_of_hosts_found:
                mac = get_mac_address(ip=ip)
                self.LIST_IP.append({'id':'0','nome':'nomeCam', 'ip':ip, 'mac':mac, 'port':'0', 'user':'user', 
                    'passwd':'passwd', 'channel':'channel', 'source':'0', 'emUso':'False'})

            
            
            #for ipLocal in os.popen(cmd):     
            #    ipLocal = ipLocal.split(' ')
            #    if '[ether]' in ipLocal:
            #        ipLocal[1] = ipLocal[1].replace(')', '')
            #        LIST_IP.append({'ip':ipLocal[1].replace('(', ''),'mac':ipLocal[3] })

            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
            progressTotal = len(self.LIST_IP) * len(self.LIST_PORT) * len(self.LIST_PASSWORD) * len(self.LIST_USERNAME) * len(self.LIST_CHANNEL)
            progressI = 1 
            
            
            for ip in self.LIST_IP: 
                
                if ip not in listCamAtivas:
                    
                    pktDescribe = self.describe(ip.get('ip'))
                    
                    for port in self.LIST_PORT:

                        if ip not in listCamAtivas:
                   
                            log.debug('-------')
                            log.debug("IP: {}:{}".format(ip.get('ip'), str(port)))
                            
                            try:
                                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                                s.settimeout(self.TIMEOUT)
                                s.connect((ip.get('ip'), port))
            
                            except socket.timeout:
                                log.debug("Timeout IP: {}:{}".format(ip.get('ip'), str(port)))
            
                            except socket.error as e:
                                if e.errno == errno.ECONNREFUSED:
                                    log.debug('Conenction Refused IP: {}:{}'.format(ip.get('ip'), str(port)))
                                    
                            else:
                                            
                                s.sendall(pktDescribe)            
                                dataDescribe = s.recv(1024)                    
                                
                                if dataDescribe is not None:
                                    resp = dataDescribe.decode()
                                    if (ip not in listCamAtivas):
                                        for passwd in self.LIST_PASSWORD:
                                            if (ip not in listCamAtivas):
                                                for user in self.LIST_USERNAME:
                                                    if (ip not in listCamAtivas):
                                                        for channel in self.LIST_CHANNEL:                                                   
                                                            
                                                            if ip not in listCamAtivas:
                                                                
                                                                source = 'rtsp://' + user + ':' + passwd + '@' + ip.get('ip') + ':' + str(port) + '/' + channel 
                                                                ipCam, error = utils.camSource(source)                   
                                                                
                                                                if error != '':                                                                    
                                                                    log.info('Erro camSource: {}'.format(error))

                                                                    if ip not in listCamEncontradas and ip not in listCamAtivas: 

                                                                        ip['id'] = str(idCam)
                                                                        ip['nome'] = 'Cam_' + str(idCam)
                                                                        ip['port'] = str(port)                                                                    
                                                                        ip['user'] = user
                                                                        ip['passwd'] = passwd
                                                                        ip['channel'] = channel
                                                                        ip['source'] = source 
                                                                        listCamEncontradas.append(ip)
                                                                        idCam = idCam + 1

                                                                else:                                    
                                                                    log.info('Cam ativa encontrada')
                                                                    log.info('source: {}'.format(source))
                                                                    log.info('Data: \n {}'.format(dataDescribe.decode()))
                                                                    log.info(' ')

                                                                    ip['id'] = str(idCam)
                                                                    ip['nome'] = 'Cam_' + str(idCam)
                                                                    ip['port'] = str(port)
                                                                    ip['user'] = user
                                                                    ip['passwd'] = passwd
                                                                    ip['channel'] = channel
                                                                    ip['source'] = source 
                                                                    listCamAtivas.append(ip)                                    
                                                                    idCam = idCam + 1
                                                        
                                                        
                                                
                                        
                        s.close()
                # end for in LIST_PORT                            
                        #self.updateProgress.emit((progressI/(len(self.LIST_PORT)*len(self.LIST_IP)) )*100, listCamEncontradas, listCamAtivas)
                        progressI = progressI + 1
                        #print('progressI: {:d}'.format(progressI))
                        #print('progressI: {:f}'.format((progressI/ (len(self.LIST_PORT)*len(self.LIST_IP)) )*100))
                        
                #self.updateProgress.emit((progressI/ (len(self.LIST_PORT)*len(self.LIST_IP)) )*100, listCamEncontradas, listCamAtivas)
                progressI = progressI + 1
                #print('progressI: {:d}'.format(progressI))
                #print('progressI: {:.2f}'.format((progressI/ (len(self.LIST_PORT)*len(self.LIST_IP)) )*100))
                
            #self.updateProgress.emit(100, listCamEncontradas, listCamAtivas)    
            s.close()
            
            
            return listCamEncontradas, listCamAtivas         