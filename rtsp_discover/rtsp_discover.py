# RTSP Auth Grinder
# USAGE: rtsp_authgrind [-l username | -L username_file] [-p password | -P password_file] <target ip[:port]>
# Author: TekTengu
# Copyright (C) 2014 Luke Stephens and Tek Security Group, LLC - all rights reserved

"""
    rtsp_discover.py - A quick tool to run the DESCRIBE and OPTIONS verbs against an RTSP
    connection. Will provide key information or clue the auditor into this
    possibly not being a true RTSP connection.

    Copyright (C) 2014 Luke Stephens and Tek Security Group, LLC - all rights reserved

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    RTSP Discover is provided for testing purposes only and is not
    authorized for use to conduct malicious, illegal or other nefarious activities.

    Standard usage is:

    python rtsp_discover <target ip [:port]>

"""
import utilsCore as utils

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


LIST_PORT = [554, 8554]
LIST_IP = []

OS_PLATFORM = 'windows'

if sys.platform == 'linux':
    OS_PLATFORM = 'linux'


DESCRIBEPACKET = ""
OPTIONSPACKET = ""
TIMEOUT = 10

LIST_CHANNEL = ['profile0', '', 'profile1', 'Streaming/Channels/01', 'h264?channel=1', 'onvif1']

LIST_PASSWORD = ['WWYZRL', '123456', '1234', '12345', 'admin', '9999', 'pass', 'none',
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

def createListIps():
  
    #definindo IP Local
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP_LOCAL = s.getsockname()[0]
    IP_LOCAL = IP_LOCAL.split('.')
    IP_LOCAL = IP_LOCAL[0] + '.' + IP_LOCAL[1] + '.' + IP_LOCAL[2]
    s.close()
    
    listCamEncontradas = []
    listCamRtspOk = []
    listCamRefused = []
    listCamTimeout = []
    dataDescribe = None
    
   
    if OS_PLATFORM == 'linux':
        cmd = 'arp -a'
    else:
        cmd = 'arp /a'
        
    myNetwork = IP_LOCAL + '.0/24' 
    myScan = networkscan.Networkscan(myNetwork) 
    myScan.run()
    
    for ip in myScan.list_of_hosts_found:
        mac = get_mac_address(ip=ip)
        LIST_IP.append({'ip':ip, 'mac':mac, 'port':'0', 'user':'user', 
                        'passwd':'passwd', 'channel':'channel'})

    #for ipLocal in os.popen(cmd):     
    #    ipLocal = ipLocal.split(' ')
    #    if '[ether]' in ipLocal:
    #        ipLocal[1] = ipLocal[1].replace(')', '')
    #        LIST_IP.append({'ip':ipLocal[1].replace('(', ''),'mac':ipLocal[3] })
        
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    #ip = '192.168.5.60'
    #port = 554
        
    for ip in LIST_IP: 
        
        if ip not in listCamEncontradas:
            
            #ip = IP_LOCAL + '.' + str(i)
            pktDescribe = describe(ip.get('ip'))
            
            for port in LIST_PORT:    
           
                print ('-------')
                print("IP: {}:{}".format(ip.get('ip'), str(port)))
                
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
                    s.settimeout(TIMEOUT)
                    s.connect((ip.get('ip'), port))
                    #s.connect((ip, port))
    
                except socket.timeout:
                    print("Timeout IP: {}:{}".format(ip.get('ip'), str(port)))
                    listCamTimeout.append(ip.get('ip'))
    
                except socket.error as e:
                    if e.errno == errno.ECONNREFUSED:
                        print('Conenction Refused IP: {}:{}'.format(ip.get('ip'), str(port)))
                        listCamRefused.append(ip.get('ip'))
                        
                else:
                                
                    s.sendall(pktDescribe)            
                    dataDescribe = s.recv(1024)                    
                    
                    if dataDescribe is not None:
                        resp = dataDescribe.decode()
                        print('Camera encontrada IP: {}:{}'.format(ip.get('ip'), str(port)))
                        print('Mac: {}'.format(ip.get('mac')))
                        #print('Data: \n' + dataDescribe.decode())                    
                        for passwd in LIST_PASSWORD:
                            if (ip not in listCamEncontradas):
                                for user in LIST_USERNAME:
                                    if (ip not in listCamEncontradas):
                                        for channel in LIST_CHANNEL:
                                            
                                            if (ip not in listCamEncontradas):
                                                
                                                source = 'rtsp://' + user + ':' + passwd + '@' + ip.get('ip') + ':' + str(port) + '/' + channel 
                                                print('source: {}'.format(source))
                                                ipCam, error = utils.camSource(source)                   
                                                
                                                if error != '':                                                                    
                                                    print('Erro camSource: {}'.format(error))
                                                else:                                    
                                                    print('Conexao com camera restabelecida.')
                                                    ip['port'] = str(port)
                                                    ip['user'] = user
                                                    ip['passwd'] = passwd
                                                    ip['channel'] = channel
                                                    listCamEncontradas.append(ip)                                    
            s.close()
        # end for in LIST_PORT                            
    s.close()
    
    return listCamEncontradas, listCamRtspOk, listCamRefused, listCamTimeout
            


if __name__ == '__main__':
    
    #print "   or https://github.com/tektengu/rtsp_discover/license.txt\n\n"

    listCam, listRtsp, listRefused, listTimeout = createListIps()

    print('List Cameras encontradas')
    for cam in listCam:
        print ('IP: ' + str(cam))
        
        
    print('List Cameras Refused')
    for cam in listRefused:
        print ('IP: ' + str(cam))
        
    print('List Cameras Timeout')
    for cam in listTimeout:
        print ('IP: ' + str(cam))
        
    print('List Cameras Refused')
    for cam in listRtsp:
        print ('IP: ' + str(cam))        
    
    
