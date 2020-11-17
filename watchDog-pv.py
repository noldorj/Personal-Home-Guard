#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 09:56:22 2020

@author: igor
"""
import os
import logging as log
import time
import sys
import subprocess

log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, stream=sys.stdout)

def getTasks(name):
    r = os.popen('tasklist /v').read().strip().split('\n')
    log.info('Numero de processos: {} .'.format(len(r)) )
    for i in range(len(r)):
        s = r[i]        
        s = s.split('.')
        
        if name in s:
            log.info('Processo: "{}" em execução'.format(s[0]))
            return r[i]
    return []


timesRestarted = 1
timeRunning = 0
DETACHED_PROCESS = 0x00000008


if __name__ == '__main__':
    '''
    This code checks tasklist, and will print the status of a code
    '''
    
    notResponding = 'Not Responding'
    
    app = os.getcwd() + '/portao_virtual_tracking.exe'
    
    timeInit = time.time()
    
    name = "portao_virtual_tracking"
   
    
    while True:
        
        r = getTasks(name)  
        
        if not r:
        #if not getProcess(name):
            
            log.critical('Portão Virtual não está em execução')
            
            #cmds = shlex.split(app)
            #p = subprocess.Popen(app, start_new_session=True)
            
            timeRunning = (time.time() - timeInit) / 3600 #em horas
            
            log.critical('Portao Virtual inicializado pela {} vez '.format(timesRestarted))
            log.critical('Tempo de execução até o momento: {:03.1} hs' .format(timeRunning))
                        
            subprocess.Popen([app], creationflags=DETACHED_PROCESS)
            timesRestarted = timesRestarted + 1
            timeInit = time.time()

        elif 'Not Responding' in r:
            log.critical('Portão Virtual não está respondendo ...')
                    
        else:
            log.info('Portão Virtual em execução')
            
        time.sleep(10)