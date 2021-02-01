#Teste de Servidor 

from checkLicence.sendingData import checkLoginPv
from checkLicence.sendingData import changePasswdPv
from checkLicence.sendingData import checkSessionPv
from checkLicence.sendingData import forgotPasswordPv
import utilsCore as utils

from threading import Thread
import logging as log
import secrets
import time


log.root.setLevel(log.DEBUG)
log.basicConfig()

for handler in log.root.handlers[:]:
    log.root.removeHandler(handler)


log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, handlers=[log.FileHandler('testes_servidor/testes_servidor.log', 'w', 'utf-8')])
log.getLogger('socketio').setLevel(log.ERROR)
log.getLogger('engineio').setLevel(log.ERROR)

#token = secrets.token_urlsafe(20)
token_g = 'wHe9sXX5lAKyvSDDQwuo8Ds-jZ4'

#print('token: {}'.format(token))
print('\n')

#100 usuarios

def teste_login(num_users):

    login = {'user':utils.encrypt('igorddf@gmail.com'), 'passwd':utils.encrypt('senha2'), 'token':utils.encrypt(token)}
    
    #log.info('Testando' + str(num_users) + 'Logins ao mesmo tempo')
    print('Testando [' + str(num_users) + '] Logins ao mesmo tempo')
    
    for i in range(1, num_users+1):
        #log.info('Teste login thread {:d}'.format(i))
        print('\n Teste login thread [{:d}]'.format(i))
        thread_user = Thread(target=login_unitario, args=(login, i))
        thread_user.start()
   
    
 
def login_unitario(login, id):
    statusLicence, error_login  = checkLoginPv(login)    
    log.info('Login id: {:d} , status: {} , error: {} '.format(id, statusLicence, error_login)) 
    print('\n Login id: {:d} , status: {} , error: {} '.format(id, statusLicence, error_login)) 
    

def sessao_unitario(login, id):

    sessionStatus, error = checkSessionPv(login)
    log.info('sessao id: {:d} , status: {} , error: {} '.format(id, sessionStatus, error)) 
    print('\n sessao id: {:d} , status: {} , error: {} '.format(id, sessionStatus, error)) 


def teste_sessao(num_users, tempo, token):
    
    login = {'user':utils.encrypt('igorddf@gmail.com'), 'passwd':utils.encrypt('senha2'), 'token':utils.encrypt(token)}
    
    statusLicence, error_login  = checkLoginPv(login)    
    
    time.sleep(2)
    
    timeSessionEnd = tempo + 1
    timeSessionInit = 0
    
    timeSession = timeSessionEnd - timeSessionInit
    
    while True:    
        
        print('\nTeste sessao iniciando a cada {:2.2f} minutos'.format(tempo/60))
        
        if timeSession >= tempo:
        
            for i in range(1, num_users+1):
                print('\n Disparando teste sessao ID [' + str(i) + ']')
                thread_user = Thread(target=sessao_unitario, args=(login, i))
                thread_user.start()
                time.sleep(0.5)
                
            timeSessionInit = time.time()           
        
        time.sleep(tempo)        
        timeSessionEnd = time.time() 
        

def teste_multiplas_sessoes():

    token1 = 'token1' 
    token2 = 'token2' 
    token3 = 'token3'  
    token4 = 'token4'   
    
    token5 = 'token5'
    token6 = 'token6'
    token7 = 'token7'
    
    login1 = {'user':utils.encrypt('igorddf@gmail.com'), 'passwd':utils.encrypt('senha'), 'token':utils.encrypt(token1)}
    login2 = {'user':utils.encrypt('igorddf@gmail.com'), 'passwd':utils.encrypt('senha'), 'token':utils.encrypt(token2)}
    login3 = {'user':utils.encrypt('igorddf@gmail.com'), 'passwd':utils.encrypt('senha'), 'token':utils.encrypt(token3)}
    login4 = {'user':utils.encrypt('igorddf@gmail.com'), 'passwd':utils.encrypt('senha'), 'token':utils.encrypt(token4)}
    login5 = {'user':utils.encrypt('igorddf@gmail.com'), 'passwd':utils.encrypt('senha'), 'token':utils.encrypt(token5)}
    
    print('Iniciando multiplos logins')
    status1, error1  = checkLoginPv(login1)    
    time.sleep(0.5)
    status2, error2  = checkLoginPv(login2)    
    time.sleep(0.5)
    status3, error3  = checkLoginPv(login3)    
    time.sleep(0.5)
    status4, error4  = checkLoginPv(login4)    
    time.sleep(0.5)
    
    print('Login resultados \n')
    print('status1: {} error1: {} \n'.format(status1, error1))
    print('status2: {} error2: {} \n'.format(status2, error2))
    print('status3: {} error3: {} \n'.format(status3, error3))
    print('status4: {} error4: {} \n'.format(status4, error4))
    
    print('\n Testando Login5')
    status5, error5  = checkLoginPv(login5)    
    print('\n status5: {} error5: {} \n'.format(status5, error5))
    

    
if __name__=="__main__":
    
    #teste_login(1)    
    #teste_sessao(25, 60, token_g)
    
    #teste_multiplas_sessoes()
    #teste_sessao(25, 60, 'token13')
    #teste_sessao(25, 60, 'token10')
    #teste_sessao(25, 60, 'token15')
    #teste_sessao(25, 60, 'token14')
    teste_sessao(1, 10, 'token10')
    
