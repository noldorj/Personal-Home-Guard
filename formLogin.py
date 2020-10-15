# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'formLogin.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_formLogin(object):
    def setupUi(self, formLogin):
        formLogin.setObjectName("formLogin")
        formLogin.resize(572, 241)
        formLogin.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.formLayoutWidget = QtWidgets.QWidget(formLogin)
        self.formLayoutWidget.setGeometry(QtCore.QRect(80, 50, 401, 71))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.txtPasswd = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.txtPasswd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txtPasswd.setObjectName("txtPasswd")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtPasswd)
        self.txtEmail = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.txtEmail.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.txtEmail.setObjectName("txtEmail")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.txtEmail)
        self.btnLogin = QtWidgets.QPushButton(formLogin)
        self.btnLogin.setGeometry(QtCore.QRect(150, 140, 89, 31))
        self.btnLogin.setObjectName("btnLogin")
        self.btnExit = QtWidgets.QPushButton(formLogin)
        self.btnExit.setGeometry(QtCore.QRect(260, 140, 89, 31))
        self.btnExit.setObjectName("btnExit")
        self.label_3 = QtWidgets.QLabel(formLogin)
        self.label_3.setGeometry(QtCore.QRect(170, 10, 221, 17))
        self.label_3.setObjectName("label_3")
        self.lblStatus = QtWidgets.QLabel(formLogin)
        self.lblStatus.setGeometry(QtCore.QRect(0, 207, 571, 31))
        self.lblStatus.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lblStatus.setText("")
        self.lblStatus.setObjectName("lblStatus")

        self.retranslateUi(formLogin)
        QtCore.QMetaObject.connectSlotsByName(formLogin)
        formLogin.setTabOrder(self.txtEmail, self.txtPasswd)
        formLogin.setTabOrder(self.txtPasswd, self.btnLogin)
        formLogin.setTabOrder(self.btnLogin, self.btnExit)

    def retranslateUi(self, formLogin):
        _translate = QtCore.QCoreApplication.translate
        formLogin.setWindowTitle(_translate("formLogin", "Login - Portão Virtual"))
        self.label.setText(_translate("formLogin", "Email:"))
        self.label_2.setText(_translate("formLogin", "Senha:"))
        self.btnLogin.setText(_translate("formLogin", "Entrar"))
        self.btnExit.setText(_translate("formLogin", "Cancelar"))
        self.label_3.setText(_translate("formLogin", "Portão Virtual - Login"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    formLogin = QtWidgets.QWidget()
    ui = Ui_formLogin()
    ui.setupUi(formLogin)
    formLogin.show()
    sys.exit(app.exec_())

