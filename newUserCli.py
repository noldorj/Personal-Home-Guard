import socketio
import logging as log
import sys

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
from smtplib import SMTPException
from smtplib import SMTP_SSL

import secrets

emailCliente = 'paulinhoks@gmail.com'
numCameras = '1'
diasLicenca = '30'



def sendMailnewUser(to, port, smtp, userPassword):

    status = False   
    
    
    sent_from = 'contato@portaovirtual.com.br'    
    gmail_password = 'flevkztxyqcaovue'    
    

    subject = ('Portão Virtual - Compra de Licença')

    body = ('Obrigado pela sua compra do software Portao Virtual ! \n\n Dados do seu login: \
        \n\n Usuário: {} \n Senha: {} \n\n Recomendamos que você altere a senha o quanto antes. \
    \n Link para download: https://ffc586ba-2e2b-4c36-abe6-ef6399680533.usrfiles.com/archives/ffc586_d900bfbbf80d4d92910d7b316a0c078e.zip \n \
    \n Link para o Manual: https://ffc586ba-2e2b-4c36-abe6-ef6399680533.usrfiles.com/ugd/ffc586_93634d61390045fe90c9fbe459e6ce9c.pdf \n \
    \n\n Atenciosamente, \n\n Equipe Portao Virtual \n\n www.portaovirtual.com.br ').format(to, userPassword)

    message = 'Subject: {} \n\n {}'.format(subject, body)
  
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(sent_from, gmail_password)
        server.sendmail(sent_from, to, message.encode('utf-8'))
        server.close()
        print ('Email enviado !')
        status = True
        
    except:
        print ('Something went wrong...')

    return status


log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)

sio = socketio.Client()
#ip fixo instancia AWS
#host = "http://ec2-18-230-50-38.sa-east-1.compute.amazonaws.com:5000"
host = "http://pvSessionLB-1827991081.sa-east-1.elb.amazonaws.com:5000"

statusNewUser = False

@sio.event
def connect():
    log.info('connect: conexao efetuada')


@sio.event
def newUser(login):
    log.info('Novo usuario: ' + login['user']) 
    sio.emit('newUser', login )


@sio.event 
def replyNewUser(status):
    global statusNewUser
    log.info('Novo Usuario status: ' + str(status))
    sio.disconnect()
    statusNewUser = status


def main():

    passwd = secrets.token_urlsafe(6)    
    
    print('email       : ' + emailCliente)
    print('passwd      : ' + passwd)
    print('numCameras  : ' + numCameras)
    print('diasLicenca : ' + diasLicenca)
    
    login = {'user':emailCliente, 'passwd':passwd, 'userEmail':emailCliente, 'numCameras':numCameras, 'diasLicenca':diasLicenca} 
    
    try: 
        sio.connect(host)

    except socketio.exceptions.ConnectionError as  err:

        log.info('Erro na conexao: ' + str(err))
      

    else:
        log.info('Conexao efetuada')
        
        newUser(login)  
        
        sio.wait()
        
        log.info('statusNewuser: {}'.format(statusNewUser))
    
    if statusNewUser:
        log.info('Usuario cadastrado com sucesso')

        sendMailnewUser(     emailCliente,                            
                            '465',
                            'smtp.gmail.com', 
                            passwd)


if __name__ == "__main__":
    main()

