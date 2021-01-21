# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'formTermos.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogTermosUso(object):
    def setupUi(self, DialogTermosUso):
        DialogTermosUso.setObjectName("DialogTermosUso")
        DialogTermosUso.setWindowModality(QtCore.Qt.WindowModal)
        DialogTermosUso.resize(718, 711)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(DialogTermosUso)
        self.plainTextEdit.setGeometry(QtCore.QRect(3, 260, 711, 361))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.checkBoxAceite = QtWidgets.QCheckBox(DialogTermosUso)
        self.checkBoxAceite.setGeometry(QtCore.QRect(13, 630, 261, 23))
        self.checkBoxAceite.setObjectName("checkBoxAceite")
        self.checkBoxNaoAceite = QtWidgets.QCheckBox(DialogTermosUso)
        self.checkBoxNaoAceite.setGeometry(QtCore.QRect(323, 630, 291, 23))
        self.checkBoxNaoAceite.setObjectName("checkBoxNaoAceite")
        self.plainTextEdit_2 = QtWidgets.QPlainTextEdit(DialogTermosUso)
        self.plainTextEdit_2.setGeometry(QtCore.QRect(3, 70, 711, 181))
        self.plainTextEdit_2.setObjectName("plainTextEdit_2")
        self.label = QtWidgets.QLabel(DialogTermosUso)
        self.label.setGeometry(QtCore.QRect(190, 10, 311, 17))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.btnOk = QtWidgets.QPushButton(DialogTermosUso)
        self.btnOk.setGeometry(QtCore.QRect(260, 670, 121, 25))
        self.btnOk.setObjectName("btnOk")

        self.retranslateUi(DialogTermosUso)
        QtCore.QMetaObject.connectSlotsByName(DialogTermosUso)

    def retranslateUi(self, DialogTermosUso):
        _translate = QtCore.QCoreApplication.translate
        DialogTermosUso.setWindowTitle(_translate("DialogTermosUso", "Termos de Uso - Portão Virtual"))
        self.plainTextEdit.setPlainText(_translate("DialogTermosUso", "TERMOS DE USO \n"
"SISTEMA PORTÃO VIRTUAL - SOFTWARE E APLICATIVO \n"
"\n"
"Contrato de Registro do Usuário do Portão Virtual\n"
"Aviso:\n"
"Este Contrato de Registro do Usuário (o \"Contrato\") regulamenta o uso do Software e Aplicativo Portão Virtual (o “Aplicativo”), da PORTÃO VIRTUAL LTDA, a saber, \"PORTÃO VIRTUAL\". Revise este Contrato antes de se registrar, especialmente as cláusulas de exclusão e limitação das responsabilidades da PORTÃO VIRTUAL . Ao concluir o processo de registro, considera-se que você concorda e aceita este Contrato. Se tiver alguma dúvida, entre em contato conosco através do email contato@portaovirtual.com.br \n"
"Registro de Usuário\n"
"O Aplicativo PORTÃO VIRTUAL destina-se unicamente a pessoas elegíveis de acordo com a lei. Ao acessar ou usar o Aplicativo PORTÃO VIRTUAL  você revela e garante que tem elegibilidade para utilizar seus recursos ou serviços.\n"
"Durante o processo de registro, para a criação de uma conta, você deverá fornecer certas informações e estabelecer um nome de usuário e uma senha, concordando em fornecer informações verídicas. A PORTÃO VIRTUAL LTDA reserva-se o direito, a seu exclusivo critério, de suspender ou encerrar sua conta no momento em que for constatado que suas informações são incompletas ou com sinais de fraude.\n"
"Após a conclusão do processo de registro, você possuirá uma conta (login e senha) que é considerada um certificado para acessar o sistema PORTÃO VIRTUAL, assim podendo receber atualizações dos softwares e aplicativos, funcionalidades extras e acessar o nosso serviço de suporte.\n"
"\n"
"Você é inteiramente responsável por manter a confidencialidade das informações da conta, por exemplo, redefinindo sua senha periodicamente, limitando o acesso a seus dispositivos, ou fazendo uso de outros métodos eficazes. Você não deverá transferir sua conta e senha para outros indivíduos de qualquer maneira.  \n"
"Regras de Uso\n"
"Para utilizar adequadamente o sistema PORTÃO VIRTUAL, seja o aplicativo ou o software, você precisará de uma conexão estável com a Internet, justamente para receber os avisos de alertas de detecção de pessoas ou carros. A PORTÃO VIRTUAL LTDA não se responsabiliza por erros de conexão, interrupções na internet, ou interrupções de serviços de email de terceiros como Gmail do Google, ou Outlook da Microsoft. \n"
"A PORTÃO VIRTUAL LTDA também não se responsabiliza pelo computador, notebook, ou celular utilizado. A manutenção destes equipamentos, para o correto funcionamento do sistema PORTÃO VIRTUAL é de responsabilidade única e exclusiva do usuário. \n"
"Falhas nas detecções de objetos, carros ou pessoas pelo sistema PORTÃO VIRTUAL podem ocorrer devido a vários fatores, erros de comunicação da rede sem fio ou cabeada do usuário, erros de processamento ou estabilidade do sistema operacional do computador/notebook do usuário, ou fatores como iluminação e resolução da câmera do usuário. Devido à característica destes fatores não terem relação com o sistema PORTÃO VIRTUAL, a PORTÃO VIRTUAL LTDA  não se responsabiliza por estas falhas, e o que estas falhas podem ocasionar. \n"
"Vale ressaltar que o sistema PORTÃO VIRTUAL é uma ferramenta de segurança adicional e complementa as boas práticas de segurança residencial e comercial. A PORTÃO VIRTUAL LTDA não se responsabiliza por perdas monetárias, danos comerciais, ou qualquer outro tipo de prejuízo por eventuais falhas dos componentes eletrônicos utilizados pelo usuário, como câmeras, cabeamento, computadores, rede local e conexão com a internet, e eventuais falhas do PORTÃO VIRTUAL. \n"
"    Você reconhece que não poderá utilizar o sistema PORTÃO VIRTUAL para atividades ilegais, ilícitas ou imorais, e que ficará responsável pelas imagens armazenadas, visto que a PORTÃO VIRTUAL LTDA não armazena nenhuma informação relacionada aos avisos por email, vídeos obtidos pelas câmeras configuradas, e informações de configuração. Apenas as informações de cadastro do usuário são armazenadas em nossos servidores, justamente para prover o acesso via login e senha. \n"
"    A PORTÃO VIRTUAL LTDA reserva-se o direito de suspender suas atividades, suspender o suporte e venda do sistema PORTÃO VIRTUAL, sem aviso prévio. Apesar disso, pela característica do software, o sistema já adquirido poderá ser utilizado de acordo com os termos de licença de aquisição, mas sem updates e atualizações de novas versões, ou correções de bugs existentes. \n"
"Propriedade Intelectual\n"
"Todos os textos, imagens, logotipos, e código fonte do software e aplicativo PORTÃO VIRTUAL, estão protegidos por este termo de propriedade intelectual, direitos autorais, marcas registradas e patentes. \n"
"A PORTÃO VIRTUAL concede a você uma licença de uso do software ou aplicativo, através da compra da licença diretamente com a PORTÃO VIRTUAL ou através de parceiros comerciais. Não é permitida a cópia, reprodução, revenda de todo do software ou aplicativo, seja para fins comerciais ou não.\n"
"Proteção de Privacidade\n"
"    A PORTÃO VIRTUAL LTDA não armazena, coleta, ou tem acesso aos vídeos gravados pelo sistema PORTÃO VIRTUAL. A única informação armazenada em nossos servidores são as informações de aquisição pelo cliente no ato da compra da licença, e por consequência, as informações de login e senha, que são enviadas de forma criptografada. \n"
"    Todos os alertas gerados por email, são enviados com o próprio email que você configurou no sistema PORTÃO VIRTUAL. \n"
"    A PORTÃO VIRTUAL LTDA não se responsabiliza por ataques cibernéticos, perda ou roubo de informações efetuados por terceiros aos equipamentos utilizados para operar o sistema, como notebooks, celulares, rede local, e acesso à internet. \n"
"    Se você perceber qualquer atividade suspeita, ilícita, ou de roubo de informações e queira cancelar sua conta, basta entrar em contato através do email contato@portaovirtual.com.br que faremos o cancelamento da conta o mais rápido possível. \n"
"    A responsabilidade por manter a segurança dos notebooks, computadores, celulares ou qualquer tipo de equipamento utilizado para o sistema PORTÃO VIRTUAL, é exclusiva do usuário. Também é responsabilidade do usuário garantir quem utilizará o sistema através das informações de login e senha. \n"
"Inadimplência\n"
"Você concorda que a PORTÃO VIRTUAL poderá, a seu exclusivo critério e sem aviso prévio, suspender ou encerrar seu acesso ao Aplicativo PORTÃO VIRTUAL , bloquear acesso futuro, investigar e atribuir responsabilidade legal, ou tomar quaisquer ações legais contra você, se a PORTÃO VIRTUAL determinar que violou este Contrato ou as leis e regulamentos aplicáveis. Você também concorda em afiançar todas as perdas que a PORTÃO VIRTUAL ou terceiros sofram como resultado de tal violação. \n"
"Notificação\n"
"O anúncio de novas versões, contendo novas funcionalidades ou correções de defeitos (bugs), será feito através de nossos canais oficiais ( www.portaovirtual.com.br ) e por email para os clientes registrados. Você concorda em receber estas notificações por email ou por telefone previamente cadastrados e autorizados. \n"
"É de sua responsabilidade manter atualizado o sistema PORTÃO VIRTUAL assim que receber tais notificações. \n"
"O Contrato deverá ser interpretado e entendido de acordo com as leis brasileiras e regido por elas, excluindo-se quaisquer outras leis. O Foro de São Paulo - SP, domicílio da PORTÃO VIRTUAL, terá jurisdição exclusiva para presidir ao julgamento de qualquer contestação nos termos deste Contrato.\n"
"O Contrato poderá ser modificado de tempos em tempos e todas as atualizações serão publicadas neste manual. O uso continuado do sistema PORTÃO VIRTUAL  após a publicação de alterações implica que você concorda e aceita todas as alterações. Você reconhece que a versão atualizada do Contrato será aplicável em caso de disputa.\n"
"Em caso de dúvidas, entre em contato conosco pelo website www.intelbras.com.br.   \n"
"Compartilhamento de Informações Pessoais\n"
"\n"
"A PORTÃO VIRTUAL não divulgará suas informações pessoais, a menos que (i) tenha seu consentimento prévio por escrito; (ii) esteja de acordo com as leis e regulamentos aplicáveis, ou exigidas pelas autoridades; (iii) seja obrigada por decisão judicial; (iv) esteja de acordo com os termos da Política; (v) seja essencial para a proteção dos interesses legítimos da PORTÃO VIRTUAL.\n"
"A PORTÃO VIRTUAL poderá permitir que seus funcionários acessem seus dados pessoais em ocasiões específicas com base na necessidade de conhecimento, e assegurará que seus funcionários cumpram com as obrigações no mesmo nível estabelecido pela Política.\n"
"A PORTÃO VIRTUAL LTDA tem o objetivo de prover SEGURANÇA, por isso, nossa política é de não compartilhar seus dados de cadastro com empresas terceiras sem sua autorização prévia por escrito (email). Caso surja essa necessidade, para melhorias do próprio sistema PORTÃO VIRTUAL, um comunicado será enviado descrevendo exatamente quais dados seriam compartilhados e quais seriam os objetivos.  \n"
"\n"
"Método de Contato\n"
"Se você suspeitar de que suas informações pessoais estejam sendo coletadas, usadas ou infringidas ilegalmente de qualquer maneira, entre em contato conosco através do email contato@portaovirtual.com.br  \n"
""))
        self.checkBoxAceite.setText(_translate("DialogTermosUso", "Li e concordo com o termo de uso"))
        self.checkBoxNaoAceite.setText(_translate("DialogTermosUso", "Não concordo, sair do sistema"))
        self.plainTextEdit_2.setPlainText(_translate("DialogTermosUso", "Considerações Importantes ! \n"
"\n"
"1. Configure o Windows 10 para não hibernar/desligar\n"
"\n"
"2. O Portão Virtual exige uma conexão estável com a Internet\n"
"\n"
"3. Configure o Windows Defender para não bloquear o Portão Virtual - Acesse seu Manual ! \n"
"\n"
"4. Cheque se sua câmera IP está instalada corretamente em sua rede local"))
        self.label.setText(_translate("DialogTermosUso", "Bem-vindo ao Portão Virtual !"))
        self.btnOk.setText(_translate("DialogTermosUso", "Continuar"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DialogTermosUso = QtWidgets.QDialog()
    ui = Ui_DialogTermosUso()
    ui.setupUi(DialogTermosUso)
    DialogTermosUso.show()
    sys.exit(app.exec_())

