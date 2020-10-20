#import pyodbc
import json
import time
from datetime import datetime
import logging as log
import pymysql
import sys

log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)

#tempo de expiracao da sessao em minutos
TIME_SESSION = 1

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
    
    log.info("pvLicenceChecker-server::  Alterando senha do usuario")
    
    file = 'sessions/'+ userName + '.json'
    
    status = checkFileSession(file)

    if status:

        try:

            session = json.load(open(file, 'r'))

        except OSError as ex:

            log.critical('Arquivo de sessao: {} não encontrado'.format(file))
            log.critical('Error: {}'.format(str(ex.errno)))
            status = False

        else:

            log.info('Sessao: {} lida com sucesso'.format(session.get('userName')+'.json'))
            
            log.info("changePasswd:: Usuario ok - alterando a senha no banco de dados...")

            conn = pymysql.connect(host, user=user,port=port, passwd=password, db=dbname)
    

            try:
                with conn.cursor() as cursor:
                    #cursor.execute("SET PASSWORD FOR '" + userName + "'@dbpv = PASSWORD('" + userPassword + "'")
                    #cursor.execute("ALTER USER '" + userName + "'@dbpv IDENTIFIED BY '" + userPassword + "'")
                    cursor.execute("UPDATE users set userPassword = '" + userPassword + "' where userName = '" + userName + "'")
                    
            except OSError as error:
                status = False
                log.critical(error)

            finally:
                
                log.info("senha alterada com sucesso no banco de dados")
                cursor.close()
                conn.close()
            
            #altera password da sessao 

            session['userPassword'] = userPassword

            try:
                log.info('Atualizando senha no arquivo de sessao: ' + file)
                json.dump(session, open(file,'w'),indent=3)

            except OSError as ex:
                status = False
                log.critical('Erro ao gravar arquivo de sessao')

            else:
                log.info('Sessao: {} atualizada'.format(userName))

    else:
        status = False 
        log.critical('Arquivo de sessao: {} não encontrado'.format(file))
        return status

    return status

def newUser(userName, userPassword, userEmail):

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
                log.info('pvLicenceChecker-server::newUsers::  Usuário existente')

            else:

                sql =  "INSERT INTO `users` (`userName`, `userPassword`, `userEmail`) VALUES (%s, %s, %s)"
                values = (userName, userPassword, userEmail) 
                cursor.execute(sql, values)
                conn.commit()

                cursor.execute("SELECT userId FROM users WHERE users.userName= '"+ userName + "'")
                userId = cursor.fetchone()[0]

                if userId == None:
                    log.critical('Erro ao cadastrar novo usuario')
                    status = False
                else:
                    log.info('Usuário cadastrado no banco de dados - userID: {}'.format(userId))

                    #criando arquivo de sessao baseado no ID
                    session = {
                        'userId':userId,
                        'userName':userName,
                        'userPassword':userPassword,
                        'userToken':'0',
                        'lastLogin':'0',
                        'lastSession':'0',
                        'loginStatus':'off',
                        'sessionStatus':'off'
                    }
                    file = 'sessions/' + str(userName) + '.json'
                    try:
                        json.dump(session, open(file, 'w'),indent=3)
                    except OSError as ex:
                        log.critical('Erro ao salvar o arquivo de sessao do Usuario: {}'.format(userName))
                        status = False
                    else:
                        log.info('Arquivo de sessão salvo - Usuario: {}'.format(userName))

    except Error as error:
        print(error)

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
    log.info('Checando arquivo de sessao do userName: ' + userName)
    file = 'sessions/'+ userName + '.json'
    

    session = None
    date = getDate()
    lastLogin = date.get('year') + '-' + date.get('month') + '-' + date.get('day') + ' ' + date.get('hourOnly') + ':' + date.get('minute')

    status = checkFileSession(file)

    if status:

        try:

            session = json.load(open(file, 'r'))

        except OSError as ex:

            log.critical('Arquivo de sessao: {} não encontrado'.format(file))
            log.critical('Error: {}'.format(str(ex.errno)))
            status = False

        else:

            log.info('Sessao: {} lida com sucesso'.format(session.get('userName')+'.json'))
            log.info('userPassword: {}'.format(userPassword))
            log.info('userPassword session: {}'.format(session['userPassword']))

            #checar login
            if userName == session['userName'] and userPassword == session['userPassword']:

                #checando userToken para garantir logins apenas em uma maquina por vez
                #se userToken = '0' entao este é o primeiro login com este token gerado pelo PV-Client
                log.info('Username: : ' + userName)
                log.info('Token cliente: ' + userToken)
                log.info('Token servidor: ' + session['userToken'])
                
                if session['userToken'] == '0':
                    #gravo o userToken na sessao
                    log.info('Primeiro login - sessao on')
                    
                    session['userToken'] = userToken
                    session['loginStatus'] = 'on'
                    session['sessionStatus'] = 'on'
                    session['lastLogin'] = lastLogin
                    session['lastSession'] = lastLogin

                #se for um segundo login, valida o userToken e ativa a sessao
                elif session['userToken'] == userToken:
                    log.info('Validando login - userToken existent')
                    
                    session['loginStatus'] = 'on'
                    session['sessionStatus'] = 'on'
                    session['lastLogin'] = lastLogin
                    session['lastSession'] = lastLogin

                #se for um login devido a perda de sessao anterior
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
                log.info('Login invalido')
                status = False

    else:
        log.critical('Arquivo de sessao: {} não encontrado'.format(file))
    
    return status



def saveSession(session, file):
    file = 'sessions/'+file+'.json'
    try:
        json.dump(session, open(file,'w'),indent=3)

    except OSError as ex:
        log.critical('Erro ao gravar arquivo de sessao')
    else:
        log.info('Sessao gravada')

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

            print('Arquivo de sessao: {} não encontrado'.format(file))
            print('Error: {}'.format(str(ex.errno)))
            status = False

        else:

            print('Sessao: {} lida com sucesso'.format(session.get('userName')+'.json'))

            #session = json.load(open('sessions/igor14.json', 'r'))

            lastSession = datetime.strptime(session['lastSession'], '%Y-%b-%d %H:%M')

            deltaSession = currentDate - lastSession

            minutes =  deltaSession.__str__().split(',')

            if (len(minutes)>1):
                status = False
                print('Sessão expirou')
               #expirou o tempo , dias já se passaram
            else:
                minutes = minutes[0].split(':')
                minutes = int(minutes[1])

                if userName == session['userName'] and userToken == session['userToken']:
                    if minutes < expireTime:
                        
                        session['lastSession'] = currentDate.__str__()
                        session['sessionStatus'] = 'on'
                        saveSession(session, userName)
                    else:
                        #sessao expirou ou token errado
                        print('Sessão expirada')
                        session['sessionStatus'] = 'off'
                        session['loginStatus'] = 'off'
                        saveSession(session, userName)
                        status = False
                else:
                    #usuario invalido
                    print('Usuario ou Token inválidos')
    else:
        log.critical('Arquivo de sessao: {} não encontrado'.format(file))

    return status
