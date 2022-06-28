import eventlet
import socketio
import logging 
import sys
import os

from pvLicenceChecker import checkLogin as cl 
from pvLicenceChecker import newUser as nu 
from pvLicenceChecker import checkSession as cs 
from pvLicenceChecker import checkNuvem as checkN
from pvLicenceChecker import changePasswd as passwd 
from pvLicenceChecker import forgotPassword as forgotPasswd 

from pbkdf2 import PBKDF2
from cryptography.fernet import Fernet

log = logging.getLogger('pv-log')
log.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('pv.log', 'w', 'utf-8')
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

#log.basicConfig(format="[ %(levelname)s ] %(message)s", stream=sys.stdout)

@sio.event
def connect(sid, environ):
    log.info('connect: ' + sid)
    

@sio.event
def checkLogin(sid, login):
    #log.info('checkLogin: login' + login)
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
    status = nu(login['user'], login['passwd'], login['userEmail'], login['numCameras'], login['diasLicenca']) 
    sio.emit('replyNewUser', status, room=sid)
            

@sio.event
def checkNuvem(sid, email):
    log.info('checkNuvem: {}'.format(email))
    status = checkN(email)
    #status = cs(decrypt(session['user']), decrypt(session['token']))
    sio.emit('replyCheckNuvem', status, room=sid)

@sio.event
def checkSession(sid, session):
    log.info('checkSession: {}'.format(session))
    status = cs(decrypt(session['user']), decrypt(session['token']))
    sio.emit('replyCheckSession', status, room=sid)


@sio.event
def disconnect(sid):
    log.info('disconnect:: sid: ' +  sid)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
