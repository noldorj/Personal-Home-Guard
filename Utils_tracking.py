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

statusConfig = utils.StatusConfig() 

emailConfig = statusConfig.getEmailConfig()

#log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)
log.basicConfig(format="[ %(asctime)s] [%(levelname)s ] %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO, stream=sys.stdout)

def saveImageBox(frame, classe):

    print('classe: ' + classe)
    idFoto = len(os.listdir(os.getcwd() + '/dataset/training_set/' + classe)) + 1
    print('numero fotos: ' + str(idFoto))


    try:
        cv.imwrite(os.getcwd() + '/dataset/training_set/' + classe + '/' + classe + '.' + str(idFoto) + '.jpg',frame)
    except OSError as error:
        log.error("Erro em 'saveImageBox': " + str(error))
    else:
        log.info('saveImageBox - imagem salva')


def sendMail(subject, text):

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
        log.info("sendMail: Error: unable to send email" + str(e))

    else:
        log.info('sendMail: {} enviado.'.format(subject))
        status = True

    return status





#envia alerta do portao virtual com imagem anexada ao email
def sendMailAlert(sender, recipients, subject, port, smtp, user, frame, tipoObjetoDetectado, region):

    

    status = False

    img_file = os.getcwd() + '/' + 'foto_alerta.jpg'

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

    if tipoObjetoDetectado == 'person':
        tipoObjetoDetectado = 'Pessoa'

    elif tipoObjetoDetectado == 'dog':
        tipoObjetoDetectado = 'Cachorro'

    elif tipoObjetoDetectado == 'bike':
        tipoObjetoDetectado = 'Moto'

    elif tipoObjetoDetectado == 'car':
        tipoObjetoDetectado = 'Carro'

    msg['Subject'] = subject + ' - ' + '"' + tipoObjetoDetectado + '"' + ' na ' + region + '-' + data['hour']
    msg['From'] = sender
    msg['To'] = recipients

    text = MIMEText('"' + tipoObjetoDetectado + '"' + ' na ' + region + '-  Detectado em ' + data['hour'] + ' - ' + data['day'] + '/' + data['month'] + '/' + data['year'] )
    msg.attach(text)

    img_file = MIMEImage(img_file)
    msg.attach(img_file)


    password = utils.decrypt(emailConfig['password'])
    
    #smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj = smtplib.SMTP(smtp, int(port))
    try:
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(sender,password)
        smtpObj.send_message(msg)
        smtpObj.quit()

    except SMTPException as e:
        log.critical("Error: unable to send email" + str(e))

    else:
        log.info('Email de alerta enviado')
        status = True

    return status

#sendMailAlert('igorddf@gmail.com', 'igorddf@gmail.com', 'foto_alarme.png')

#def isMotionDetected(width, height, frame):
#    cv.CvtColor(frame, self.frame2gray, cv.CV_RGB2GRAY)
#
#    #Absdiff to get the difference between to the frames
#    cv.AbsDiff(self.frame1gray, self.frame2gray, self.res)
#
#    #Remove the noise and do the threshold
#    cv.Smooth(self.res, self.res, cv.CV_BLUR, 5,5)
#    element = cv.CreateStructuringElementEx(5*2+1, 5*2+1, 5, 5,  cv.CV_SHAPE_RECT)
#    cv.MorphologyEx(self.res, self.res, None, None, cv.CV_MOP_OPEN)
#    cv.MorphologyEx(self.res, self.res, None, None, cv.CV_MOP_CLOSE)
#    cv.Threshold(self.res, self.res, 10, 255, cv.CV_THRESH_BINARY_INV)
#
#
#    nb=0 #Will hold the number of black pixels
#
#    for y in range(height): #Iterate the hole image
#        for x in range(width):
#            if self.res[y,x] == 0.0: #If the pixel is black keep it
#                nb += 1
#    avg = (nb*100.0)/self.nb_pixels #Calculate the average of black pixel in the image
#    #print "Average: ",avg, "%\r",
#    if avg > self.ceil:#If over the ceil trigger the alarm
#        return True
#    else:
#        return False



