#
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
from smtplib import SMTPException
import logging as log
import sys

log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)


#Envio de emails para funcoes como esqueceu a senha

def sendMailForgotPasswd(sender, recipients, subject, port, smtp, user, password, userPassword):

    status = False

    #data = utils.getDate()
    msg = MIMEMultipart()

    msg['Subject'] = subject 
    msg['From'] = sender
    msg['To'] = recipients

    text = MIMEText('Sua senha atual é: "' + userPassword + '. Recomendamos que você altere a senha o quanto antes."' )
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
