import socketio
import logging as log
import sys

log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)

sio = socketio.Client()
#ip fixo instancia AWS
#host = "http://ec2-18-230-53-22.sa-east-1.compute.amazonaws.com:5000"
host = "http://ec2-18-230-50-38.sa-east-1.compute.amazonaws.com:5000"

loginStatus = False
sessionStatus = False
error = ''
changePasswdStatus = False


@sio.event
def connect():
    log.info('conexao efetuada')

@sio.event
def sendingData():
    log.info('sendingData: Enviando dados...')
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
def changePasswd(login):
    global changePasswdStatus, error
    
    
    try: 
        sio.connect(host)

    except socketio.exceptions.ConnectionError as  err:

        log.info('Erro na conexao: ' + str(err))
        error = 'conexao' 

    else:
        log.info('Conexao efetuada')
       
        log.info('Alterando a senha do usuario: ' + login['user']) 
        sio.emit('changePasswd', login)
        sio.wait()
        log.info('changePasswd changePasswd: ' + str(changePasswd))
        #sio.disconnect()
    
    return changePasswd, error


def checkSessionPv(session):
    global sessionStatus, error

    sessionStatus = True

    try: 
        sio.connect(host)

    except socketio.exceptions.ConnectionError as  err:

        log.info('Erro na conexao: ' + str(err))
        error = 'conexao' 
        sessionStatus = False

    else:
        log.info('Conexao efetuada')
        checkSession(session)
        sio.wait()
        log.info('checkSessionPv: ' + str(sessionStatus))
    
    return sessionStatus, error



def checkLoginPv(login):
    global loginStatus, error

    loginStatus = True

    try: 
        sio.connect(host)

    except socketio.exceptions.ConnectionError as  err:

        log.info('Erro na conexao: ' + str(err))
        error = 'conexao' 
        loginStatus = False

    else:
        log.info('Conexao efetuada')
        checkLogin(login)
        sio.wait()
        log.info('loginStatus checkLoginPv: ' + str(loginStatus))
    
    return loginStatus, error

@sio.event 
def replyChangePasswd(status):
    global changePasswdStatus, error

    changePasswdStatus = status
    
    if not status:
        error = 'login'

    log.info('replyChangePasswd: ' + str(changePasswdStatus))
    sio.disconnect()


@sio.event 
def replyLogin(status):
    global loginStatus, error
    
    log.info('Login status: ' + str(status))
    
    loginStatus = status

    #neste caso, o erro foi de login .. e não de conexao com o servidor
    if not status:
        error = 'login'

    log.info('loginStatus replyLogin: ' + str(loginStatus))
    sio.disconnect()


@sio.event 
def replyNewUser(status):
    log.info('Novo Usuario status: ' + str(status))
    sio.disconnect()

@sio.event 
def replyCheckSession(status):
    global sessionStatus

    print ('Check Session status: ' + str(status))
    sessionStatus = status 
    sio.disconnect()

@sio.event 
def disconnect():
    print('desconectado')





