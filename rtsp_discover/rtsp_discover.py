
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

import os
import subprocess

#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, stream=sys.stdout)
log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", stream=sys.stdout, datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO)
#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', filename='pv.log', encoding='utf-8') 

LIST_PORT = [554, 8554]
LIST_IP = []

OS_PLATFORM = 'windows'

if sys.platform == 'linux':
    OS_PLATFORM = 'linux'


DESCRIBEPACKET = ""
OPTIONSPACKET = ""
TIMEOUT = 10

LIST_CHANNEL = ['profile0', '', 'profile1', 'Streaming/Channels/01', 'h264?channel=1', 'onvif1']
#'WWYZRL'
LIST_PASSWORD = ['123456', '1234', '12345', 'admin', '9999', 'pass', 'none',
                 'service', '888888', '666666', 'fliradmin', 'system', 'jvc',
                 '1111', 'meinsm', '4321', '1111111', 'ikwd', 'supervisor',
                 'ubnt', 'wbox123', '']
                 
LIST_USERNAME = ['admin', 'Admin', 'Administrator', 'root', 'service', '888888',
                 '666666', 'supervisor', 'ubnt']

def is_Unauthorized(s):
    return '401 Unauthorized' in s

def create_describe_packet(ip):
    global DESCRIBEPACKET
    if len(DESCRIBEPACKET) <= 0:
        DESCRIBEPACKET = 'DESCRIBE rtsp://%s RTSP/1.0\r\n' % ip
        DESCRIBEPACKET += 'CSeq: 2\r\n'
    return DESCRIBEPACKET

def create_options_packet():
    global OPTIONSPACKET
    if len(OPTIONSPACKET) <= 0:
        OPTIONSPACKET = 'OPTIONS * RTSP/1.0\r\n'
        OPTIONSPACKET += 'CSeq: 1\r\n'
    return OPTIONSPACKET

def describe(ip):
    return (create_describe_packet(ip) + "\r\n").encode()

def options():
    return (create_options_packet() + "\r\n").encode()

def getListCam():
  
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
    
   
    #if OS_PLATFORM == 'linux':
    #    cmd = 'arp -a'
    #else:
    #    cmd = 'arp /a'
        
    myNetwork = IP_LOCAL + '.0/24' 
    myScan = networkscan.Networkscan(myNetwork) 
    myScan.run()
    
    for ip in myScan.list_of_hosts_found:
        mac = get_mac_address(ip=ip)
        LIST_IP.append({'id':'0', 'ip':ip, 'mac':mac, 'port':'0', 'user':'user', 
            'passwd':'passwd', 'channel':'channel', 'source':'0', 'emUso':'False'})

    #for ipLocal in os.popen(cmd):     
    #    ipLocal = ipLocal.split(' ')
    #    if '[ether]' in ipLocal:
    #        ipLocal[1] = ipLocal[1].replace(')', '')
    #        LIST_IP.append({'ip':ipLocal[1].replace('(', ''),'mac':ipLocal[3] })
        
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
        
    for ip in LIST_IP: 
        
        if ip not in listCamAtivas:
            
            pktDescribe = describe(ip.get('ip'))
            
            for port in LIST_PORT:

                if ip not in listCamAtivas:
           
                    log.debug('-------')
                    log.debug("IP: {}:{}".format(ip.get('ip'), str(port)))
                    
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                        s.settimeout(TIMEOUT)
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
                            #print('Camera encontrada IP: {}:{}'.format(ip.get('ip'), str(port)))
                            #print('Mac: {}'.format(ip.get('mac')))
                            if (ip not in listCamAtivas):
                                for passwd in LIST_PASSWORD:
                                    if (ip not in listCamAtivas):
                                        for user in LIST_USERNAME:
                                            if (ip not in listCamAtivas):
                                                for channel in LIST_CHANNEL:
                                                    
                                                    if ip not in listCamAtivas:
                                                        
                                                        source = 'rtsp://' + user + ':' + passwd + '@' + ip.get('ip') + ':' + str(port) + '/' + channel 
                                                        ipCam, error = utils.camSource(source)                   
                                                        
                                                        if error != '':                                                                    
                                                            log.info('Erro camSource: {}'.format(error))

                                                            if ip not in listCamEncontradas and ip not in listCamAtivas: 

                                                                ip['id'] = 'Cam_' + str(idCam)
                                                                ip['port'] = str(port)
                                                                ip['port'] = str(port)
                                                                ip['user'] = user
                                                                ip['passwd'] = passwd
                                                                ip['channel'] = channel
                                                                ip['source'] = source 
                                                                listCamEncontradas.append(ip)
                                                                print('resp encontradas: ' + resp)
                                                                print(' ')
                                                                idCam = idCam + 1

                                                        else:                                    
                                                            log.info('Cam ativa encontrada')
                                                            log.info('source: {}'.format(source))
                                                            log.info('Data: \n {}'.format(dataDescribe.decode()))
                                                            log.info(' ')

                                                            ip['id'] = 'Cam_' + str(idCam)
                                                            ip['port'] = str(port)
                                                            ip['user'] = user
                                                            ip['passwd'] = passwd
                                                            ip['channel'] = channel
                                                            ip['source'] = source 
                                                            print('resp ativas: ' + resp)
                                                            print(' ')
                                                            listCamAtivas.append(ip)                                    
                                                            idCam = idCam + 1
                s.close()
        # end for in LIST_PORT                            
    s.close()
    
    return listCamEncontradas, listCamAtivas 
            


#if __name__ == '__main__':
#    
#    #print "   or https://github.com/tektengu/rtsp_discover/license.txt\n\n"
#
#    listCam, listRtsp, listRefused, listTimeout = createListIps()
#
#    print('List Cameras encontradas')
#    for cam in listCam:
#        print ('IP: ' + str(cam))
#        
#        
#    print('List Cameras Refused')
#    for cam in listRefused:
#        print ('IP: ' + str(cam))
#        
#    print('List Cameras Timeout')
#    for cam in listTimeout:
#        print ('IP: ' + str(cam))
#        
#    print('List Cameras Refused')
#    for cam in listRtsp:
#        print ('IP: ' + str(cam))        
    
    
