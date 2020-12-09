import socketio
import logging as log
import sys
import utilsCore as utils

#log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.DEBUG, stream=sys.stdout)

#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', filename='pv.log')

sio = socketio.Client()
#sio = socketio.AsyncClient()
#ip fixo instancia AWS
#host = "http://ec2-18-230-53-22.sa-east-1.compute.amazonaws.com:5000"
#host = "http://ec2-18-230-50-38.sa-east-1.compute.amazonaws.com:5000"
host = "http://pvSessionLB-1827991081.sa-east-1.elb.amazonaws.com:5000"

loginStatus = False
sessionStatus = False
error = ''
changePasswdStatus = False
statusForgotPasswd = False


@sio.event
def connect():
    log.debug('connect: conexao efetuada')

@sio.event
def checkLogin(login):
    #log.info('Login de: ' + login['user']) 
    sio.emit('checkLogin', login)


@sio.event
def checkSession(session):
    #print('Check session de: ' + session['user']) 
    sio.emit('checkSession', session)

@sio.event
def forgotPassword(email):
    #log.info('forgotPassword:: email: ' + email) 
    sio.emit('forgotPassword', email)


@sio.event
def changePasswd(login):
    #log.info('changePasswd:: alterando senha do usuario: ' + login['user']) 
    sio.emit('changePasswd', login)


@sio.event
def newUser(login):
    #log.info('Novo usuario: ' + login['user']) 
    sio.emit('newUser', login )

@sio.event
def changePasswdPv(login):
    global changePasswdStatus, error
    
    
    try: 
        sio.connect(host)
        #sio.wait()

    except socketio.exceptions.ConnectionError as  err:

        log.error('Erro na conexao: ' + str(err))
        error = 'conexao' 
        changePasswdStatus = False

    else:
        #log.error('changePasswd:: Conexao efetuada')
        #log.info('changePasswd:: Alterando a senha do usuario: ' + login['user']) 
        error = ''

        changePasswd(login)  
        sio.wait()
    
        #log.info('changePasswd:: changePasswdStatus: ' + str(changePasswdStatus))
        #sio.disconnect()
    
    return changePasswdStatus, error



def forgotPasswordPv(email):
    global statusForgotPasswd, error

    try: 
        log.info("forgotPasswordPv:: conectando...")
        sio.connect(host)

    except socketio.exceptions.ConnectionError as  err:

        log.error('forgotPasswordPv:: Erro na conexao: ' + str(err))
        error = 'conexao' 
        statusForgotPasswd = False

    else:
        log.debug('forgotPasswordPv:: Conexao efetuada ')
        forgotPassword(email)
        sio.wait()
        error = ''
        #sio.disconnect()
    
    return statusForgotPasswd, error 


def checkSessionPv(session):
    global sessionStatus, error

    #sessionStatus = True

    try: 
        log.debug("checkSessionPv:: conectando...")
        sio.connect(host)

    except socketio.exceptions.ConnectionError as  err:

        log.error('checkSessionPv:: Erro na conexao: ' + str(err))
        error = 'servidorOut' 
        sessionStatus = False

    else:
        #log.info('checkSessionPv:: Conexao efetuada checkSessionPv')
        error = ''
        checkSession(session)
        sio.wait()
        #log.info('checkSessionPv: ' + str(sessionStatus))

        #sio.disconnect()
    
    return sessionStatus, error



def checkLoginPv(login):
    global loginStatus, error

    #loginStatus = True

    try: 
        sio.connect(host)
        #sio.wait()        

    except socketio.exceptions.ConnectionError as  err:

        log.error('checkLoginPv:: Erro na conexao: ' + str(err))
        error = 'conexao' 
        loginStatus = False

    else:
        log.warning('checkLoginPv:: Conexao efetuada')
        checkLogin(login)
        sio.wait()
        #log.info('checkLoginPv:: loginStatus: ' + str(loginStatus))
        #sio.disconnect()
    
    return loginStatus, error

@sio.event 
def replyChangePasswd(status):
    global changePasswdStatus, error

    changePasswdStatus = status
    
    if not status:
        error = 'login'

    #log.info('replyChangePasswd: ' + str(changePasswdStatus))
    sio.disconnect()


@sio.event 
def replyForgotPassword(status):
    global statusForgotPasswd
    
    statusForgotPasswd = status
    #log.info('replyForgotPassword:: statusForgotPasswd: ' + str(statusForgotPasswd))

    sio.disconnect() 



@sio.event 
def replyLogin(status):
    global loginStatus, error
    
    #log.info('replyLogin:: Login status: ' + str(status))
    
    loginStatus = status

    #neste caso, o erro foi de login .. e não de conexao com o servidor
    if not status:
        error = 'login'

    #log.info('replyLogin:: loginStatus: ' + str(loginStatus))
    sio.disconnect()
    sio.wait()


@sio.event 
def replyNewUser(status):
    #log.info('Novo Usuario status: ' + str(status))
    sio.disconnect()

@sio.event 
def replyCheckSession(status):
    global sessionStatus

    #print ('replyCheckSession:: sessionStatus: ' + str(status))
    sessionStatus = status 
    sio.disconnect()

@sio.event 
def disconnect(sid):
    log.debug('disconnect:: sid: {}'.format(sid))

