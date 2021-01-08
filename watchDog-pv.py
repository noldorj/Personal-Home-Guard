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
    #log.info('Numero de processos: {} .'.format(len(r)) )
    for i in range(len(r)):
        s = r[i]
        s = s.split('.')

        if nameProcess in s:
            #log.info('Processo: "{}" em execução'.format(s[0]))
            return r[i]
    return []

def getTasksPid(nameProcess):
    for eachProcess in psutil.process_iter():
        if nameProcess == eachProcess.name():
            #log.info('proc.name: {}'.format(eachProcess.name()))
            #log.info('proc.pid: {:d}'.format(eachProcess.pid))
            return eachProcess.pid
    return 0

timesRestarted = 1
timeRunning = 0
DETACHED_PROCESS = 0x00000008


'''
This code checks tasklist, and will print the status of a code
'''

notResponding = 'Not Responding'

timeInit = time.time()
    
name = 'pv'
namePid = 'pv'

if sys.platform == 'linux':
    app = os.getcwd() + '/pv'
    namePid = 'portao_virtual_tracking'
else:
    #log.info('Windows')
    app = os.getcwd() + '/pv.exe'
    namePid = 'pv.exe'


log.info('Iniciando watchDog em 60 segundos...')
time.sleep(60)

while True:


    r = getTasks(name)
    
    if not r:
        
        log.debug('Portão Virtual não está em execução')
        
        timeRunning = (time.time() - timeInit) / 60 #em minutos
        
        log.debug('Portao Virtual inicializado pela {} vez '.format(timesRestarted))
        log.debug('Tempo de execução até o momento: {:f} min' .format(timeRunning))

        #subprocess.Popen([app], creationflags=DETACHED_PROCESS)
        subprocess.Popen(app.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, start_new_session=True, close_fds=True)
        
        timesRestarted = timesRestarted + 1
        timeInit = time.time()

    elif 'Not Responding' in r:
        log.critical('Portão Virtual não está respondendo ...')

    else:
        #log.info('Portão Virtual em execução')
        pid = getTasksPid(namePid)
        #log.info('ProcessID: {:d}'.format(pid))

    time.sleep(15)
