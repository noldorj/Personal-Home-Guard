import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QErrorMessage, QMessageBox, QPushButton
from PyQt5.QtCore import QTime
from mainForm import *
import utilsCore as utils


app = QtWidgets.QApplication(sys.argv)
windowConfig = QtWidgets.QMainWindow()
ui = Ui_windowConfig()
ui.setupUi(windowConfig)

statusConfig = utils.StatusConfig(configFile='config.json.gpu')
#TODO getRegions
regions = statusConfig.getRegions()

def refreshStatusConfig():
    statusConfig = utils.StatusConfig(configFile='config.json.gpu')
    regions = statusConfig.getRegions()


def btnCancelRegion():
    ui.btnSaveRegion.setEnabled(False)
    ui.btnCancelRegion.setEnabled(False)
    if len(regions) > 0:
        ui.btnDeleteRegion.setEnabled(True)
    else:
        ui.btnDeleteRegion.setEnabled(False)

    ui.btnNewRegion.setEnabled(True)
    ui.btnNewAlarm.setEnabled(True)
    clearFields()
    comboRegionsUpdate(0)

def clearFields():
    ui.txtRegionName.clear()
    ui.txtNameAlarm.clear()
    ui.txtThreshold.clear()
    ui.comboAlarms.clear()
    ui.comboRegions.clear()
    ui.checkEmailAlert.setCheckState(False)
    ui.checkAlertSound.setCheckState(False)
    ui.checkPerson.setCheckState(False)
    ui.checkBike.setCheckState(False)
    ui.checkCar.setCheckState(False)
    ui.checkDog.setCheckState(False)
    ui.checkMon.setCheckState(False)
    ui.checkTue.setCheckState(False)
    ui.checkWed.setCheckState(False)
    ui.checkThur.setCheckState(False)
    ui.checkFri.setCheckState(False)
    ui.checkSat.setCheckState(False)
    ui.checkSun.setCheckState(False)
    ui.timeEnd.clear()
    ui.timeStart.clear()

def btnCancelAlarm():
    ui.btnSaveRegion.setEnabled(False)
    ui.btnSaveAlarm.setEnabled(False)
    ui.btnDeleteAlarm.setEnabled(True)
    ui.btnCancelAlarm.setEnabled(False)
    ui.btnNewAlarm.setEnabled(True)
    ui.comboAlarms.setEnabled(True)
    comboRegionsUpdate(ui.comboRegions.currentIndex())

def btnSaveRegion():
    print('botao btnSaveRegion')
    statusFields = True
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Campo em branco")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    #checando campos em branco

    if len(ui.txtRegionName.text()) == 0:
        msg.setText("Campo 'Nome da Região' em branco")
        msg.exec()
        ui.txtRegionName.setFocus()
        statusFields = False

    elif len(ui.txtThreshold.text()) == 0:
        msg.setText("Campo 'Acurácia' em branco")
        msg.exec()
        ui.txtThreshold.setFocus()
        statusFields = False

    elif len(ui.txtNameAlarm.text()) == 0:
        msg.setText("Campo 'Nome do Alarme' em branco")
        msg.exec()
        ui.txtNameAlarm.setFocus()
        statusFields = False

    if statusFields:
        t = {'start':{'hour':ui.timeStart.time().hour(), 'min':ui.timeStart.time().minute()},
             'end':{'hour':ui.timeEnd.time().hour(), 'min':ui.timeEnd.time().minute()}}
        days = {'mon':'True' if ui.checkMon.isChecked() else 'False',
                'tues':'True' if ui.checkTue.isChecked() else 'False',
                'wed':'True' if ui.checkWed.isChecked() else 'False',
                'thurs':'True' if ui.checkThur.isChecked() else 'False',
                'fri':'True' if ui.checkFri.isChecked() else 'False',
                'sat':'True' if ui.checkSat.isChecked() else 'False',
                'sun':'True' if ui.checkSun.isChecked() else 'False'
               }
        newAlarm = [{"name":ui.txtNameAlarm.displayText(), 'time':t, 'days':days}]

        objectType = {'person':'True' if ui.checkPerson.isChecked() else 'False',
                      'car':'True' if ui.checkCar.isChecked() else 'False',
                      'bike':'True' if ui.checkBike.isChecked() else 'False',
                      'dog':'True' if ui.checkBike.isChecked() else 'False'}

        points = [[[15,15],[15,65],[65,15],[65,65]]]

        statusConfig.addRegion(ui.txtRegionName.displayText(),
                               'True' if ui.checkEmailAlert.isChecked() else 'False' ,
                               'True' if ui.checkAlertSound.isChecked() else 'False' ,
                               newAlarm, objectType, round(float(ui.txtThreshold.displayText())/100,2), points )
        refreshStatusConfig()
        #print('count: {}'.format(len(regions)))
        comboRegionsUpdate(len(regions)-1)
        comboAlarmsUpdate(0)
        ui.btnSaveRegion.setEnabled(False)

def btnSaveAlarm():
    statusFields = True
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Campo em branco")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    #checando campos em branco

    if len(ui.txtNameAlarm.text()) == 0:
        msg.setText("Campo 'Nome do Alarme' em branco")
        msg.exec()
        ui.txtNameAlarm.setFocus()
        statusFields = False

    if statusFields:

        print('botao btnSAveAlarm')
        t = {'start':{'hour':ui.timeStart.time().hour(), 'min':ui.timeStart.time().minute()},
             'end':{'hour':ui.timeEnd.time().hour(), 'min':ui.timeEnd.time().minute()}}
        days = {'mon':'True' if ui.checkMon.isChecked() else 'False',
                'tues':'True' if ui.checkTue.isChecked() else 'False',
                'wed':'True' if ui.checkWed.isChecked() else 'False',
                'thurs':'True' if ui.checkThur.isChecked() else 'False',
                'fri':'True' if ui.checkFri.isChecked() else 'False',
                'sat':'True' if ui.checkSat.isChecked() else 'False',
                'sun':'True' if ui.checkSun.isChecked() else 'False'
               }
        a = {"name":ui.txtNameAlarm.displayText(), 'time':t, 'days':days}
        statusConfig.addAlarm(ui.comboRegions.currentIndex(), a)
        refreshStatusConfig()

        comboRegionsUpdate(ui.comboRegions.currentIndex())
        ui.btnSaveAlarm.setEnabled(False)
        ui.btnDeleteAlarm.setEnabled(False)
        ui.btnCancelAlarm.setEnabled(False)
        ui.btnNewAlarm.setEnabled(True)
        ui.comboAlarms.setEnabled(True)


def btnDeleteAlarm():
    #print('botao btnDeleteAlarm')
    #print('alarmId: {}'.format(ui.comboRegions.currentText()))
    #print('regionId: {}'.format(ui.comboAlarms.currentText()))
    statusConfig.deleteAlarm(ui.comboRegions.currentText(), ui.comboAlarms.currentText())
    refreshStatusConfig()
    comboRegionsUpdate(0)
    comboAlarmsUpdate(0)


def btnDeleteRegion():
    statusConfig.deleteRegion(ui.comboRegions.currentText())
    refreshStatusConfig()
    comboRegionsUpdate(0)
    comboAlarmsUpdate(0)


def btnNewRegion():
    #print('botao btnNewRegion')
    #clear fields
    clearFields()
    #ui.comboRegions.clear()
    ui.btnCancelRegion.setEnabled(True)
    ui.btnDeleteRegion.setEnabled(False)
    ui.btnSaveRegion.setEnabled(True)
    ui.btnDeleteAlarm.setEnabled(False)
    ui.btnCancelAlarm.setEnabled(False)
    ui.btnSaveAlarm.setEnabled(False)

def fillComboAlarm(regionId):

    #preenchendo lista de alarmes
    if not statusConfig.isAlarmEmpty(regionId):
        for a in regions[regionId].get('alarm'):
            #print('size alarm list: {}'.format(len(r.get('alarm'))))
            #print('name alarm added : {}'.format(a.get('name')))
            ui.comboAlarms.addItem(a.get('name'))

def comboRegionsUpdate(i):
    #print('combo regions update')
    #print('comboBox id: {}'.format(i))

    clearFields()
    #r = regions[i]

    ui.comboAlarms.clear()

    if not statusConfig.isRegionsEmpty():
        for r in regions:
            ui.comboRegions.addItem(r.get("nameRegion"))

        r = regions[i]
        ui.txtRegionName.insert(r.get('nameRegion'))
        ui.txtThreshold.insert(str(r.get('prob_threshold')*100))
        ui.checkEmailAlert.setCheckState(r.get('isEmailAlert')=="True")
        ui.checkAlertSound.setCheckState(r.get('isSoundAlert')=="True")
        ui.checkPerson.setCheckState(r.get('objectType').get('person')=="True")
        ui.checkCar.setCheckState(r.get('objectType').get('car')=="True")
        ui.checkBike.setCheckState(r.get('objectType').get('bike')=="True")
        ui.checkDog.setCheckState(r.get('objectType').get('dog')=="True")

        if not statusConfig.isAlarmEmpty(i):
            fillComboAlarm(i)
            #comboAlarmsUpdate(0)
            #ui.comboAlarms.setCurrentIndex(0)
            print('alarm update from regionupdate')

        ui.comboRegions.setCurrentIndex(i)
        comboAlarmsUpdate(0)
        ui.btnDeleteRegion.setEnabled(True)
        ui.btnCancelRegion.setEnabled(False)



def clearFieldsAlarm():
    ui.checkMon.setCheckState(False)
    ui.checkTue.setCheckState(False)
    ui.checkWed.setCheckState(False)
    ui.checkThur.setCheckState(False)
    ui.checkFri.setCheckState(False)
    ui.checkSat.setCheckState(False)
    ui.checkSun.setCheckState(False)
    ui.timeStart.clear()
    ui.timeEnd.clear()
    ui.txtNameAlarm.clear()
    #ui.comboAlarms.clear()

def btnNewAlarm():
    clearFieldsAlarm()
    ui.btnSaveAlarm.setEnabled(True)
    ui.btnDeleteAlarm.setEnabled(False)
    ui.btnCancelAlarm.setEnabled(True)
    ui.comboAlarms.setEnabled(False)

def comboAlarmsUpdate(i):
    print('alarmUpdate i: {}'.format(i))
    clearFieldsAlarm()

    #preenchendo lista de alarmes
    if not statusConfig.isAlarmEmpty(ui.comboRegions.currentText()) and not statusConfig.isRegionsEmpty():

        ui.btnDeleteAlarm.setEnabled(True)
        a = regions[ui.comboRegions.currentIndex()].get('alarm')[i]
        ui.checkMon.setCheckState(a.get('days').get('mon') == 'True')
        ui.checkTue.setCheckState(a.get('days').get('tues') == 'True')
        ui.checkWed.setCheckState(a.get('days').get('wed') == 'True')
        ui.checkThur.setCheckState(a.get('days').get('thurs') == 'True')
        ui.checkFri.setCheckState(a.get('days').get('fri') == 'True')
        ui.checkSat.setCheckState(a.get('days').get('sat') == 'True')
        ui.checkSun.setCheckState(a.get('days').get('sun') == 'True')
        ui.txtNameAlarm.insert(a.get('name'))
        ui.comboAlarms.setCurrentIndex(i)

        tStart = QTime(int(a.get('time').get('start').get('hour')), int(a.get('time').get('start').get('min')))
        ui.timeStart.setTime(tStart)

        tEnd = QTime(int(a.get('time').get('end').get('hour')),int(a.get('time').get('end').get('min')))
        ui.timeEnd.setTime(tEnd)

    else:
       ui.btnDeleteAlarm.setEnabled(False)



if __name__ == "__main__":

    #preenchendo lista de regioes
    if not statusConfig.isRegionsEmpty:
        ui.btnDeleteRegion.setEnabled(True)
        ui.btnDeleteAlarm.setEnabled(True)

        for r in regions:
            ui.comboRegions.addItem(r.get("nameRegion"))
        comboRegionsUpdate(ui.comboRegions.currentIndex())
        comboAlarmsUpdate(ui.comboAlarms.currentIndex())
    else:
        ui.btnDeleteRegion.setEnabled(False)
        ui.btnDeleteAlarm.setEnabled(False)

    ui.btnSaveAlarm.setEnabled(False)
    ui.btnCancelRegion.setEnabled(False)
    ui.btnCancelAlarm.setEnabled(False)
    ui.btnSaveRegion.setEnabled(False)
    ui.btnNewAlarm.setEnabled(True)
    ui.comboAlarms.setEnabled(True)

    #linkando com slots
    ui.comboRegions.activated['int'].connect(comboRegionsUpdate)
    #ui.comboRegions.currentIndexChanged['int'].connect(comboRegionsUpdate)
    ui.comboAlarms.activated['int'].connect(comboAlarmsUpdate)
    ui.btnSaveAlarm.clicked.connect(btnSaveAlarm)
    ui.btnSaveRegion.clicked.connect(btnSaveRegion)
    ui.btnDeleteAlarm.clicked.connect(btnDeleteAlarm)
    ui.btnDeleteRegion.clicked.connect(btnDeleteRegion)
    ui.btnCancelAlarm.clicked.connect(btnCancelAlarm)
    ui.btnCancelRegion.clicked.connect(btnCancelRegion)
    ui.btnNewRegion.clicked.connect(btnNewRegion)
    ui.btnNewAlarm.clicked.connect(btnNewAlarm)


    windowConfig.show()
    sys.exit(app.exec_())

