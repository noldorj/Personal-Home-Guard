from sendingData import * 
import time
import sys

log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)

login1 = {'user':'igor1', 'passwd':'senha','token':'1'}
login2 = {'user':'igor10', 'passwd':'senha','token':'2'}
login3 = {'user':'igor10', 'passwd':'senha','token':'3'}

#sio = socketio.Client()
#ip fixo instancia AWS
#host = "http://ec2-18-230-53-22.sa-east-1.compute.amazonaws.com:5000"
host = "http://ec2-18-230-50-38.sa-east-1.compute.amazonaws.com:5000"

print('novo usuario - token 1')
sio.connect(host)
#checkLoginPv(login1)
#sio.wait()

newUser(login1)
sio.wait()

#sio.connect(host)
#print(' ')
#
##caso de uso: multiplos login sessao ativa
#print('token1 ativo - esperado true')
#checkLogin(login1)  #token 1 ativo
#sio.wait()
#sio.connect(host)
#print(' ')
#
##checkSession(login1)
##sio.wait()
##sio.connect(host)
#
#print('login2 - esperado erro')
#checkLogin(login2) #esperado erro
#sio.wait()
#sio.connect(host)
#print(' ')
#
#print('login3 - esperado erro')
#checkLogin(login3) #esperado erro
#sio.wait()
#print(' ')
#
##sessao expirou
#print('wait 60s')
#time.sleep(61) # pronto para ativar novo token - sessao off
#print(' ')
#
#print('checando sessao')
#sio.connect(host)
#checkSession(login1)
#sio.wait()
#sio.connect(host)
#
#print(' ')
#
#print('login2 - token 2 ativo')
#checkLogin(login2) #token 2 ativo
#sio.wait()
#sio.connect(host)
#print(' ')
#
#print('login1 - esperado erro')
#checkLogin(login1) #esperado erro de login 
#sio.wait()
#sio.connect(host)
#print(' ')
#
#print('login2 - esperado true')
#checkLogin(login2) #esperado true 
#sio.wait()
#
##sio.connect(host)
#
##session = {'user':'igor6', 'token':'aaa'}
##checkSession(session)
#
##sio.emit('my_message', {'usuario':'igor2'})
#
##data = "dados"
##my_message(data)
#
