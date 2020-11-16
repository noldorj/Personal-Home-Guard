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
    print ('# of tasks is %s' % (len(r)))
    for i in range(len(r)):
        s = r[i]
        if name in r[i]:
            print ('%s in r[i]' %(name))
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
    
    
   
    
    while True:
        
        r = getTasks('portao_virtual_tracking.exe')        
        
        print(r)

        if not r:
            log.critical('Portão Virtual não está em execução')
            
            #cmds = shlex.split(app)
            #p = subprocess.Popen(app, start_new_session=True)
            
            timeRunning = (time.time() - timeInit) / 3600 #em horas
            
            log.critical('Portao Virtual inicializado pela {} vez '.format(timesRestarted))
            log.critical('Tempo de execução até o momento: {:03.1} hs' .format(timeRunning))
            
            #subprocess.call([app], close_fds=True)
            subprocess.Popen([app], creationflags=DETACHED_PROCESS)
            timesRestarted = timesRestarted + 1
            timeInit = time.time()

    
        elif 'Not Responding' in r:
            log.critical('Portão Virtual não está respondendo ...')
                    
        else:
            log.info('Portão Virtual em execução')
            
        time.sleep(60)