from PyQt5.QtWidgets import QDialog,  QPushButton,QProgressBar,QSpinBox
from PyQt5 import QtCore
import turns
from threading import Thread

class TurnUpdate_Dialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
    ##    if parent:
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
        update_thread = Thread(target=turns.load,args=(self.progressBar,self.update_turns_finished))
        update_thread.start()
        pass
    def update_turns_finished(self):
        self.updateButton.setEnabled(True)
        self.doneButton.setEnabled(True)
        self.progressBar.setProperty("value", 0)