import socketio
import logging as log
import sys

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
from smtplib import SMTPException


def sendMailnewUser(sender, recipients, subject, port, smtp, user, password, userPassword):

    status = False

    #data = utils.getDate()
    msg = MIMEMultipart()

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients

    text = MIMEText('Obrigado pela sua compra do software Portao Virtual ! Dados do seu login: Usuário : ' + user + '  Senha   : ' + userPassword + ' . Recomendamos que você altere a senha o quanto antes. Atenciosamente, Equipe Portao Virtual www.portaovirtual.com.br'
            )
    msg.attach(text)

    smtpObj = smtplib.SMTP(smtp, int(port))
    try:
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(sender,password)
        smtpObj.send_message(msg)
        smtpObj.quit()

    except SMTPException as e:
        log.info("sendMailForgotPasswd:: Error: unable to send email" + str(e))

    else:
        log.info('sendMailForgotPasswd:: Email Esqueceu a Senha - enviado')
        status = True

    return status


log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)

sio = socketio.Client()
#ip fixo instancia AWS
host = "http://ec2-18-230-50-38.sa-east-1.compute.amazonaws.com:5000"

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

    email = sys.argv[1]
    passwd = sys.argv[2]
    numCameras = sys.argv[3]
    
    print('email:      ' + email)
    print('passwd:     ' + passwd)
    print('numCameras: ' + numCameras)
    
    login = {'user':email, 'passwd':passwd, 'userEmail':email, 'numCameras':numCameras} 
    
    try: 
        sio.connect(host)

    except socketio.exceptions.ConnectionError as  err:

        log.info('Erro na conexao: ' + str(err))
        error = 'conexao' 
        status = False

    else:
        log.info('Conexao efetuada')
        
        newUser(login)  
        
        sio.wait()
        
        log.info('statusNewuser: {}'.format(statusNewUser))
    
    if statusNewUser:
        log.info('Usuario cadastrado com sucesso')

        sendMailnewUser('contato@portaovirtual.com.br',
                            email,
                            'Portao Virtual - Compra',
                            '587',
                            'smtp.gmail.com',
                            email,
                            'cacete33',
                            passwd)





if __name__ == "__main__":
    main()

def teste():
    email = 'igorddf@gmail.com'    
    passwd = 'senha'

    sendMailnewUser('contato@portaovirtual.com.br',
                            email,
                            'Portao Virtual - Compra',
                            '587',
                            'smtp.gmail.com',
                            email,
                            'cacete33',
                            passwd)
