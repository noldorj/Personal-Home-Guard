#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 09:56:22 2020

@author: igor
"""
import os

def getTasks(name):
    r = os.popen('tasklist /v').read().strip().split('\n')
    print ('# of tasks is %s' % (len(r)))
    for i in range(len(r)):
        s = r[i]
        if name in r[i]:
            print ('%s in r[i]' %(name))
            return r[i]
    return []

if __name__ == '__main__':
    '''
    This code checks tasklist, and will print the status of a code
    '''

    imgName = 'dwm.exe'

    notResponding = 'Not Responding'

    r = getTasks(imgName)

    if not r:
        print('%s - No such process' % (imgName)) 

    elif 'Not Responding' in r:
        print('%s is Not responding' % (imgName))
        
    else:
        print('%s is Running or Unknown' % (imgName))