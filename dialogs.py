from PyQt5.QtWidgets import QDialog, QPushButton,QProgressBar,QLabel,QLineEdit,QMessageBox
from PyQt5 import QtCore,QtGui
import turns
from threading import Thread
import phoenix_core as core
import positions

class TurnUpdate_Dialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowIcon(QtGui.QIcon("phoenix_32x32.png"))
        self.setModal(True)
        self.setWindowTitle("Download Turns")
        self.setObjectName("Dialog")
        self.setFixedSize(450, 70)
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(QtCore.QRect(10, 10, 430, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")

        self.doneButton = QPushButton(self)
        self.doneButton.setGeometry(QtCore.QRect(367, 40, 75, 23))
        self.doneButton.setFlat(False)
        self.doneButton.setObjectName("doneButton")
        self.doneButton.setText("Done")
        self.doneButton.clicked.connect(self.done)

        self.updateButton = QPushButton(self)
        self.updateButton.setGeometry(QtCore.QRect(280, 40, 75, 23))
        self.updateButton.setFlat(False)
        self.updateButton.setObjectName("updateButton")
        self.updateButton.setText("Update")
        self.updateButton.clicked.connect(self.update_turns)

        QtCore.QMetaObject.connectSlotsByName(self)

    def update_turns(self):
        self.updateButton.setEnabled(False)
        self.doneButton.setEnabled(False)
        positions.load_from_site()
        update_thread = Thread(target=turns.load,args=(self.progressBar,self.update_turns_finished))
        update_thread.start()

    def update_turns_finished(self):
        self.updateButton.setEnabled(True)
        self.doneButton.setEnabled(True)
        self.progressBar.setProperty("value", 0)

## Login button to convert passowrd to code/uid
class Login_Dialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowIcon(QtGui.QIcon("phoenix_32x32.png"))
        self.setModal(True)
        self.setWindowTitle("Login to Phoenix")
        self.setFixedSize(400, 72)

        self.label_0 = QLabel(self)
        self.label_0.setObjectName(u"label_0")
        self.label_0.setGeometry(QtCore.QRect(10, 10, 71, 16))
        self.label_0.setText(u"User Name")

        self.label_1 = QLabel(self)
        self.label_1.setObjectName(u"label_1")
        self.label_1.setGeometry(QtCore.QRect(10, 40, 71, 16))
        self.label_1.setText(u"Password")

        self.username = QLineEdit(self)
        self.username.setObjectName(u"Username")
        self.username.setGeometry(QtCore.QRect(92, 10, 201, 20))

        self.password = QLineEdit(self)
        self.password.setObjectName(u"Password")
        self.password.setGeometry(QtCore.QRect(92, 40, 201, 20))

        self.login_button = QPushButton(self)
        self.login_button.setObjectName(u"login")
        self.login_button.setGeometry(QtCore.QRect(310, 10, 81, 23))
        self.login_button.setText("Login")
        self.login_button.clicked.connect(self.login)

        self.cancel_button = QPushButton(self)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setGeometry(QtCore.QRect(310, 40, 81, 23))
        self.cancel_button.setText(u"Cancel")
        self.cancel_button.clicked.connect(self.reject)

    def login(self):
        txt = "No username or password."
        if self.username.text()!='' and self.password.text()!='':
            ok=core.login(self.username.text(),self.password.text())
            if ok:
                self.accept()
                return
            txt="Password or username is wrong."
        self.login_message(txt)

    def login_message(self,txt):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Login failed: "+txt)
        msg.setWindowTitle("Login Failed")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
