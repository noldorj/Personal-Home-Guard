# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainForm.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_formConfig(object):
    def setupUi(self, formConfig):
        formConfig.setObjectName("formConfig")
        formConfig.resize(878, 500)
        self.tabConfig = QtWidgets.QTabWidget(formConfig)
        self.tabConfig.setGeometry(QtCore.QRect(0, 0, 871, 481))
        self.tabConfig.setObjectName("tabConfig")
        self.tabRegion = QtWidgets.QWidget()
        self.tabRegion.setObjectName("tabRegion")
        self.formLayoutWidget = QtWidgets.QWidget(self.tabRegion)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 60, 265, 197))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formRegion = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formRegion.setContentsMargins(0, 0, 0, 0)
        self.formRegion.setObjectName("formRegion")
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        self.label.setObjectName("label")
        self.formRegion.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.txtRegionName = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.txtRegionName.setObjectName("txtRegionName")
        self.formRegion.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.txtRegionName)
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formRegion.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.checkDog = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkDog.setObjectName("checkDog")
        self.formRegion.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.checkDog)
        self.checkBike = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkBike.setObjectName("checkBike")
        self.formRegion.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.checkBike)
        self.checkCar = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkCar.setObjectName("checkCar")
        self.formRegion.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.checkCar)
        self.checkPerson = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkPerson.setObjectName("checkPerson")
        self.formRegion.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.checkPerson)
        self.formLayoutWidget_4 = QtWidgets.QWidget(self.tabRegion)
        self.formLayoutWidget_4.setGeometry(QtCore.QRect(10, 280, 160, 41))
        self.formLayoutWidget_4.setObjectName("formLayoutWidget_4")
        self.formAccuracy = QtWidgets.QFormLayout(self.formLayoutWidget_4)
        self.formAccuracy.setContentsMargins(0, 0, 0, 0)
        self.formAccuracy.setObjectName("formAccuracy")
        self.label_11 = QtWidgets.QLabel(self.formLayoutWidget_4)
        self.label_11.setObjectName("label_11")
        self.formAccuracy.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.txtThreshold = QtWidgets.QLineEdit(self.formLayoutWidget_4)
        self.txtThreshold.setText("")
        self.txtThreshold.setPlaceholderText("")
        self.txtThreshold.setObjectName("txtThreshold")
        self.formAccuracy.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.txtThreshold)
        self.formLayoutWidget_3 = QtWidgets.QWidget(self.tabRegion)
        self.formLayoutWidget_3.setGeometry(QtCore.QRect(460, 60, 411, 336))
        self.formLayoutWidget_3.setObjectName("formLayoutWidget_3")
        self.formAlarm = QtWidgets.QFormLayout(self.formLayoutWidget_3)
        self.formAlarm.setContentsMargins(0, 0, 0, 0)
        self.formAlarm.setObjectName("formAlarm")
        self.formTime = QtWidgets.QFormLayout()
        self.formTime.setObjectName("formTime")
        self.label_9 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_9.setObjectName("label_9")
        self.formTime.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.txtNameAlarm = QtWidgets.QLineEdit(self.formLayoutWidget_3)
        self.txtNameAlarm.setObjectName("txtNameAlarm")
        self.formTime.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.txtNameAlarm)
        self.label_3 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_3.setObjectName("label_3")
        self.formTime.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.checkMon = QtWidgets.QCheckBox(self.formLayoutWidget_3)
        self.checkMon.setObjectName("checkMon")
        self.formTime.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.checkMon)
        self.checkFri = QtWidgets.QCheckBox(self.formLayoutWidget_3)
        self.checkFri.setObjectName("checkFri")
        self.formTime.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.checkFri)
        self.checkTue = QtWidgets.QCheckBox(self.formLayoutWidget_3)
        self.checkTue.setObjectName("checkTue")
        self.formTime.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.checkTue)
        self.checkSat = QtWidgets.QCheckBox(self.formLayoutWidget_3)
        self.checkSat.setObjectName("checkSat")
        self.formTime.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.checkSat)
        self.checkWed = QtWidgets.QCheckBox(self.formLayoutWidget_3)
        self.checkWed.setObjectName("checkWed")
        self.formTime.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.checkWed)
        self.checkSun = QtWidgets.QCheckBox(self.formLayoutWidget_3)
        self.checkSun.setObjectName("checkSun")
        self.formTime.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.checkSun)
        self.checkThur = QtWidgets.QCheckBox(self.formLayoutWidget_3)
        self.checkThur.setObjectName("checkThur")
        self.formTime.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.checkThur)
        self.formAlarm.setLayout(0, QtWidgets.QFormLayout.SpanningRole, self.formTime)
        self.label_4 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_4.setObjectName("label_4")
        self.formAlarm.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_5 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_5.setObjectName("label_5")
        self.formAlarm.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.timeStart = QtWidgets.QTimeEdit(self.formLayoutWidget_3)
        self.timeStart.setObjectName("timeStart")
        self.formAlarm.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.timeStart)
        self.label_6 = QtWidgets.QLabel(self.formLayoutWidget_3)
        self.label_6.setObjectName("label_6")
        self.formAlarm.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.timeEnd = QtWidgets.QTimeEdit(self.formLayoutWidget_3)
        self.timeEnd.setObjectName("timeEnd")
        self.formAlarm.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.timeEnd)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnSaveAlarm = QtWidgets.QPushButton(self.formLayoutWidget_3)
        self.btnSaveAlarm.setEnabled(True)
        self.btnSaveAlarm.setObjectName("btnSaveAlarm")
        self.horizontalLayout.addWidget(self.btnSaveAlarm)
        self.btnDeleteAlarm = QtWidgets.QPushButton(self.formLayoutWidget_3)
        self.btnDeleteAlarm.setObjectName("btnDeleteAlarm")
        self.horizontalLayout.addWidget(self.btnDeleteAlarm)
        self.btnCancelAlarm = QtWidgets.QPushButton(self.formLayoutWidget_3)
        self.btnCancelAlarm.setObjectName("btnCancelAlarm")
        self.horizontalLayout.addWidget(self.btnCancelAlarm)
        self.formAlarm.setLayout(5, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.checkEmailAlert = QtWidgets.QCheckBox(self.formLayoutWidget_3)
        self.checkEmailAlert.setObjectName("checkEmailAlert")
        self.formAlarm.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.checkEmailAlert)
        self.checkAlertSound = QtWidgets.QCheckBox(self.formLayoutWidget_3)
        self.checkAlertSound.setObjectName("checkAlertSound")
        self.formAlarm.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.checkAlertSound)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.tabRegion)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 441, 41))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_7 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_2.addWidget(self.label_7)
        self.comboRegions = QtWidgets.QComboBox(self.horizontalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboRegions.sizePolicy().hasHeightForWidth())
        self.comboRegions.setSizePolicy(sizePolicy)
        self.comboRegions.setObjectName("comboRegions")
        self.horizontalLayout_2.addWidget(self.comboRegions)
        self.btnNewRegion = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.btnNewRegion.setObjectName("btnNewRegion")
        self.horizontalLayout_2.addWidget(self.btnNewRegion)
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.tabRegion)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(460, 10, 391, 41))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_8 = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_3.addWidget(self.label_8)
        self.comboAlarms = QtWidgets.QComboBox(self.horizontalLayoutWidget_3)
        self.comboAlarms.setMinimumSize(QtCore.QSize(200, 0))
        self.comboAlarms.setCurrentText("")
        self.comboAlarms.setObjectName("comboAlarms")
        self.horizontalLayout_3.addWidget(self.comboAlarms)
        self.btnNewAlarm = QtWidgets.QPushButton(self.horizontalLayoutWidget_3)
        self.btnNewAlarm.setMaximumSize(QtCore.QSize(200, 16777215))
        self.btnNewAlarm.setObjectName("btnNewAlarm")
        self.horizontalLayout_3.addWidget(self.btnNewAlarm)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.tabRegion)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 399, 391, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.btnSaveRegion = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnSaveRegion.setObjectName("btnSaveRegion")
        self.horizontalLayout_4.addWidget(self.btnSaveRegion)
        self.btnDeleteRegion = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnDeleteRegion.setObjectName("btnDeleteRegion")
        self.horizontalLayout_4.addWidget(self.btnDeleteRegion)
        self.btnCancelRegion = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.btnCancelRegion.setObjectName("btnCancelRegion")
        self.horizontalLayout_4.addWidget(self.btnCancelRegion)
        self.tabConfig.addTab(self.tabRegion, "")
        self.tabConfig_2 = QtWidgets.QWidget()
        self.tabConfig_2.setObjectName("tabConfig_2")
        self.gridLayoutWidget = QtWidgets.QWidget(self.tabConfig_2)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 50, 381, 191))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_13 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 1, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 0, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_10.setText("")
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 3, 1, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(self.gridLayoutWidget)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 2, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.tabConfig_2)
        self.label_12.setGeometry(QtCore.QRect(10, 0, 187, 16))
        self.label_12.setObjectName("label_12")
        self.tabConfig.addTab(self.tabConfig_2, "")

        self.retranslateUi(formConfig)
        self.tabConfig.setCurrentIndex(1)
        self.comboAlarms.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(formConfig)
        formConfig.setTabOrder(self.comboRegions, self.btnNewRegion)
        formConfig.setTabOrder(self.btnNewRegion, self.txtRegionName)
        formConfig.setTabOrder(self.txtRegionName, self.checkPerson)
        formConfig.setTabOrder(self.checkPerson, self.checkCar)
        formConfig.setTabOrder(self.checkCar, self.checkBike)
        formConfig.setTabOrder(self.checkBike, self.checkDog)
        formConfig.setTabOrder(self.checkDog, self.txtThreshold)
        formConfig.setTabOrder(self.txtThreshold, self.txtNameAlarm)
        formConfig.setTabOrder(self.txtNameAlarm, self.checkMon)
        formConfig.setTabOrder(self.checkMon, self.checkTue)
        formConfig.setTabOrder(self.checkTue, self.checkWed)
        formConfig.setTabOrder(self.checkWed, self.checkThur)
        formConfig.setTabOrder(self.checkThur, self.checkFri)
        formConfig.setTabOrder(self.checkFri, self.checkSat)
        formConfig.setTabOrder(self.checkSat, self.checkSun)
        formConfig.setTabOrder(self.checkSun, self.checkEmailAlert)
        formConfig.setTabOrder(self.checkEmailAlert, self.checkAlertSound)
        formConfig.setTabOrder(self.checkAlertSound, self.timeStart)
        formConfig.setTabOrder(self.timeStart, self.timeEnd)
        formConfig.setTabOrder(self.timeEnd, self.btnSaveAlarm)
        formConfig.setTabOrder(self.btnSaveAlarm, self.btnSaveRegion)
        formConfig.setTabOrder(self.btnSaveRegion, self.tabConfig)
        formConfig.setTabOrder(self.tabConfig, self.btnDeleteAlarm)
        formConfig.setTabOrder(self.btnDeleteAlarm, self.comboAlarms)
        formConfig.setTabOrder(self.comboAlarms, self.btnNewAlarm)
        formConfig.setTabOrder(self.btnNewAlarm, self.btnCancelAlarm)
        formConfig.setTabOrder(self.btnCancelAlarm, self.btnDeleteRegion)
        formConfig.setTabOrder(self.btnDeleteRegion, self.btnCancelRegion)

    def retranslateUi(self, formConfig):
        _translate = QtCore.QCoreApplication.translate
        formConfig.setWindowTitle(_translate("formConfig", "Form"))
        self.label.setText(_translate("formConfig", "Nome:"))
        self.label_2.setText(_translate("formConfig", "Tipo de reconhecimento"))
        self.checkDog.setText(_translate("formConfig", "Cachorro"))
        self.checkBike.setText(_translate("formConfig", "Moto"))
        self.checkCar.setText(_translate("formConfig", "Carro"))
        self.checkPerson.setText(_translate("formConfig", "Pessoa"))
        self.label_11.setText(_translate("formConfig", "Acurácia (%)"))
        self.label_9.setText(_translate("formConfig", "Nome:"))
        self.label_3.setText(_translate("formConfig", "Dias"))
        self.checkMon.setText(_translate("formConfig", "Seg"))
        self.checkFri.setText(_translate("formConfig", "Sex"))
        self.checkTue.setText(_translate("formConfig", "Ter"))
        self.checkSat.setText(_translate("formConfig", "Sab"))
        self.checkWed.setText(_translate("formConfig", "Qua"))
        self.checkSun.setText(_translate("formConfig", "Dom"))
        self.checkThur.setText(_translate("formConfig", "Qui"))
        self.label_4.setText(_translate("formConfig", "Horários"))
        self.label_5.setText(_translate("formConfig", "Início"))
        self.label_6.setText(_translate("formConfig", "Fim"))
        self.btnSaveAlarm.setText(_translate("formConfig", "Salvar"))
        self.btnDeleteAlarm.setText(_translate("formConfig", "Deletar"))
        self.btnCancelAlarm.setText(_translate("formConfig", "Cancelar"))
        self.checkEmailAlert.setText(_translate("formConfig", "Alerta de Email"))
        self.checkAlertSound.setText(_translate("formConfig", "Alerta Sonoro"))
        self.label_7.setText(_translate("formConfig", "Regiões:"))
        self.btnNewRegion.setText(_translate("formConfig", "+ Nova região"))
        self.label_8.setText(_translate("formConfig", "Alarmes"))
        self.btnNewAlarm.setText(_translate("formConfig", "+ Novo Alarme"))
        self.btnSaveRegion.setText(_translate("formConfig", "Salvar Região"))
        self.btnDeleteRegion.setText(_translate("formConfig", "Deletar"))
        self.btnCancelRegion.setText(_translate("formConfig", "Cancelar"))
        self.tabConfig.setTabText(self.tabConfig.indexOf(self.tabRegion), _translate("formConfig", "Adicionar Região"))
        self.label_13.setText(_translate("formConfig", "Diretório de gravação:"))
        self.checkBox.setText(_translate("formConfig", "Gravação de video"))
        self.label_12.setText(_translate("formConfig", "Configurações Gerais"))
        self.tabConfig.setTabText(self.tabConfig.indexOf(self.tabConfig_2), _translate("formConfig", "Configuração"))

