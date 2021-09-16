from PyQt5.QtWidgets import QWidget, QDialog 
from PyQt5 import QtCore 
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
import utilsCore as utils
from utilsCore import StatusConfig
from camRunTime import CamRunTime
from formLogin import *
import logging as log
import secrets
import psutil
#from inferenceCore import *
import winshell
from win32com.client import Dispatch
import getpass
import os


from checkLicence.sendingData import checkLoginPv 
from checkLicence.sendingData import changePasswdPv 
from checkLicence.sendingData import checkSessionPv
from checkLicence.sendingData import forgotPasswordPv 

class FormLogin(QDialog):

    statusConfig = None
    camRunTime = None
    
    
    logged = False   
    #setBackStatusConfigCamRunTime = pyqtSignal(StatusConfig, CamRunTime)
    updateStatusLogin = pyqtSignal(bool)

    def __init__(self, camRunTimeP, statusConfigP, parent=None ):
        log.info('initGuiLogin:: __init__')

        super(FormLogin, self).__init__(parent)
        #Dialog = QtWidgets.QDialog()
        self.uiLogin = Ui_Dialog()
        self.uiLogin.setupUi(self)        
        
        

        #self.uiLogin.setWindowModality(QtCore.Qt.ApplicationModal)

        self.statusConfig = statusConfigP
        self.camRunTime = camRunTimeP

        log.info('initGuiLogin:: dataLogin: ' + self.statusConfig.dataLogin.get('user'))

        if self.statusConfig.dataLogin.get('autoStart') == 'True':
            self.uiLogin.checkBoxLoginAutoStart.setCheckState(True)
        else:
            self.uiLogin.checkBoxLoginAutoStart.setCheckState(False)
        
        if self.statusConfig.dataLogin.get('salvarLogin') == 'True':
            
            self.uiLogin.txtEmail.setText(self.statusConfig.dataLogin.get('user'))
            
            passwd = utils.decrypt(self.statusConfig.dataLogin.get('passwd')) 
            
            self.uiLogin.txtPasswd.setText(passwd)
            self.uiLogin.checkBoxSalvarLogin.setCheckState(True)

        
        self.uiLogin.btnLogin.clicked.connect(self.btnLogin)
        self.uiLogin.btnExit.clicked.connect(self.btnExit)        
        self.uiLogin.btnEsqueciSenha.clicked.connect(self.btnEsqueciSenha)
        self.uiLogin.checkBoxSalvarLogin.stateChanged.connect(self.checkBoxSalvarLogin)
        self.uiLogin.checkBoxLoginAutomatico.stateChanged.connect(self.checkBoxLoginAutomatico)
        self.uiLogin.checkBoxLoginAutoStart.stateChanged.connect(self.checkBoxLoginAutoStart)
        self.uiLogin.checkBoxAtalhoDesktop.stateChanged.connect(self.checkBoxAtalhoDesktop)
        
        self.uiLogin.btnAlterarSenha.clicked.connect(self.btnAlterarSenha)
        
        

    
    def setEnv(self, camRunTimeP, statusConfigP):
        log.info('setEnv login')
        self.statusConfig = statusConfigP
        self.camRunTime = camRunTimeP
       
    def isLogged(self):
        log.info('isLogged')
        return self.logged    

    def checkBoxLoginAutoStart(self, state):     
        
        
        if self.camRunTime.OS_PLATFORM == 'windows':
            ATALHO_PATH = 'PortaoVirtual.lnk'
            USER_NAME = getpass.getuser()       
            ROOT_PATH = os.path.splitdrive(os.environ['WINDIR'])[0]    
            AUTO_START_PATH = ROOT_PATH + '/Users/' + USER_NAME + '/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup' 
            
        
        if state == 0:
            
            log.info('Auto start login off')
            self.statusConfig.setLoginAutoStart('False')
            
            try:
                if os.path.exists(AUTO_START_PATH + '/' + ATALHO_PATH):
                    os.remove(AUTO_START_PATH + '/' + ATALHO_PATH)
                else:
                    log.info("Atalho na pasta de Inicialização do sistema não existe")
            except OSError as error:
                log.error('checkBoxLoginAutoStart:: error: {}'.formart(error))
            else:
                log.info('checkBoxLoginAutoStart:: Auto Start off')

        elif (state == 1 or state == 2):
            
            log.info('Auto start login On')
            self.statusConfig.setLoginAutoStart('True')  
            
            try:
            
                if not os.path.exists(AUTO_START_PATH + '/' + ATALHO_PATH):              
                    
                    path = os.path.join(AUTO_START_PATH, "PortaoVirtual.lnk")
                    target = os.getcwd() + '/' + 'pv.exe'
                    wDir = os.getcwd()
                    #icon = r"P:\Media\Media Player Classic\mplayerc.exe"
                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(path)
                    shortcut.Targetpath = target
                    shortcut.WorkingDirectory = wDir
                    #shortcut.IconLocation = icon
                    shortcut.save()
                    #print('AUTO_START_PATH: {}'.format(AUTO_START_PATH))
                    #shutil.copy2(ATALHO_PATH, AUTO_START_PATH) # complete target filename given
                    
            except OSError as err:
                log.error('checkBoxLoginAutoStart:: error: {}'.formart(error))              
            
            else:
                log.info('checkBoxLoginAutoStart:: Auto Start On')

    def checkBoxAtalhoDesktop(self, state):
    
        log.info('checkBoxAtalhoDesktop:: Removendo atalho desktop')
        desktop = winshell.desktop()
        path = os.path.join(desktop, "PortaoVirtual.lnk")
        
        if state == 0:
        
            self.statusConfig.setAtalhoDesktop('False')
            if os.path.exists(path):
                os.remove(path)
            else:
                log.info("checkBoxAtalhoDesktop:: Atalho no Desktop já foi removido")
            
            self.statusConfig.setAtalhoDesktop('False')

        elif (state == 1 or state == 2):                    
            
            target = os.getcwd() + '/' + 'pv.exe'
            wDir = os.getcwd()            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = wDir
            #shortcut.IconLocation = icon
            shortcut.save()                        
            self.statusConfig.setAtalhoDesktop('True')
            log.info('checkBoxAtalhoDesktop:: Atalho desktop criado')
    
    def checkBoxLoginAutomatico(self, state):
        #global LOGIN_AUTOMATICO, self.statusConfig        
        log.info('checkBoxLoginAutomatico')
        
        if state == 0:
            
            log.info('checkBoxLoginAutomatico:: Login automatico off')
            self.statusConfig.setLoginAutomatico('False')
            self.camRunTime.LOGIN_AUTOMATICO = False


        elif (state == 1 or state == 2):
            
            log.info('checkBoxLoginAutomatico:: Login automatico on')
            self.statusConfig.setLoginAutomatico('True')
            self.camRunTime.LOGIN_AUTOMATICO = True 

    def checkBoxSalvarLogin(self, state):
        #global fernetKey, statusConfig        
        
        if state == 0:
            
            log.info('salvar login off')
            self.statusConfig.addLoginConfig(self.uiLogin.txtEmail.text(),
                                        '',
                                        'False',
                                        self.statusConfig.dataLogin['loginAutomatico'],
                                        self.statusConfig.dataLogin['autoStart']
                                        )
            log.info('Salvar Login desligado')

        elif (state == 1 or state == 2):
            

            passEncrypted = utils.encrypt(self.uiLogin.txtPasswd.text())        
            
            self.statusConfig.addLoginConfig(self.uiLogin.txtEmail.text(),
                                        passEncrypted,
                                        'True',
                                        self.statusConfig.dataLogin['loginAutomatico'],
                                        self.statusConfig.dataLogin['autoStart'])
            
            log.info('Salvar Login ligado')

    def btnExit(self):
        #global statusLicence, init_video
        log.info('Login Cancelado')
        self.camRunTime.statusLicence = False
        self.camRunTime.init_video = False
        self.updateStatusLogin.emit(False)
        utils.stopWatchDog()
        
        #event.accept()
        self.close()
        #self.windowLogin.close()

    def btnAlterarSenha(self):
        #global uiLogin, statusPasswd

        log.info("Alterando a senha")
        
        conexao = utils.checkInternetAccess()

        if conexao:    

            if (self.uiLogin.txtNovaSenha.text() == self.uiLogin.txtNovaSenha2.text()):
            
                self.camRunTime.login = {'user':utils.encrypt(self.uiLogin.txtEmail_minhaConta.text()), 'passwd':utils.encrypt(self.uiLogin.txtNovaSenha.text()), 'token':utils.encrypt(self.camRunTime.token)} 
                

                self.camRunTime.statusPasswd, self.camRunTime.error = changePasswdPv(self.camRunTime.login)
                
                if self.camRunTime.statusPasswd:
                    
                    log.info("formLogin::btnAlterarSenha:: Senha alterada com sucesso")
                    self.uiLogin.lblStatus.setText("Senha alterada com sucesso")
                
                else:

                    #se o servidor estiver fora do ar - libera acesso ao sistema 
                    if self.camRunTime.error == "conexao":
                        log.warning("Erro de conexão com o servidor")
                        self.uiLogin.lblStatus.setText("Erro de conexão com o servidor")

                    elif self.camRunTime.error == "login":
                        log.warning("Usuario invalido")
                        self.uiLogin.lblStatus.setText("Usuário ou senha inválida. Tente novamente")
        else:
            log.info("Erro de conexao com a Internet")
            self.uiLogin.lblStatus.setText("Cheque sua conexão com a Internet por favor e tente mais tarde")

    def btnEsqueciSenha(self):
        #global self.uiLogin, conexao

        log.info('btnEsqueciSenha:: Checando conexão com a Internet')
        self.uiLogin.lblStatus.setText("Checando conexão com a Internet")

        self.camRunTime.conexao = utils.checkInternetAccess()

        if self.camRunTime.conexao:    
        
            log.info('btnEsqueciSenha:: Checando licença no servidor - Por favor aguarde')
            #self.uiLogin.lblStatus.setText("Conectando com o servidor")
            status, error = forgotPasswordPv(self.uiLogin.txtEmail.text()) 
            
            if error == "conexao":
                log.warning("btnEsqueciSenha:: Erro de conexão com o servidor")
                self.uiLogin.lblStatus.setText("Error de conexão com o servidor - tente novamente")

            elif error == "login":

                log.warning("Usuario invalido")
                self.uiLogin.lblStatus.setText("Usuário desconhecido.")

            if status:
                log.warning("Email de recuperação de senha enviado")
                self.uiLogin.lblStatus.setText("Email de recuperação de senha enviado")

        else:
             
            log.warning("Erro de conexao com a Internet")
            self.uiLogin.lblStatus.setText("Cheque sua conexão com a Internet.")

    def btnLogin(self):

        #checando licenca de usuario no servidor
        #global init_video, statusLicence, self.uiLogin, conexao, login 

        log.info('btnLogin:: Checando conexão com a Internet')
        self.uiLogin.lblStatus.setText("Checando conexão com a Internet")

        self.camRunTime.conexao = utils.checkInternetAccess()
        #conexao = True

        if self.camRunTime.conexao:    
        
            log.info('btnLogin:: Checando licença no servidor - Por favor aguarde')
            #print('Checando licença no servidor - Por favor aguarde')
            self.uiLogin.lblStatus.setText("Conectando com o servidor")
            
            self.camRunTime.login = {'user':utils.encrypt(self.uiLogin.txtEmail.text()), 'passwd':utils.encrypt(self.uiLogin.txtPasswd.text()), 'token':utils.encrypt(self.camRunTime.token)}
            #log.info('btnLogin::TOKEN: {}'.format(self.camRunTime.login.get('token').decode()))
            self.statusConfig.setUserNameLoginConfig(self.uiLogin.txtEmail.text())
            
            self.camRunTime.statusLicence, self.camRunTime.error  = checkLoginPv(self.camRunTime.login) 
            #statusLicence = True ## testando apenas IJF
            

            if self.camRunTime.statusLicence:
                
                #print("Usuario logado")
                self.camRunTime.init_video = True 
                self.camRunTime.statusLicence = True
                #utils.initWatchDog()   
                self.logged = True
                #print('initLogin statusLicence: ' + str(self.camRunTime.statusLicence))
                #self.setBackStatusConfigCamRunTime.emit(self.statusConfig, self.camRunTime)
                self.updateStatusLogin.emit(True)
                self.hide()
                #self.close()
                #windowLogin.close()
            
            else:

                #se o servidor estiver fora do ar - libera acesso ao sistema 
                if self.camRunTime.error == "conexao":
                    #print("Erro de conexão com o servidor")
                    self.camRunTime.init_video = True
                    self.camRunTime.statusLicence = True
                    self.updateStatusLogin.emit(True)
                    log.warning("Liberando acesso")
                    #event.accept()            
                    #self.setBackStatusConfigCamRunTime.emit(self.statusConfig, self.camRunTime)
                    self.close()
                    #windowLogin.close()

                elif self.camRunTime.error == "login":

                    self.camRunTime.init_video = False
                    self.camRunTime.statusLicence = False
                    self.updateStatusLogin.emit(False)
                    log.warning("Usuario invalido")
                    print("Usuario invalido")
                    self.uiLogin.lblStatus.setText("Usuário ou senha inválida. Tente novamente")

        else:

            log.info("Erro de conexao com a Internet")
            self.uiLogin.lblStatus.setText("Cheque sua conexão com a Internet por favor e tente mais tarde")

        #self.setBackStatusConfigCamRunTime.emit(self.statusConfig, self.camRunTime)
        

        #windowLogin.show()
        #app.exec_()


    def closeEvent(self, event):
        self.camRunTime.statusLicence = False
        self.camRunTime.init_video = False
        self.updateStatusLogin.emit(False)
        utils.stopWatchDog()
        #event.accept()            
        log.info('close formLogin')

