import eventlet
import socketio
import logging as log
import sys

from pvLicenceChecker import checkLogin as cl 
from pvLicenceChecker import newUser as nu 
from pvLicenceChecker import checkSession as cs 
from pvLicenceChecker import changePasswd as passwd 

sio = socketio.Server()

app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})



log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)

@sio.event
def connect(sid, environ):
    log.info('connect ' + sid)

@sio.event
def checkLogin(sid, login):
    log.info('checkLogin of: ' + login['user']) 
    log.info('sid: ' + sid) 
    status = cl(login['user'], login['passwd'], login['token']) 
    sio.emit('replyLogin', status, room=sid)


@sio.event
def changePasswd(sid, login):
    log.info('changePasswd of: ' + login['user']) 
    log.info('sid: ' +  sid) 
    status = passwd(login['user'], login['passwd'], login['token'])
    sio.emit('replyChangePasswd', status, room=sid)


@sio.event
def newUser(sid, login):
    log.info('newUser of: ' + login['user']) 
    log.info('sid: ' +  sid) 
    status = nu(login['user'], login['passwd'], login['token']) #IJF checar login['email'] no lugar de login['token']
    sio.emit('replyNewUser', status, room=sid)
            

@sio.event
def checkSession(sid, session):
    log.info('checkSession of: ' + session['user']) 
    log.info('sid: ' + sid) 
    status = cs(session['user'], session['token'])
    sio.emit('replyCheckSession', status, room=sid)


@sio.event
def disconnect(sid):
    log.info('disconnect ' +  sid)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
