"""
Created on Sat Nov 14 09:56:22 2020

@author: igor
"""
import os
import logging as log
import time
import sys
import subprocess
#from subprocess import check_output
import psutil



def getTasks(nameProcess):
    
    r = os.popen('tasklist /v').read().strip().split('\n')    
    listP = []

    for i in range(len(r)):
        s = r[i]
        s = s.split('.')
        
        if nameProcess in s:    
            listP.append(r[i])            
    
    return listP

def getTasksPid(nameProcess, path):
    listP = []
    for eachProcess in psutil.process_iter():
        if nameProcess == eachProcess.name() and path == eachProcess.cwd():            
            listP.append([eachProcess.pid, eachProcess.cwd(), eachProcess.cmdline()])
            
            
    return listP
    #return 0

timesRestarted = 1
timeRunning = 0
DETACHED_PROCESS = 0x00000008

path_process = ''

notResponding = 'Not Responding'

timeInit = time.time()
    
name = 'pv'
namePid = 'pv'

listProcess = []

if sys.platform == 'linux':
    app = os.getcwd() + '/pv'
    namePid = 'portao_virtual_tracking'
else:
    #log.info('Windows')
    app = os.getcwd() + '/pv.exe'
    namePid = 'pv.exe'


log.info('Iniciando watchDog em 60 segundos...')
#time.sleep(60)

while True:

    listProcess = getTasksPid(namePid, os.getcwd())
    
    if len(listProcess) == 0:
        
        log.info('Portão Virtual não está em execução')
        
        timeRunning = (time.time() - timeInit) / 60 #em minutos
        
        log.info('Portao Virtual inicializado pela {} vez '.format(timesRestarted))
        log.info('Tempo de execução até o momento: {:f} min' .format(timeRunning))

        #subprocess.Popen([app], creationflags=DETACHED_PROCESS)
        subprocess.Popen(app.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, start_new_session=True, close_fds=True)
        
        timesRestarted = timesRestarted + 1
        timeInit = time.time()

    elif 'Not Responding' in listProcess:
        log.critical('Portão Virtual não está respondendo ...')

    else:
        log.info('Portão Virtual em execução')
        for proc in listProcess:
            pid, path, cmdline = proc[0], proc[1], proc[2]
            log.info('ProcessID: {:d} \n Path: {} \n Comando: {}'.format(pid, path, cmdline))            
            log.info('\n')        


    time.sleep(15)
