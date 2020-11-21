import eventlet
import socketio
import logging as log
import sys
import os

from pvLicenceChecker import checkLogin as cl 
from pvLicenceChecker import newUser as nu 
from pvLicenceChecker import checkSession as cs 
from pvLicenceChecker import changePasswd as passwd 
from pvLicenceChecker import forgotPassword as forgotPasswd 

from pbkdf2 import PBKDF2
from cryptography.fernet import Fernet

sio = socketio.Server()

app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})


def decrypt(token): 
     
    password = b'error'
    
    key = b'x-LhW_rs81XBzuFLq9jgUFOcGbjDWwWXS5A7lpV0onQ='
    fernetKey = Fernet(key)
    
    #Fernet.generate_key()
        
    
    try:
        #password = fernetKey.decrypt(token.encode())
        password = fernetKey.decrypt(token)

    except Exception as e:

        log.error('decrypt: error: {}'.format(e))
    
    return password.decode() 


def encrypt(password):
    
    token = 'error' 
    key = b'x-LhW_rs81XBzuFLq9jgUFOcGbjDWwWXS5A7lpV0onQ='    
    f = Fernet(key)

    try:
        token = f.encrypt(password.encode())    
    except Exception as e:
        
        log.error('utils.encrypt: error: {}'.format(e))
  
    return token

log.basicConfig(format="[ %(levelname)s ] %(message)s", stream=sys.stdout)

@sio.event
def connect(sid, environ):
    log.info('connect: ' + sid)

@sio.event
def checkLogin(sid, login):
    status = cl(decrypt(login['user']), decrypt(login['passwd']), decrypt(login['token'])) 
    sio.emit('replyLogin', status, room=sid)


@sio.event
def forgotPassword(sid, email):
    status = forgotPasswd(email)
    sio.emit('replyForgotPassword', status, room=sid)


@sio.event
def changePasswd(sid, login):
    status = passwd(decrypt(login['user']), decrypt(login['passwd']), decrypt(login['token']))
    sio.emit('replyChangePasswd', status, room=sid)


@sio.event
def newUser(sid, login):
    status = nu(login['user'], login['passwd'], login['userEmail'], login['numCameras']) 
    sio.emit('replyNewUser', status, room=sid)
            

@sio.event
def checkSession(sid, session):
    status = cs(decrypt(session['user']), decrypt(session['token']))
    sio.emit('replyCheckSession', status, room=sid)


@sio.event
def disconnect(sid):
    log.info('disconnect:: sid: ' +  sid)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
