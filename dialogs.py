from PyQt5.QtWidgets import QDialog, QPushButton,QProgressBar,QLabel,QLineEdit,QMessageBox,QComboBox,QListWidget,QListWidgetItem,QTableWidget,QTableWidgetItem
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem,QHeaderView
from PyQt5 import QtCore,QtGui
import turns
from threading import Thread
import phoenix_core as core
import positions
import tree

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
        self.update()
        positions.load_from_site(self.progressBar)
        turns.download(self.progressBar)
        turns.update_text(self.progressBar)
        #self.updateButton.setEnabled(True)
        self.doneButton.setEnabled(True)
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(1)


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


class Options_Dialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowIcon(QtGui.QIcon("phoenix_32x32.png"))
        self.setModal(True)
        self.setWindowTitle("Phoenix Downloader Options")
        self.setFixedSize(280, 46)

        self.label = QLabel(self)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QtCore.QRect(10, 10, 111, 21))
        self.label.setText(u"Position Browser Colour")

        self.comboBox = QComboBox(self)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QtCore.QRect(130, 10, 140, 22))

        out = tree.Output('images/', 'blue', core.install_path())
        index=0
        for k,v in enumerate(out.colour_scheme):
            if core.data['colour']==v:
                index=k
            self.comboBox.addItem(v)
        self.comboBox.setCurrentIndex(index)
        self.comboBox.currentIndexChanged.connect(self.index_changed)

    def index_changed(self, index):
        colour=self.comboBox.currentText()
        core.set_colour(colour)

## Login button to convert passowrd to code/uid
class Search_Dialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWindowIcon(QtGui.QIcon("phoenix_32x32.png"))
        self.setModal(True)
        self.setWindowTitle("Search Options")
        self.setFixedSize(320, 379)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(10)
        # Add headers
        header= QTableWidgetItem()
        header.setText("Search Terms")
        self.tableWidget.setHorizontalHeaderItem(0,header)
        header= QTableWidgetItem()
        header.setText("Limit")
        self.tableWidget.setHorizontalHeaderItem(1,header)
        #fill in table for searches
        for i in range(0,9):
            s=str(i)
            item = QTableWidgetItem()
            item.setText(str(i+1))
            self.tableWidget.setVerticalHeaderItem(i, item)
            limit='100'
            if s in core.data["search"]:
                item = QTableWidgetItem()
                item.setText(core.data["search"][s]['text'])
                self.tableWidget.setItem(i, 0, item)
                limit=core.data["search"][s]['limit']
            item = QTableWidgetItem()
            item.setText(str(limit))
            self.tableWidget.setItem(i,1, item)

        self.tableWidget.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 300, 326))
        self.tableWidget.itemChanged.connect(self.edit_search)

        self.login_button = QPushButton(self)
        self.login_button.setObjectName(u"test_search")
        self.login_button.setGeometry(QtCore.QRect(10, 346, 81, 23))
        self.login_button.setText("Test Search")
        self.login_button.clicked.connect(self.run_search)

        self.cancel_button = QPushButton(self)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setGeometry(QtCore.QRect(229, 346, 81, 23))
        self.cancel_button.setText(u"Done")
        self.cancel_button.clicked.connect(self.reject)

    def edit_search(self,item):
        r=str(item.row())
        if r not in core.data["search"]:
            core.data["search"][r] = {'text': '', 'limit': '100'}
        if item.column()==0:
            core.data["search"][r]['text']=item.data(0)
        else:
            core.data["search"][r]['limit']=item.data(0)
        core.save()
    def run_search(self):
        positions.create_search_page()


