#import pyodbc
import json
import time
from datetime import datetime
import logging as log
import pymysql
import sys
from threading import Thread

from utilsServer import sendMailForgotPasswd

#log.root.setLevel(log.DEBUG)
#log.basicConfig()

#for handler in log.root.handlers[:]:
#    log.root.removeHandler(handler)
#
#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.DEBUG, handlers=[log.FileHandler('pv-server.log', 'a', 'utf-8')])


#log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.DEBUG, stream=sys.stdout)

#tempo de expiracao da sessao em minutos
TIME_SESSION = 2

#host="dbpv.c3jzryxr6fxw.sa-east-1.rds.amazonaws.com"
host = "dbpv.cswsskc4btjh.sa-east-1.rds.amazonaws.com"  
port = 3306
dbname = "pv_users"
user = "igorddf"
password = "cacete33"

#conn = pymysql.connect(host, user=user,port=port, passwd=password, db=dbname)


def getDate():

    data = time.asctime().split(" ")
    #para dias com um digito
    if data.count("") > 0:
        data.remove("")
    data = {'day':data[2], 'month':data[1],'hour':data[3], 'year':data[4], 'weekDay':data[0].lower(), 'minute':data[3].split(":")[1], 'hourOnly':data[3].split(":")[0]}
    return data


def changePasswd(userName, userPassword, userToken):

    status = True
    
    log.info("changePasswd:: Alterando senha do usuario")
    
    file = 'sessions/'+ userName + '.json'
    
    status = checkFileSession(file)

    if status:

        try:

            session = json.load(open(file, 'r'))

        except OSError as ex:

            log.critical('changePasswd:: Arquivo de sessao: {} não encontrado'.format(file))
            log.critical('changePasswd:: Error: {}'.format(str(ex.errno)))
            status = False

        else:

            log.info('changePasswd:: Sessao: {} lida com sucesso'.format(session.get('userName')+'.json'))
            
            log.info("changePasswd:: Usuario ok - alterando a senha no banco de dados...")

            conn = pymysql.connect(host, user=user,port=port, passwd=password, db=dbname)
    

            try:
                with conn.cursor() as cursor:
                    
                    cursor.execute("UPDATE users set userPassword = '" + userPassword + "' where userName = '" + userName + "'")
                    
            except OSError as error:
                status = False
                log.critical('changePasswd:: error: {}'.format(error))

            finally:
                
                log.info("changePasswd:: senha alterada com sucesso no banco de dados")
                cursor.close()
                conn.close()
            
            #altera password da sessao 

            session['userPassword'] = userPassword

            try:
                log.info('changePasswd:: Atualizando senha no arquivo de sessao: ' + file)
                json.dump(session, open(file,'w'),indent=3)

            except OSError as ex:
                status = False
                log.critical('changePasswd:: Erro ao gravar arquivo de sessao')

            else:
                log.info('changePasswd:: Sessao: {} atualizada'.format(userName))

    else:
        status = False 
        log.critical('changePasswd:: Arquivo de sessao: {} não encontrado'.format(file))

    return status

def newUser(userName, userPassword, userEmail, numCameras, diasLicenca):

    log.info("pvLicenceChecker-server:: Criando novo usuario")

    conn = pymysql.connect(host, user=user,port=port, passwd=password, db=dbname)
    
    status = True
    userId = None

    #cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    #cursor = cnxn.cursor()

    #checar se usuário já existe
    try:
        with conn.cursor() as cursor:

            cursor.execute("SELECT userName FROM users WHERE users.userName= '"+ userName + "'")
            dbUserName = cursor.fetchone()

            if (dbUserName is not None and dbUserName[0] == userName):
                status = False
                log.info('newUsers::  Usuário existente')

            else:

                sql =  "INSERT INTO `users` (`userName`, `userPassword`, `userEmail`, `numCameras`, `diasLicenca`) VALUES (%s, %s, %s, %s, %s)"
                values = (userName, userPassword, userEmail, numCameras, diasLicenca) 
                cursor.execute(sql, values)
                conn.commit()

                cursor.execute("SELECT userId FROM users WHERE users.userName= '"+ userName + "'")
                userId = cursor.fetchone()[0]

                if userId == None:

                    log.critical('newUser:: Erro ao cadastrar novo usuario')
                    status = False

                else:

                    log.info('newUsers:: Usuário cadastrado no banco de dados - userID: {}'.format(userId))

                    #criando arquivo de sessao baseado no ID

                    date = getDate()
                    currentDate = date.get('year') + '-' + date.get('month') + '-' + date.get('day')
                    currentDate = datetime.strptime(currentDate, '%Y-%b-%d')
                    currentDate = currentDate.strftime('%Y-%b-%d')

                    #diasLicenca valor 0 significa vitalicia
                    log.debug('currentDate: {}'.format(currentDate.__str__()))

                    session = {
                        'userId':userId,
                        'userName':userName,
                        'userPassword':userPassword,
                        'userToken':'0',
                        'lastLogin':'0',
                        'lastSession':'0',
                        'loginStatus':'off',
                        'sessionStatus':'off',
                        'numCameras':numCameras,
                        'diasLicenca':diasLicenca,
                        'inicioLicenca':currentDate.__str__()
                    }
                    file = 'sessions/' + str(userName) + '.json'
                    try:
                        log.debug('Salvando arquivo de sessao: {}'.format(userName))
                        json.dump(session, open(file, 'w'),indent=3)

                    except OSError as ex:
                        
                        log.critical('newUsers:: Erro ao salvar o arquivo de sessao do Usuario: {}'.format(userName))
                        status = False

                    else:
                        log.info('newUsers:: Arquivo de sessão salvo - Usuario: {}'.format(userName))

    except Error as error:

        log.critical(error)

    finally:
        cursor.close()
        conn.close()

    return status

def checkFileSession(file):
    
    try:
        with open(file) as f:

            log.info('Arquivo de sessao: {}  enconrado'.format(file))
            return True

    except IOError:

        log.critical('Arquivo de sessao: ' + file + ' nao existente')
        return False



def checkLogin(userName, userPassword, userToken):

    status = True
    #checar se existe arquivo de sesson 'userName.json'
    log.debug('checkLogin:: Checando arquivo de sessao do userName: ' + userName)
    file = 'sessions/'+ userName + '.json'
    

    session = None
    date = getDate()
    lastLogin = date.get('year') + '-' + date.get('month') + '-' + date.get('day') + ' ' + date.get('hourOnly') + ':' + date.get('minute')

    status = checkFileSession(file)

    if status:

        try:

            session = json.load(open(file, 'r'))

        except OSError as ex:

            log.critical('checkLogin:: Arquivo de sessao: {} não encontrado'.format(file))
            log.critical('checkLogin:: Error: {}'.format(str(ex.errno)))
            status = False

        else:

            log.info('checkLogin:: Sessao: {} lida com sucesso'.format(session.get('userName')+'.json'))
            #log.info('userPassword: {}'.format(userPassword))
            #log.info('userPassword session: {}'.format(session['userPassword']))

            #checar versao de testes
            date = getDate()
            currentDate = date.get('year') + '-' + date.get('month') + '-' + date.get('day') 
            currentDate = datetime.strptime(currentDate, '%Y-%b-%d')
            
            log.debug('inicioLicenca session : {}'.format(session['inicioLicenca']))
            
            inicioLicenca = datetime.strptime(session['inicioLicenca'], '%Y-%b-%d')
            
            deltaLicenca = currentDate - inicioLicenca 

            log.debug('deltaLicenca : {}'.format(deltaLicenca.__str__().split('-')))
            log.debug('inicioLicenca : {}'.format(inicioLicenca.__str__()))
            log.debug('currentDate: {}'.format(currentDate.__str__()))

            if deltaLicenca.__str__() == '0:00:00':
                delta = 0
            else:
                delta = deltaLicenca.__str__().split(',')[0]
                delta = int(delta.split(' ')[0])
            
            log.debug('delta: {:d}'.format(delta))

            if delta <= int(session['diasLicenca']) or session['diasLicenca'] == '0': 
             
                #checar login
                if userName == session['userName'] and userPassword == session['userPassword']:

                    #checando userToken para garantir logins apenas em uma maquina por vez
                    #se userToken = '0' entao este é o primeiro login com este token gerado pelo PV-Client
                    log.debug('Username: : ' + userName)
                    log.debug('Token cliente: ' + userToken)
                    log.debug('Token servidor: ' + session['userToken'])
                    
                    if session['userToken'] != userToken:
                        #gravo o userToken na sessao
                        log.debug('Primeiro login - sessao on')
                        
                        session['userToken'] = userToken
                        session['loginStatus'] = 'on'
                        session['sessionStatus'] = 'on'
                        session['lastLogin'] = lastLogin
                        session['lastSession'] = lastLogin

                    #se for um segundo login, valida o userToken e ativa a sessao - apenas para registro no log
                    elif session['userToken'] == userToken:
                        log.debug('Validando login - userToken existente')
                        
                        session['loginStatus'] = 'on'
                        session['sessionStatus'] = 'on'
                        session['lastLogin'] = lastLogin
                        session['lastSession'] = lastLogin

                    #se for um login devido a perda de sessao anterior ou login em outra maquina
                    elif session['sessionStatus'] == 'off' or session['loginStatus']=='off':
                        
                        log.info('Validando perda de sessao')
                        log.info('Atribuindo novo Token')

                        session['userToken'] = userToken
                        session['loginStatus'] = 'on'
                        session['sessionStatus'] = 'on'
                        session['lastLogin'] = lastLogin
                        session['lastSession'] = lastLogin

                    try:
                        log.info('Atualizando arquivo de sessao: ' + file)
                        json.dump(session, open(file,'w'),indent=3)

                    except OSError as ex:
                        log.critical('Erro ao gravar arquivo de sessao')

                    else:
                        log.info('Sessao: {} atualizada'.format(userName))

                else:
                    log.debug('Login invalido')
                    status = False

            #checando diasLicenca 
            else:
                log.critical('checkLogin:: Licenca de teste expirou')
                status = False


    else:
        log.critical('checkLogin:: Arquivo de sessao: {} não encontrado'.format(file))
    
    return status



def saveSession(session, file):
    file = 'sessions/'+file+'.json'
    try:
        json.dump(session, open(file,'w'),indent=3)

    except OSError as ex:
        log.critical('saveSession:: Erro ao gravar arquivo de sessao')
    else:
        log.info('saveSession:: Sessao gravada')


def forgotPassword(email):
    
    file = 'sessions/'+ email + '.json'
    status = checkFileSession(file) 
    session = None

    if status:

        try:

            session = json.load(open(file, 'r'))

        except OSError as ex:

            log.critical('forgotPassword:: Arquivo de sessao: {} não encontrado'.format(file))
            log.critical('forgotPassword:: Error: {}'.format(str(ex.errno)))
            status = False

        else:
            
            passwd = session['userPassword']

            threadEmail = Thread(target=sendMailForgotPasswd, 
                    args=('portaovirtual@contato.com.br',
                    email,
                    'Portao Virtual - Recuperação de senha',
                    '587',
                    'smtp.gmail.com', 
                    'portaovirtual@gmail.com',
                    'budega11',
                    passwd
                                                                                                               ))                                                                        
        threadEmail.start()  
        status = True

    return status


def checkSession(userName, userToken):
    status = True
    expireTime = TIME_SESSION #em minutos

    #checar se existe arquivo de sesson 'userName.json'
    file = 'sessions/'+ userName + '.json'
    
    status = checkFileSession(file) 

    if status: 
    
        session = None
        date = getDate()
        currentDate = date.get('year') + '-' + date.get('month') + '-' + date.get('day') + ' ' + date.get('hourOnly') + ':' + date.get('minute')
        currentDate = datetime.strptime(currentDate, '%Y-%b-%d %H:%M')
        
        try:

            session = json.load(open(file, 'r'))

        except OSError as ex:

            log.critical('checkSession:: Arquivo de sessao: {} não encontrado'.format(file))
            log.critical('checkSession Error: {}'.format(str(ex.errno)))
            status = False

        else:

            log.debug('checkSession:: Sessao: {} lida com sucesso'.format(session.get('userName')+'.json'))

            #session = json.load(open('sessions/igor14.json', 'r'))

            lastSession = datetime.strptime(session['lastSession'], '%Y-%b-%d %H:%M')
            
            deltaSession = currentDate - lastSession

            minutes =  deltaSession.__str__().split(',')
            
            #usando strftime para corrigir inclusao de segundos, indevidamente, na data 
            currentDate = currentDate.strftime('%Y-%b-%d %H:%M')

            if (len(minutes)>1):
                #status = False
                if userName == session['userName'] and userToken == session['userToken']:
                    log.critical('checkSession:: Sessão expirou')
                    session['sessionStatus'] = 'off'
                    session['loginStatus'] = 'off'
                    saveSession(session, userName)
                    #sessao expirou, mas tem que retornar True se a conexao voltar 
                    status = True 
                else:
                    status = False
                    log.critical('checkSession:: Sessão expirou. Mas User e Token são válidos')
                    session['sessionStatus'] = 'off'
                    session['loginStatus'] = 'off'
               #expirou o tempo , dias já se passaram
            else:
                minutes = minutes[0].split(':')
                minutes = int(minutes[1])

                log.debug('checkSession:: lastSession  : {}'.format(lastSession))
                log.debug('checkSession:: currentDate  : {}'.format(currentDate))
                log.debug('checkSession:: deltaSession : {}'.format(deltaSession))
                log.debug('')
                log.debug('checkSession:: userName          : {}'.format(userName))
                log.debug('checkSession:: session userName  : {}'.format(session['userName']))
                log.debug('checkSession:: userToken         : {}'.format(userToken))
                log.debug('checkSession:: session userToken : {}'.format(session['userToken']))
                
                if userName == session['userName'] and userToken == session['userToken']:
                    
                    log.debug('checkSession:: minutes    : {}'.format(minutes))
                    log.debug('checkSession:: expireTime : {}'.format(expireTime))
                    
                    if minutes < expireTime:
                        
                        session['lastSession'] = currentDate.__str__()
                        session['sessionStatus'] = 'on'
                        saveSession(session, userName)
                        log.info('checkSession:: Sessao [{}] validada'.format(userName))
                        status = True

                    else:
                        #sessao expirou - apenas para registrar quanto tempo ficou off 
                        session['sessionStatus'] = 'off'
                        session['loginStatus'] = 'off'
                        saveSession(session, userName)
                        #sessao expirou, mas tem que retornar True se a conexao voltar 
                        #status = False 
                        status = True 
                        log.critical('checkSession:: Sessão expirou. Mas User e Token são válidos')
                else:
                    #usuario ou token invalidos
                    status = False
                    log.critical('checkSession:: Usuario [{}] ou Token inválidos'.format(userName))
    else:
        log.critical('checkSession:: Arquivo de sessao: {} não encontrado'.format(file))
        status = False

    return status
