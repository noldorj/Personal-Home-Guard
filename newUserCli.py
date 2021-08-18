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

import firebase_admin
from firebase_admin import credentials

from firebase_admin import auth

import datetime

emailCliente = 'igorddf@gmail.com'
numCameras = '1'
diasLicenca = '0'

cred = {
      "type": "service_account",
      "project_id": "pvalarmes-3f7ee",
      "private_key_id": "4563d30a50f6b0e7dcc46291396761e2a62b2198",
      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDD1w6dONroiO/4\nyK/4nRqkTFPOa1FnNzbHHkKv5QwHN2KxezVY4dB75LuKfwC2lTwbBB182kLYABDZ\nw/qAWV96j6qDKPVK5BBs75xJixeuMTY3Cz0ChA74wIp4eC2iXws91zvJiDIC3Ox/\nNdEKKIuYtOagh6o8P7UOE1S/k3ywNe2u5SN7e5CNnqHW2iGR4P+RocNuV3WfeTSV\n7OEVMlOomA8z6nvBMU36B+KQL/XSP5pPPXd3kHl38OG0EFGGUPzCBc8vSFSdabWk\nDAmgHlk1TYZjOeasMSNBhjZDbmadtRl3OAE2KrykQV4YXdcVuMOnh9O86sP/U83x\nTjof5CLdAgMBAAECggEAA/OBk7n7LrBemRghdsRirnhsw3AmXQz/4a4SXd6i6r1b\nFCYeeivaKzm+7+kmkEh8BTaEyslTimyb6mzaD79d3gjqgYlww4FM9Im0D0bLZEQR\najRjl3qnG600zf/succtoKKITgVdrvGaoulozYnqYRsbQRdjn6IQateIgPH+lMaE\ntveBBQqu+AELnYxr5sDgbtdCeFbXFL6sTjxssl3hNQPTCcJisuOnqxX/2RhJyR3Z\nVhtqSHQcuM5TtJkV0qjK0gjmTNGAZaCaNjj0oTWbBAvIlOzYzFYkUq8XUvO//Lra\nG61FmijqrpTQs/CVMRhoEM/OuXZCfR/Hnd4XeDWVKQKBgQDuLRuwEvr6OsIHIxUZ\n1ZJIXvjFBPBo69s0dnNM966ia6Jo9RewAyAc6uVcG8Pw8TSOb0OXz2gSNp5312Kn\nANc25OFSaGTt9kKG6omD/ILZ+TvhzORD+pgSybPLM5EPW69Bs+Rwrh6tHVnMc06w\nDGMJk4Xp1QvtKTEcdCHs2ai7iQKBgQDSfuOK03sE1pw0v6ti/RB7hipQJObMgPBr\nfzf1QDQ/8tl4DalSu1YnYWLpwhTSOGIhnbaE1MG1P0eRtjDNqZwkebrbaOGFHxgc\ntFjHh/j3fDFF9/nSSUEJubbTy9hRmUZk/tYNOqXp95X0uTAKZWztxytKao9S3aJh\nZyh2EVFztQKBgQDUNaytvLuRqDioU0HBuuCTSssr/7KUSVEN9VvV//jBDlWuXnG0\niZRbL48b+kEitEa3gbsfz9RSJggbjvR/B+i5KET6P7ltrDSqMN5Fkv6jZ8VK8luP\nlf9Y/g4Lxu5AWNhWGgo3u2vponUYDMTXZrH3HlH6fbAaptDzISX4+hW0wQKBgQCV\nrquJzca98wpTLDToiEIPRKGUKhmBNPNBzc5x9Lzy+HMSPsy4SwUBrevThDKgJn4J\nn4fpvw0cIKp5AFCF/uVMvs9UNKmhqzHPP6OeB5/QBR1YvvSER5kbHFfZFix2IgN/\n0ANQlvLihC+7PXDfA67JCwdKvKm8aGSO1PddtgTwvQKBgQC63E2CwORx9KtYeBgI\nRbWnCVUb67K3WCS9bu5Yd5Gfc5IXBQChUg19645wNW7Vqxo1YiAbDO0SobOOn7iL\nIlOy2xWj+klRFMk6MoZ5rNcUJD6xAcq7K8mOORk3uVQ2ccbuq8MTrx3BL7FV+UqO\niw54w17h/4bR1e96Y0eM5ojCWw==\n-----END PRIVATE KEY-----\n",
      "client_email": "firebase-adminsdk-slpxb@pvalarmes-3f7ee.iam.gserviceaccount.com",
      "client_id": "106587989855928727506",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-slpxb%40pvalarmes-3f7ee.iam.gserviceaccount.com"
    }
#cred = credentials.Certificate("config/pvalarmes-3f7ee-firebase-adminsdk-slpxb-4563d30a50.json")

credential = credentials.Certificate(cred)

firebase_admin.initialize_app(credential, {'storageBucket': 'pvalarmes-3f7ee.appspot.com'})


def newUserFirebase(email, passwd):

    name = email.split('@')[0]
    
    user = auth.create_user(
    email=email, 
    email_verified=False,    
    password=passwd,
    display_name=name,    
    disabled=False)
    print('Sucessfully created new user: {0}'.format(user.uid))
    


def sendMailnewUser(to, port, smtp, userPassword):

    status = False   
    
    
    sent_from = 'contato@portaovirtual.com.br'    
    gmail_password = 'flevkztxyqcaovue'
    
    

    subject = ('Portão Virtual - Compra de Licença')

    body = ('Obrigado pela sua compra do software Portao Virtual ! \n\n Dados do seu login: \
        \n\n Usuário: {} \n Senha: {} \n\n Recomendamos que você altere a senha o quanto antes. \
    \n Link para download: https://drive.google.com/file/d/1YM7G-xrg2xinNQM6YoRmkYWpuI9cBr-b/view?usp=sharing \n \
    \n Link para o Manual: https://ffc586ba-2e2b-4c36-abe6-ef6399680533.usrfiles.com/ugd/ffc586_93634d61390045fe90c9fbe459e6ce9c.pdf \n \
    \n Link para baixar o App do Portão Virtual (versão Android por enquanto): https://play.google.com/store/apps/details?id=br.com.portaovirtual.pv \n \
    \n Obs: a senha do Aplicativo deve ser alterada por ele ! O Sistema Portão Virtual do seu computador não altera a senha do seu App que roda no seu celular \
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
#host = "http://pvSessionLB-1827991081.sa-east-1.elb.amazonaws.com:5000"
host = "http://34.145.8.88:5000"

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
    
    newUserFirebase(emailCliente, passwd)
    
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
    #newUserFirebase('igorddf@gmail.com','senha22')
    

