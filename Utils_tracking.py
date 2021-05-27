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
import urllib.request


import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import storage
import datetime



cred = credentials.Certificate("config/pvalarmes-3f7ee-firebase-adminsdk-slpxb-4563d30a50.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'pvalarmes-3f7ee.appspot.com'})


#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', filename='pv.log')


def saveImageFirebase(frame, idImage, user):

    bucket = storage.bucket()    
    
    img_file = os.getcwd() + '/config/alertas_app/' + idImage + '.jpg'
    
    try:
        cv.imwrite(img_file, frame)

    except OSError as error:
        log.critical('Erro ao salvar a foto: ' + str(error))
        return status
    else:
        log.info('Foto alarme app salva')        
        
     

    
    # try:
        # img_file = open(img_file, 'rb').read()        

    # except OSError as error:
        # log.critical('Erro ao anexar foto no email: ' + str(error))
        # return status
    # else:
        # log.info('Foto anexada')
    
    bucket = storage.bucket()
    
    blob = bucket.blob(user + '/' + idImage + '.jpg')
    
    blob.upload_from_filename(img_file)
    
    blob.make_public() 
    
    
    return blob.public_url, blob.name  



def saveImageBox(frame, classe):

    #print('classe: ' + classe)
    idFoto = len(os.listdir(os.getcwd() + '/dataset/training_set/' + classe)) + 1
    #print('numero fotos: ' + str(idFoto))


    try:
        cv.imwrite(os.getcwd() + '/dataset/training_set/' + classe + '/' + classe + '.' + str(idFoto) + '.jpg',frame)
    except OSError as error:
        log.error("Erro em 'saveImageBox': " + str(error))
    else:
        log.info('saveImageBox - imagem salva')


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
        log.info('sendMail: {} enviado.'.format(subject))
        status = True

    return status


def sendAlertApp(user, frame, tipoObjetoDetectado, region, nameCam):

    log.info('user: {}'.format(user))
    
    
    date = utils.getDate()
    
    if date['month'] == 'Jan': date['month'] = '01'
    if date['month'] == 'Feb': date['month'] = '02'
    if date['month'] == 'Mar': date['month'] = '03'
    if date['month'] == 'Apr': date['month'] = '04'
    if date['month'] == 'May': date['month'] = '05'
    if date['month'] == 'Jun': date['month'] = '06'
    if date['month'] == 'Jul': date['month'] = '07'
    if date['month'] == 'Aug': date['month'] = '08'
    if date['month'] == 'Sep': date['month'] = '09'
    if date['month'] == 'Oct': date['month'] = '10'
    if date['month'] == 'Nov': date['month'] = '11'
    if date['month'] == 'Dec': date['month'] = '12'
    
    
        
    topic = user.replace('@','.')
    
    log.info('topic: {}'.format(topic))
        
    idImage = date['day'] + '-' + date['month'] + '-' + date['year'] + '-' + date['hour']
    idImage = idImage.replace(':', '-')
    
    urlImageDownload, urlImageFirebase = saveImageFirebase(frame, idImage, topic)    
    
    print('urlImageDownload: {}'.format(urlImageDownload))
    print('urlImageFirebase: {}'.format(urlImageFirebase))
    
    statusConfig = utils.StatusConfig()
    
    if statusConfig.getUserLogin() != None:
    
    
        if tipoObjetoDetectado == 'person':
            tipoObjetoDetectado = 'Pessoa'

        elif tipoObjetoDetectado == 'dog':
            tipoObjetoDetectado = 'Cachorro'

        elif tipoObjetoDetectado == 'bike':
            tipoObjetoDetectado = 'Moto'

        elif tipoObjetoDetectado == 'car':
            tipoObjetoDetectado = 'Carro'
            

        
        title= 'Alerta: ' + tipoObjetoDetectado + ' detectado - ' + date['hour']
        
        body= tipoObjetoDetectado + ' na Região: ' + region + '- ' + date['hour'] + \
                ' - ' + date['day'] + '/' + date['month'] + '/' + date['year'] + '. Camera: ' + nameCam
        
        message = messaging.Message (    
        
            android = messaging.AndroidConfig(
                    ttl=datetime.timedelta(seconds=3600),
                    priority='normal',
                    notification=messaging.AndroidNotification(
                        icon='stock_ticker_update',
                        color='#f45342',
                        title=title,
                        body=body,
                    ),
                    
            ),
            
            notification = messaging.Notification(
                title= title, 
                body= body,
                image= urlImageDownload,
                
            ), 
            
            data = {
                'cameraName': nameCam, 
                'regionName': region, 
                'urlImageFirebase': 'https://firebasestorage.googleapis.com/v0/b/pvalarmes-3f7ee.appspot.com/o/foto_alerta.jpg?alt=media&token=755e0108-33f2-4cf2-8646-26c4498a37dc',
                'urlImageDownload': urlImageDownload,
                'id': idImage,
                'date': date['day'] + '/' + date['month'] + '/' + date['year'], 
                'hour': date['hour'], 
                'click_action': 'FLUTTER_NOTIFICATION_CLICK', 
                'objectDetected': tipoObjetoDetectado,
            },
                
            topic=topic,
        )
        # Send a message to the device corresponding to the provided

        # registration token.
        try:
            response = messaging.send(message)
        except error as e:
            print('Error: {}'.format(e))
        else:
            print('Successfully sent message:', response)
        
    else:
        log.error('sendAlertApp:: error: usuario nao configurado ou logado')
           



#envia alerta do portao virtual com imagem anexada ao email
def sendMailAlert(sender, recipients, subject, servidorEmail, user, frame, tipoObjetoDetectado, region, nameCam):
    
    #external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

    #log.info('InferenceCore::__init__:: External IP: {}'.format(external_ip))
    
    statusConfig = utils.StatusConfig() 
    emailConfig = statusConfig.getEmailConfig()
    
    status = False

    img_file = os.getcwd() + '/config/' + 'foto_alerta.jpg'

    try:
        cv.imwrite(img_file, frame)

    except OSError as error:
        log.critical('Erro ao salvar a foto: ' + str(error))
        return status
    else:
        log.info('Foto alarme salva')        


    try:
        img_file = open(img_file, 'rb').read()

    except OSError as error:
        log.critical('Erro ao anexar foto no email: ' + str(error))
        return status
    else:
        log.info('Foto anexada')

    data = utils.getDate()
    msg = MIMEMultipart()
    
    log.info('sendMailAlert:: tipoObjetoDetectado antes: {}'.format(tipoObjetoDetectado))

    if tipoObjetoDetectado == 'person':
        tipoObjetoDetectado = 'Pessoa'

    elif tipoObjetoDetectado == 'dog':
        tipoObjetoDetectado = 'Cachorro'

    elif tipoObjetoDetectado == 'bike':
        tipoObjetoDetectado = 'Moto'

    elif tipoObjetoDetectado == 'car':
        tipoObjetoDetectado = 'Carro'
        
    log.info('sendMailAlert:: tipoObjetoDetectado depois: {}'.format(tipoObjetoDetectado))
    
       
    if tipoObjetoDetectado == 'teste':
        msg['Subject'] = 'Portão Virtual - Teste de Email [ ' + sender + ' ] - ' + data['hour']
    else:        
        msg['Subject'] = subject + ' - ' + '"' + tipoObjetoDetectado + '"' + ' na ' + region  + ' [' + nameCam + '] ' + data['hour']
    
    msg['From'] = user
    msg['To'] = recipients

    text = MIMEText('"' + tipoObjetoDetectado + '"' + ' na ' + region +
                    '-  Detectado em ' + data['hour'] +
                    ' - ' + data['day'] + '/' + data['month'] + '/' + data['year'] + '\n \n')
    msg.attach(text)

    img_file = MIMEImage(img_file)
    msg.attach(img_file)


    password = utils.decrypt(emailConfig['password'])
    
    
    log.info('port: {:d}'.format(int(emailConfig['port'])))
    log.info('smtp: {:}'.format(emailConfig['smtp']))
    log.info('sender: {:}'.format(sender))
    log.info('user: {:}'.format(user))
    log.info('password: {:}'.format(password))
    log.info('password: {:}'.format(password))
    log.info(' ')     
        
    #if servidorEmail == 'Gmail':
    
    log.info('sendMailAlert:: servidorEmail: {} '.format(emailConfig['servidorEmail']))
        
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
        log.info('sendMailAlert:: Email de alerta enviado')
        status = True

    # elif servidorEmail == 'Outlook':
    
        # log.info('sendMailAlert:: usando Outlook') 
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
            # log.info('sendMailAlert:: Email de alerta enviado')
            # status = True
            
     
    
    
    return status


