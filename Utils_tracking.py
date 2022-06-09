import os
import cv2 as cv
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
from smtplib import SMTPException
import utilsCore as utils
#import logging as log
import logging

import sys
import urllib.request
import time


import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import storage
from firebase_admin import db
import datetime

'''
log.root.setLevel(log.DEBUG)
log.basicConfig()


for handler in log.root.handlers[:]:
    log.root.removeHandler(handler)

log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, handlers=[log.FileHandler('config/pv.log', 'w', 'utf-8')])
log.getLogger('socketio').setLevel(log.ERROR)
log.getLogger('engineio').setLevel(log.ERROR)


#log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', filename='pv.log')
'''

log = logging.getLogger('pv-log')
log.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('config/pv.log', 'w', 'utf-8')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter("[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
log.addHandler(ch)
log.addHandler(fh)

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

'''
log.info('initFormConfig:: carregando Certificado Firebase')
try:
    credential = credentials.Certificate(cred)
except Exception as err:
    log.critical('initFormConfig:: Certificado não encontrado - Erro: {} '.format(err))
else:        
    log.info('initFormConfig:: Inicializando Firebase')

    try:
        firebase_app_pv = firebase_admin.initialize_app(credential, {'storageBucket': 'pvalarmes-3f7ee.appspot.com', 'databaseURL': 'https://pvalarmes-3f7ee-default-rtdb.firebaseio.com/'})
    except Exception as err:
        print('utilsTracking:: Erro ao inicializar o Firebase: {}'.format(err))            
    else:
        print('utilsTracking:: Firebase inicializado com sucesso')
'''


def saveImageFirebase(frame, idImage, user):
    
    bucket = None
    blob = None
    
    try:
        bucket = storage.bucket()
    except Exception as e:
        log.error('saveImageFirebase:: storage.bucket() error: {}'.format(e))
    else:
        log.info('saveImageFirebase:: storage.bucket() ok')
    
    img_file = os.getcwd() + '/config/alertas_app/' + idImage + '.jpg'
    
    log.info('saveImageFirebase:: Salvando foto local')
    try:
        cv.imwrite(img_file, frame)

    except OSError as error:
        log.critical('saveImageFirebase:: Erro ao salvar a foto: ' + str(error))
        img_file = os.getcwd() + '/config/disco_cheio.jpg'
        #return None, None, False
    else:
        log.info('saveImageFirebase:: Foto alarme app salva')        

       
    log.info('saveImageFirebase:: Salvando imagem no Firebase')
    if bucket is not None:
        try:
            blob = bucket.blob(user + '/' + idImage + '.jpg')        
            blob.upload_from_filename(img_file)        
            
        except firebase_admin.exceptions.FirebaseError as err:
            
            log.critical('saveImageFirebase:: Erro ao salvar imagem no Firebase')
            log.critical('saveImageFirebase:: Erro: {}'.formar(err))        
            return None, None, False
        else:
            log.info('saveImageFirebase:: Imagem salva no Firebase')
        
    try:
        blob.make_public() 
    except Exception as e:
        log.critical('saveImageFirebase:: Erro blob.make_public()')
    else:
        log.info('saveImageFirebase:: Blob.make_public ok')
    
    return blob.public_url, blob.name, True  

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


def sendMail(subject, message):

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
    msg['From'] = user
    msg['To'] = recipients

    text = MIMEText(message)

    msg.attach(text)

    smtpObj = smtplib.SMTP(smtp, int(port))
    try:
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(user,password)
        smtpObj.send_message(msg)
        smtpObj.quit()

    except SMTPException as e:
        log.error("sendMail: Error: unable to send email" + str(e))

    else:
        log.info('sendMail: {} enviado.'.format(subject))
        status = True

    return status


def savePvStatusDb(user, statusPv):

    #Estrutura para salvar no Realtime DAtabase 
    userId = user.replace('.','_')
    userId = userId.replace('@','_')    
    
    ref = db.reference('/users/' + userId + '/pvStatus')
    #users_ref = ref.child(idImageDb)

    statusMessage = False
    i = 1
    while statusMessage is False:
        log.info('savePvStatusDb:: Savando PvStatus tentativa [{}]'.format(i))   
        try:
            ref.set(statusPv)
        except Exception as e:
            log.critical('savePvStatusDb:: Erro salvar PvStatus Firebase DB')
            i = i + 1
            time.sleep(1)
        else:
            statusMessage = True
            i = 0


def saveStorageInfoDb(user, storageInfo):

    #Estrutura para salvar no Realtime DAtabase 
    userId = user.replace('.','_')
    userId = userId.replace('@','_')
    
    
    ref = db.reference('/users/' + userId + '/storageStatus')
    #users_ref = ref.child(idImageDb)

    log.info('saveStorageInfoDb:: Salvando PvStatus no Firebase DB')
    statusMessage = False
    i = 1
    while statusMessage is False:
        log.info('saveStorageInfoDb:: Savando PvStatus tentativa [{}]'.format(i))   
        try:
            ref.set(storageInfo)
        except Exception as e:
            log.critical('saveStorageInfoDb:: Erro salvar PvStatus Firebase DB')
            i = i + 1
            time.sleep(1)
        else:
            statusMessage = True
            i = 0




def sendStorageAlert(user, titleMsg, msg):
    log.info('sendStorageAlert::')
    
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
    
    statusConfig = utils.StatusConfig()
    
    

    title = titleMsg
            
    body = msg
            
    message = messaging.Message (    
    
        android = messaging.AndroidConfig(
                ttl=datetime.timedelta(seconds=3600),
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='stock_ticker_update',
                    color='#f45342',
                    title=title,
                    body=body,
                    default_sound='True',
                    tag='PV-Alertas',
                    default_vibrate_timings='True',
                    default_light_settings='True',
                   
                ),
                
        ),
        
        notification = messaging.Notification(
            title= title, 
            body= body,
            #image= urlImageDownload,
            
        ), 
        
        data = {           
            'date': date['day'] + '/' + date['month'] + '/' + date['year'], 
            'hour': date['hour'], 
            'click_action': 'FLUTTER_NOTIFICATION_CLICK',             
        },
            
        topic=topic,
    )
    # Send a message to the device corresponding to the provided

    # registration token.
    log.info('sendStorageAlert:: Alerta Storage para App')
    statusMessage = False
    i = 1
    while statusMessage is False:
        log.info('sendStorageAlert:: Enviando alerta storage App [{}]'.format(i))
        try:
            response = messaging.send(message)
        except Exception as e:
            log.critical('sendStorageAlert:: Erro ao enviar alerta storage App: {}'.format(e))            
            i = i+1
            time.sleep(3)
        else:
            log.info('sendStorageAlert:: Alerta storage enviado com sucesso: {}'.format(response))            
            statusMessage = True
            i = 0
    
   
    

def sendAlertApp(user, frame, tipoObjetoDetectado, region, nameCam):

    log.info('sendAlertApp::')
    
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
    
    
    log.info('sendAlertApp:: Salvando imagem Firebase')
    
    urlImageDownload, urlImageFirebase, status = saveImageFirebase(frame, idImage, topic)
        
    
    #print('urlImageDownload: {}'.format(urlImageDownload))
    #print('urlImageFirebase: {}'.format(urlImageFirebase))
    
    statusConfig = utils.StatusConfig()
    
    if statusConfig.getUserLogin() != None:    
    
        if tipoObjetoDetectado == 'person':
            tipoObjetoDetectado = 'Pessoa'

        elif tipoObjetoDetectado == 'dog':
            tipoObjetoDetectado = 'Cachorro'

        elif tipoObjetoDetectado == 'bicycle' or tipoObjetoDetectado == 'motorcycle':
            tipoObjetoDetectado = 'Moto'

        elif tipoObjetoDetectado == 'car':
            tipoObjetoDetectado = 'Carro'
            

        
        title= 'Alerta: ' + tipoObjetoDetectado + ' detectado - ' + date['hour']
        
        body= tipoObjetoDetectado + ' na Região: ' + region + '- ' + date['hour'] + \
                ' - ' + date['day'] + '/' + date['month'] + '/' + date['year'] + '. Camera: ' + nameCam
                
         
        #Estrutura para salvar no Realtime DAtabase 
        emailId = topic.replace('.','_')        
        idImageDb = idImage.replace('.','_')
        #print('idImageDb: {}'.format(idImageDb))
        
        ref = db.reference('/users/' + emailId + '/alerts/' + date['year'] + '/' + date['month'] + '/' + date['day'] + '/' + date['hourOnly'])
        users_ref = ref.child(idImageDb)
        
        users_ref.set(            
            {
                'cameraName': nameCam, 
                'regionName': region, 
                'urlImageFirebase': urlImageFirebase,
                'urlImageDownload': urlImageDownload,
                'id': idImageDb,
                'date': date['day'] + '/' + date['month'] + '/' + date['year'], 
                'hour': date['hour'], 
                'click_action': 'FLUTTER_NOTIFICATION_CLICK', 
                'objectDetected': tipoObjetoDetectado,
                'textAlert': body,
            }
        )        
        
        message = messaging.Message (    
        
            android = messaging.AndroidConfig(
                    ttl=datetime.timedelta(seconds=3600),
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='stock_ticker_update',
                        color='#f45342',
                        title=title,
                        body=body,
                        default_sound='True',
                        tag='PV-Alertas',
                        default_vibrate_timings='True',
                        default_light_settings='True',
                       
                    ),
                    
            ),
            
            notification = messaging.Notification(
                title = title, 
                body = body,
                image = urlImageDownload,
                
            ), 
            
            data = {
                'cameraName': nameCam, 
                'regionName': region, 
                'urlImageFirebase': urlImageFirebase,
                'urlImageDownload': urlImageDownload,
                'id': idImage,
                'date': date['day'] + '/' + date['month'] + '/' + date['year'], 
                'hour': date['hour'], 
                'click_action': 'FLUTTER_NOTIFICATION_CLICK', 
                'objectDetected': tipoObjetoDetectado,
            },
                
            topic=topic,
            
            apns = messaging.APNSConfig(
                headers={'apns-priority': '10'},
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=title,                           
                            body=body,                            
                            custom_data = {
                                            'cameraName': nameCam, 
                                            'regionName': region, 
                                            'urlImageFirebase': urlImageFirebase,
                                            'urlImageDownload': urlImageDownload,
                                            'id': idImage,
                                            'date': date['day'] + '/' + date['month'] + '/' + date['year'], 
                                            'hour': date['hour'], 
                                            'click_action': 'FLUTTER_NOTIFICATION_CLICK', 
                                            'objectDetected': tipoObjetoDetectado,
                                        },                            
                        ),
                        sound="default",
                        content_available=1,
                        custom_data = {
                'cameraName': nameCam, 
                'regionName': region, 
                'urlImageFirebase': urlImageFirebase,
                'urlImageDownload': urlImageDownload,
                'id': idImage,
                'date': date['day'] + '/' + date['month'] + '/' + date['year'], 
                'hour': date['hour'], 
                'click_action': 'FLUTTER_NOTIFICATION_CLICK', 
                'objectDetected': tipoObjetoDetectado,
            }
                        
                    ),
                ),
                fcm_options = messaging.APNSFCMOptions(image=urlImageDownload),               
            ), 
            
        )
        # Send a message to the device corresponding to the provided

        # registration token.
        log.info('sendAlertApp:: Enviando mensagem para App via Cloud Message')
        statusMessage = False
        i = 1
        while statusMessage is False:
            log.info('sendAlertApp:: Enviando alerta App [{}]'.format(i))
            try:
                response = messaging.send(message)
            except Exception as e:
                log.critical('sendAlertApp:: Erro ao enviar alerta: {}'.format(e))            
                i = i+1
                time.sleep(3)
            else:
                log.info('sendAlertApp:: Alerta enviado com sucesso: {}'.format(response))            
                statusMessage = True
                i = 0
        
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

    elif tipoObjetoDetectado == 'bicycle' or tipoObjetoDetectado == 'motorcycle':
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
    
    
    # log.info('port: {:d}'.format(int(emailConfig['port'])))
    # log.info('smtp: {:}'.format(emailConfig['smtp']))
    # log.info('sender: {:}'.format(sender))
    # log.info('user: {:}'.format(user))
    # log.info('password: {:}'.format(password))
    # log.info('password: {:}'.format(password))
    # log.info(' ')     
        
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


