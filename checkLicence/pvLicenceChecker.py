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
TIME_SESSION = 5




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

    log.info(' ')
    log.info("newUser:: Criando novo usuario")    
    
    status = False
    userId = None

    #cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    #cursor = cnxn.cursor()

    #checar se usuário já existe
    try:
        
        if checkFileSession(userName):
            log.info('newUser::  Usuário existente')

        else:
            log.info('newUser::  Criando usuario {}'.format(userName))
                
            #criando arquivo de sessao baseado no ID
            
            date = getDate()
            currentDate = date.get('year') + '-' + date.get('month') + '-' + date.get('day')
            currentDate = datetime.strptime(currentDate, '%Y-%b-%d')
            currentDate = currentDate.strftime('%Y-%b-%d')

            #diasLicenca valor 0 significa vitalicia
            log.debug('newUser:: currentDate: {}'.format(currentDate.__str__()))

            token = [] 
            for i in range(0, int(numCameras)):
                token.append('0')
            
            log.info('newUser:: Usuario com [{}] tokens/licencas'.format(numCameras))

            lastToken = int(numCameras)-1
            log.info('newUser:: lastToken: {:d} '.format(lastToken))

            session = {
                'userId':userId,
                'userName':userName,
                'userPassword':userPassword,
                'userToken':token,
                'lastToken':str(lastToken),
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
                log.debug('newUser:: Salvando arquivo de sessao: {}'.format(userName))
                json.dump(session, open(file, 'w'),indent=3)

            except OSError as ex:
                
                log.critical('newUser:: Erro ao salvar o arquivo de sessao do Usuario: {}'.format(userName))                

            else:
                log.info('newUser:: Arquivo de sessão salvo - Usuario: {}'.format(userName))
                status = True

    except Error as error:
        log.critical(' ')
        log.critical('newUser:: Erro pra criar novo usuario')
        log.critical(error)
        log.critical(' ')   

    return status

def checkFileSession(file):
    
    try:
        with open(file) as f:

            log.info('Arquivo de sessao: {}  encontrado'.format(file))
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
            
            log.debug('checkLogin:: delta: {:d}'.format(delta))

            if delta <= int(session['diasLicenca']) or session['diasLicenca'] == '0': 
             
                #checar login
                if userName == session['userName'] and userPassword == session['userPassword']:

                    #checando userToken para garantir logins apenas em uma maquina por vez
                    #se userToken = '0' entao este é o primeiro login com este token gerado pelo PV-Client
                    log.debug('checkLogin:: Username: : ' + userName)
                    log.debug('checkLogin:: Token cliente: ' + userToken)
                    log.debug('checkLogin:: Token servidor: {}'.format(session['userToken']))
                    
                    tokenStatus = False

                    for token in session['userToken']:
                        if token == userToken:
                            log.debug('checkLogin:: Token True: {}'.format(session['userToken']))
                            tokenStatus = True
                            break
                    
                    log.debug('checkLogin:: Token status: {}'.format(tokenStatus))
                    
                    #if session['userToken'] != userToken:
                    if not tokenStatus:
                        #gravo o userToken na sessao
                        log.debug('checkLogin:: Sobrescrevendo sessoes')
                        
                        i = 0 
                        for token in session['userToken']:
                            if token == '0':
                                log.info('checkLogin:: token == 0')
                                session['userToken'][i] = userToken
                                break
                            i = i + 1

                        log.info('i: {:d}'.format(i))
                        log.info('len session[userToken]: {:d}'.format(len(session['userToken'])))
                        
                        if i == len(session['userToken']):
                            #session['userToken'][0] = userToken
                            log.info('i == len session[userToken] atualiando Token: {}'.format(userToken))
                            log.info('i == len session[userToken] lastToken: {}'.format(session['lastToken']))
                            session['userToken'][ int(session['lastToken'] )] = userToken

                        lastToken = 0
                        if int(session['numCameras']) > 1:  
                            if int(session['lastToken']) > 0 and \
                                    int(session['lastToken']) < int(session['numCameras']):

                                lastToken = int(session['lastToken']) - 1

                            else:

                                lastToken = int(session['numCameras']) - 1


                        log.info('lastToken: {}'.format(str(lastToken))) 
                        session['lastToken'] = str(lastToken)
                        #session['userToken'] = userToken
                        session['loginStatus'] = 'on'
                        session['sessionStatus'] = 'on'
                        session['lastLogin'] = lastLogin
                        session['lastSession'] = lastLogin

                    #se for um segundo login, valida o userToken e ativa a sessao - apenas para registro no log
                    #elif session['userToken'] == userToken:
                    elif tokenStatus:
                        log.debug('checkLogin:: Validando login - userToken existente')
                        
                        session['loginStatus'] = 'on'
                        session['sessionStatus'] = 'on'
                        session['lastLogin'] = lastLogin
                        session['lastSession'] = lastLogin

                    #se for um login devido a perda de sessao anterior ou login em outra maquina
                    elif session['sessionStatus'] == 'off' or session['loginStatus']=='off':
                        
                        log.info('checkLogin:: Validando perda de sessao')
                        log.info('checkLogin:: Atribuindo novo Token')

                        i = 0 
                        for token in session['userToken']:
                            if token == '0':
                                session['userToken'][i] = userToken
                                break
                            i = i + 1
                        
                        log.info('index i: {:d}'.format(i))

                        if i == len(session['userToken']):
                            log.info('atualiando Token: {}'.format(userToken))
                            log.info('atualiando lastLogin: {}'.format(session['lastToken']))
                            #session['userToken'][0] = userToken
                            session['userToken'][ int(session['lastToken'] )] = userToken
                            
                        
                        lastToken = 0
                        if int(session['lastToken']) > 0 and \
                                int(session['lastToken']) < int(session['numCameras']):

                            lastToken = int(session['lastToken']) - 1

                        else:

                            lastToken = int(session['numCameras']) - 1
                        
                        session['lastToken'] = str(lastToken)
                        #session['userToken'] = userToken
                        session['loginStatus'] = 'on'
                        session['sessionStatus'] = 'on'
                        session['lastLogin'] = lastLogin
                        session['lastSession'] = lastLogin

                    try:
                        log.info('checkLogin:: Atualizando arquivo de sessao: ' + file)
                        json.dump(session, open(file,'w'),indent=3)

                    except OSError as ex:
                        log.critical('checkLogin:: Erro ao gravar arquivo de sessao')

                    else:
                        log.info('checkLogin:: Sessao: {} atualizada'.format(userName))

                else:
                    log.debug('checkLogin:: Login invalido')
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
                    args=('contato@portaovirtual.com.br',
                    email,
                    'Portao Virtual - Recuperação de senha',
                    '587',
                    'smtp.gmail.com',
                    'contato@portaovirtual.com.br',
                    'flevkztxyqcaovue',
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

            tokenStatus = False

            for token in session['userToken']:
                if token == userToken:
                    tokenStatus = True
                    break
            
            log.debug('checkLogin:: Token status: {}'.format(tokenStatus))
            
            if (len(minutes)>1):
                #status = False
                #if userName == session['userName'] and userToken == session['userToken']:
                if userName == session['userName'] and tokenStatus:
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
                
                #if userName == session['userName'] and userToken == session['userToken']:
                if userName == session['userName'] and tokenStatus:
                    
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
