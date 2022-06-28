import socketio
import sys
import utilsCore as utils
import logging

#log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.DEBUG, stream=sys.stdout)

#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.CRITICAL, filename='pv.log')





'''
log.root.setLevel(log.DEBUG)
log.basicConfig()
for handler in log.root.handlers[:]:
    log.root.removeHandler(handler)
log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, handlers=[log.FileHandler('config/pv.log', 'w', 'utf-8')])
log.getLogger('socketio').setLevel(log.ERROR)
log.getLogger('engineio').setLevel(log.ERROR)
'''
log = logging.getLogger('pv-log')
log.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('config/pv.log', 'w', 'utf-8')
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


sio = socketio.Client()
#sio = socketio.AsyncClient()
#ip fixo instancia AWS
#host = "http://ec2-18-230-53-22.sa-east-1.compute.amazonaws.com:5000"
#host = "http://ec2-18-230-50-38.sa-east-1.compute.amazonaws.com:5000"
#host = "http://pvSessionLB-1827991081.sa-east-1.elb.amazonaws.com:5000"
host = "http://34.145.8.88:5000"

loginStatus = False
sessionStatus = False
error = ''
changePasswdStatus = False
statusForgotPasswd = False
nuvemStatus = ''


local_sid = None


@sio.event
def connect():
    log.info('connect: conexao efetuada. sid: {}'.format(sio.get_sid()))
    #print('conectado')
    
    #sio.wait()

@sio.event
def checkLogin(login):
    #log.info('Login de: ' + login['user']) 
    #print('checkLogin...')
    sio.emit('checkLogin', login)


@sio.event
def checkNuvem(email):
    #print('Check session de: ' + session['user']) 
    sio.emit('checkNuvem', email)


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
        sio.disconnect()
    
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
        log.info('forgotPasswordPv:: Conexao efetuada ')
        forgotPassword(email)
        sio.wait()
        error = ''
        sio.disconnect()
    
    return statusForgotPasswd, error 


def checkSessionPv(session):
    global sessionStatus, error

    #sessionStatus = True

    try: 
        log.info("checkSessionPv:: conectando...")
        sio.connect(host)

    except Exception as  err:

        log.error('checkSessionPv:: Erro na conexao: ' + str(err))
        error = 'servidorOut' 
        sessionStatus = True

    else:
        #log.info('checkSessionPv:: Conexao efetuada checkSessionPv')
        error = ''
        checkSession(session)
        sio.wait()
        log.info('checkSessionPv: ' + str(sessionStatus))

        sio.disconnect()
    
    return sessionStatus, error


#opcoes de retorno
    # True: assina Nuvem e está pago
    # False: assina Nuvem e não está pago
    # 'semNuvem': não assina Nuvem
    # '': houve algum erro para checar sessao
    # 'conexao': erro de internet
def checkNuvemPv(email):
    global nuvemStatus, error
    error = ''

    #loginStatus = True

    try: 
        log.info("checkNuvemPv:: conectando...")
        sio.connect(host)
        #socketio.sleep(1) -- error module not found
        #sio.sleep(1)        
        #sio.wait()

    #except socketio.exceptions.ConnectionError as  err:
    except Exception as  err:

        log.error('checkNuvemPv:: Erro na conexao: ' + str(err))
        error = 'conexao' 
        nuvemStatus = 'True'
        sio.disconnect()

    else:
        log.info('checkNuvemPv:: Conexao efetuada')
        checkNuvem(email)
        sio.wait()
        #log.info('checkLoginPv:: loginStatus: ' + str(loginStatus))
        sio.disconnect()
          
    return nuvemStatus, error




def checkLoginPv(login):
    global loginStatus, error

    #loginStatus = True

    try: 
        log.info("checkLoginPv:: conectando...")
        sio.connect(host)
        #sio.sleep(1)
        #socketio.sleep(1)
        #sio.wait()

    #except socketio.exceptions.ConnectionError as  err:
    except Exception as  err:

        log.error('checkLoginPv:: Erro na conexao: ' + str(err))
        error = 'conexao' 
        loginStatus = True
        sio.disconnect()

    else:
        log.info('checkLoginPv:: Conexao efetuada')
        checkLogin(login)
        sio.wait()
        #log.info('checkLoginPv:: loginStatus: ' + str(loginStatus))
        sio.disconnect()
          
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
    print('replyLogin..')
    sio.disconnect()
    sio.wait()


@sio.event 
def replyNewUser(status):
    #log.info('Novo Usuario status: ' + str(status))
    sio.disconnect()


#opcoes de retorno
    # True: assina Nuvem e está pago
    # False: assina Nuvem e não está pago
    # 'semNuvem': não assina Nuvem
    # '': houve algum erro para checar sessao
    # 'conexao': erro de internet
@sio.event 
def replyCheckNuvem(status):
    global nuvemStatus
    print ('replyCheckNuvem:: nuvemStatus: ' + str(status))
    nuvemStatus = status 
    sio.disconnect()

@sio.event 
def replyCheckSession(status):
    global sessionStatus
    print ('replyCheckSession:: sessionStatus: ' + str(status))
    sessionStatus = status 
    sio.disconnect()

@sio.event 
def disconnect():        
    log.info('disconnect:: sid: {}'.format(sio.get_sid()))


