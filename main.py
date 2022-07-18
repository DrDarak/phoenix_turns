import sys
from PyQt5 import QtWidgets, QtGui
from dialogs import *
import config as cfg
from functools import partial



class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    """
    CREATE A SYSTEM TRAY ICON CLASS AND ADD MENU
    """

    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'Phoenix Turn Downloader')
        self.menu = QtWidgets.QMenu(parent)

        ## add user list
        self.users=[]
        for login in cfg.data['users']:
            action = self.menu.addAction(login)
            self.users.append(action)
            action.triggered.connect(partial(self.change_user,login))
        self.update_current_user()

        self.separator=self.menu.addSeparator()

        open_app = self.menu.addAction("Update Turns")
        open_app.triggered.connect(self.update_turns_window)
        open_app.setIcon(QtGui.QIcon("phoenix_32x32.png"))

        self.login_action = self.menu.addAction("Login")
        self.login_action.setIcon(QtGui.QIcon("phoenix_32x32.png"))
        self.login_action.triggered.connect(self.login_window)

        exit_ = self.menu.addAction("Exit")
        exit_.triggered.connect(lambda: sys.exit())
        exit_.setIcon(QtGui.QIcon("phoenix_32x32.png"))


        self.setContextMenu(self.menu)
        ##self.activated.connect(self.onTrayIconActivated)

        ## Start timer for processing turns
        ##self.timer_id=self.startTimer(10000,self.VeryCoarseTimer)


    def timerEvent(self, event):
        self.showMessage("60 sec","60 sec")


    def onTrayIconActivated(self, reason):
        """
        This function will trigger function on click or double click
        :param reason:
        :return:
        """
        if reason == self.DoubleClick:
            self.open_notepad()
        # if reason == self.Trigger:
        #     self.open_notepad()

    def change_user(self,user):
        if cfg.set_current_user(user)==True:
            self.update_current_user()

    def options_window(self):
        ##dlg = Login_Dialog()
        ##dlg.exec_()
        pass

    def login_window(self):
        old_user=cfg.data['current_user']
        dlg =Login_Dialog()
        dlg.exec_()
        if old_user!=cfg.data['current_user']:
            ## add new action to menu
            action = QtWidgets.QAction(cfg.data['current_user'], self)
            self.menu.insertAction(self.separator, action)
            action.triggered.connect(lambda: self.change_user(cfg.data['current_user']))
            self.users.append(action)
            self.update_current_user()

    def update_current_user(self):
        for action in self.users:
            if action.text()==cfg.data['current_user']:
                action.setIcon(QtGui.QIcon("tick.png"))
            else:
                action.setIcon(QtGui.QIcon())

    def update_turns_window(self):
        dlg=TurnUpdate_Dialog()
        dlg.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon("phoenix_32x32.png"), w)
    tray_icon.show()
    ##  tray_icon.showMessage('Title', 'Hello "Name of logged in ID')
    app.exec_()


if __name__ == '__main__':
    main()



