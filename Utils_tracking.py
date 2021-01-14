#
import os
import cv2 as cv
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
from smtplib import SMTPException
import utilsCore as utils
import logging as log
import sys



#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', filename='pv.log')

def saveImageBox(frame, classe):

    #print('classe: ' + classe)
    idFoto = len(os.listdir(os.getcwd() + '/dataset/training_set/' + classe)) + 1
    #print('numero fotos: ' + str(idFoto))


    try:
        cv.imwrite(os.getcwd() + '/dataset/training_set/' + classe + '/' + classe + '.' + str(idFoto) + '.jpg',frame)
    except OSError as error:
        log.error("Erro em 'saveImageBox': " + str(error))
    else:
        log.debug('saveImageBox - imagem salva')


def sendMail(subject, text):

    statusConfig = utils.StatusConfig() 

    emailConfig = statusConfig.getEmailConfig()

    status = False

    sender = emailConfig['name']
    recipients = emailConfig['to']
    port = emailConfig['port']
    smtp = emailConfig['smtp']
    user = emailConfig['user']
    password = utils.decrypt(emailConfig['password'])


    #data = utils.getDate()
    msg = MIMEMultipart()

    msg['Subject'] = subject 
    msg['From'] = sender
    msg['To'] = recipients

    text = MIMEText(text)

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
        log.error("sendMail: Error: unable to send email" + str(e))

    else:
        log.debug('sendMail: {} enviado.'.format(subject))
        status = True

    return status





#envia alerta do portao virtual com imagem anexada ao email
def sendMailAlert(sender, recipients, subject, servidorEmail, user, frame, tipoObjetoDetectado, region, nameCam):
    
    statusConfig = utils.StatusConfig() 
    emailConfig = statusConfig.getEmailConfig()
    
    status = False

    img_file = os.getcwd() + '/' + 'foto_alerta.jpg'

    try:
        cv.imwrite(img_file, frame)

    except OSError as error:
        log.critical('Erro ao salvar a foto: ' + str(error))
        return status
    else:
        log.debug('Foto alarme salva')        


    try:
        img_file = open(img_file, 'rb').read()

    except OSError as error:
        log.critical('Erro ao anexar foto no email: ' + str(error))
        return status
    else:
        log.debug('Foto anexada')

    data = utils.getDate()
    msg = MIMEMultipart()

    if tipoObjetoDetectado == 'person':
        tipoObjetoDetectado = 'Pessoa'

    elif tipoObjetoDetectado == 'dog':
        tipoObjetoDetectado = 'Cachorro'

    elif tipoObjetoDetectado == 'bike':
        tipoObjetoDetectado = 'Moto'

    elif tipoObjetoDetectado == 'car':
        tipoObjetoDetectado = 'Carro'
    
       
    if tipoObjetoDetectado == 'teste':
        msg['Subject'] = 'Portão Virtual - Teste de Email [ ' + sender + ' ] - ' + data['hour']
    else:        
        msg['Subject'] = subject + ' - ' + '"' + tipoObjetoDetectado + '"' + ' na ' + region  + ' [' + nameCam + '] ' + data['hour']
    
    msg['From'] = user
    msg['To'] = recipients

    text = MIMEText('"' + tipoObjetoDetectado + '"' + ' na ' + region + '-  Detectado em ' + data['hour'] + ' - ' + data['day'] + '/' + data['month'] + '/' + data['year'] )
    msg.attach(text)

    img_file = MIMEImage(img_file)
    msg.attach(img_file)


    password = utils.decrypt(emailConfig['password'])
    
    
    log.debug('port: {:d}'.format(int(emailConfig['port'])))
    log.debug('smtp: {:}'.format(emailConfig['smtp']))
    log.debug('sender: {:}'.format(sender))
    log.debug('user: {:}'.format(user))
    log.debug('password: {:}'.format(password))
    log.debug('password: {:}'.format(password))
    log.debug(' ')     
        
    #if servidorEmail == 'Gmail':
    
    log.debug('sendMailAlert:: servidorEmail: {} '.format(emailConfig['servidorEmail']))
        
        #smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    
    try:
        smtpObj = smtplib.SMTP(emailConfig['smtp'], int(emailConfig['port']))
        smtpObj.ehlo()
        smtpObj.starttls()
        #smtpObj.ehlo()
        smtpObj.login(user, password)
        smtpObj.send_message(msg)
        smtpObj.quit()

    except SMTPException as e:
        log.critical("sendMailAlert:: Error: unable to send email" + str(e))       
        return False
    
    except Exception as e:
        log.critical("sendMailAlert:: Error: unable to send email" + str(e))       
        return False

    else:
        log.debug('sendMailAlert:: Email de alerta enviado')
        status = True

    # elif servidorEmail == 'Outlook':
    
        # log.debug('sendMailAlert:: usando Outlook') 
        # #smtpObj = smtplib.SMTP(smtp.office365.com, 587)
        # smtpObj = smtplib.SMTP(emailConfig['smtp'], int(emailConfig['port']))
        # try:
            # smtpObj.ehlo()
            # smtpObj.starttls()
            # #smtpObj.ehlo()
            # smtpObj.login(user, password)
            # smtpObj.send_message(msg)
            # smtpObj.quit()

        # except SMTPException as e:
            # log.critical("sendMailAlert:: Error Outlook: unable to send email" + str(e))
        # else:
            # log.debug('sendMailAlert:: Email de alerta enviado')
            # status = True
            
     
    
    
    return status


