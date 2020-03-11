import socketio
import logging as log

sio = socketio.Client()
#ip fixo instancia AWS
host = "http://ec2-18-230-53-22.sa-east-1.compute.amazonaws.com:5000"

loginStatus = False
sessaoStatus = False


@sio.event
def connect():
    print ('conexao efetuada')

@sio.event
def sendingData():
    print('enviando dados...')
    sio.emit('dados login', {'usuario':'igor2'})

@sio.event
def checkLogin(login):
    log.info('Login de: ' + login['user']) 
    sio.emit('checkLogin', login)


@sio.event
def checkSession(session):
    log.info('Check session de: ' + session['user']) 
    sio.emit('checkSession', session)


@sio.event
def newUser(login):
    log.info('Novo usuario: ' + login['user']) 
    sio.emit('newUser', login)

@sio.event 
def replyLogin(status):
    global loginStatus
    
    print ('Login status: ' + str(status))
    loginStatus = status 
    log.info('loginStatus replyLogin: ' + str(loginStatus))
    sio.disconnect()

@sio.event 
def replyNewUser(status):
    print ('Novo Usuario status: ' + str(status))
    sio.disconnect()

@sio.event 
def replyCheckSession(status):
    print ('Check Session status: ' + str(status))
    sio.disconnect()

@sio.event 
def disconnect():
    print('desconectado')

def checkLoginPv(login):
    global loginStatus
    
    sio.connect(host)
    checkLogin(login)
    sio.wait()
    log.info('loginStatus checkLoginPv: ' + str(loginStatus))
    return loginStatus




