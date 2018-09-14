import os
import cv2 as cv
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
from smtplib import SMTPException


def saveImageBox(frame, classe):


    idFoto = len(os.listdir(os.getcwd() + 'dataset/training_set/' + classe))


    try:
        cv.imwrite(os.getcwd() + '/dataset/training_set/' + classe + '/' + classe + '.' + str(idFoto) + '.jpg',frame)
    except OSError as error:
        print("Erro em 'saveImageBox': " + str(error))
    else:
        print('saveImageBox - imagem salva')


#envia alerta do portao virtual com imagem anexada ao email
def sendMailAlert(sender, recipients, frame):

    status = False



    img_file = os.getcwd() + '/' + 'foto_alerta.jpg'

    try:
        cv.imwrite(img_file, frame)

    except OSError as error:
        print('Erro ao salvar a foto: ' + str(error))
        return status
    else:
        print('Foto alarme salva')


    try:
        img_file = open(img_file, 'rb').read()

    except OSError as error:
        print('Erro ao anexar foto no email: ' + str(error))
        return status
    else:
        print('Foto anexada')
#
#    ret, image = cv.imencode('.jpg', frame)


    msg = MIMEMultipart()
    msg['Subject'] = 'Alarme PV - Foto'
    msg['From'] = sender
    msg['To'] = recipients

    text = MIMEText("Alarme - Objecto detectado")
    msg.attach(text)

    img_file = MIMEImage(img_file)
    msg.attach(img_file)


    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login(sender,'budega656')
        smtpObj.send_message(msg)
        smtpObj.quit()

    except SMTPException as e:
        print("Error: unable to send email" + str(e))

    else:
        print('Email de alerta enviado')
        status = True

    return status

#sendMailAlert('igorddf@gmail.com', 'igorddf@gmail.com', 'foto_alarme.png')




