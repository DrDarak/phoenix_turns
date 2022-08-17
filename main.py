import sys
from PyQt5 import QtWidgets, QtGui,QtCore
from dialogs import *
import phoenix_core as core
from functools import partial
import webbrowser
import positions
import status


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    """
    CREATE A SYSTEM TRAY ICON CLASS AND ADD MENU
    """
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'Phoenix Turn Downloader')
        self.menu = QtWidgets.QMenu(parent)

        self.show_turns = self.menu.addAction("Show Turns")
        self.show_turns.triggered.connect(self.show_turns_window)
        self.show_turns.setIcon(QtGui.QIcon(core.install_path()+"phoenix_32x32.png"))

        self.separator_1 = self.menu.addSeparator()

        ## add user list
        self.users=[]
        for login in core.data['users']:
            action = self.menu.addAction(login)
            self.users.append(action)
            action.triggered.connect(partial(self.change_user,login))
        self.update_current_user()

        self.separator_2=self.menu.addSeparator()

        self.update_turns = self.menu.addAction("Update Turns")
        self.update_turns.triggered.connect(self.update_turns_window)
        self.update_turns.setIcon(QtGui.QIcon(core.install_path()+"phoenix_32x32.png"))

        self.options_action = self.menu.addAction("Options")
        self.options_action.triggered.connect(self.options_window)

        self.login_action = self.menu.addAction("Login")
        self.login_action.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        self.login_action.triggered.connect(self.login_window)

        exit_ = self.menu.addAction("Exit")
        exit_.triggered.connect(lambda: sys.exit())
        exit_.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_BrowserStop))

        self.setContextMenu(self.menu)

        self.running_login = False
        self.running_update = False
        # use qt and update message que if in slow functions
        core.use_qt()

        ## Start timer for processing turns every 5 mins
        self.timer_id=self.startTimer(5*60*1000)

    def timerEvent(self, event):
        if self.running_update== False:
            self.download_turns()

    def download_turns(self):
        # checks status every 10 mins -> 1 hr
        status.load()
        # if new day downloads positions
        if status.reload_positions():
            positions.load_from_site()
        # any undownloaded position trigger a download
        turns.update()

    def onTrayIconActivated(self, reason):
        if reason == self.DoubleClick:
            self.show_turns_window()

    def change_user(self,user):
        if core.set_current_user(user)==True:
            positions.load_from_site()
            self.update_current_user()

    def options_window(self):
        pass

    def login_window(self):
        if self.running_login == True:
            return
        self.running_login=True
        old_user=core.data['current_user']
        dlg =Login_Dialog()
        dlg.exec_()
        if old_user!=core.data['current_user']:
            ## add new action to menu
            action = QtWidgets.QAction(core.data['current_user'], self)
            self.menu.insertAction(self.separator_2, action)
            action.triggered.connect(lambda: self.change_user(core.data['current_user']))
            self.users.append(action)
            self.update_current_user()
        self.running_login = False

    def update_current_user(self):
        for action in self.users:
            if action.text()==core.data['current_user']:
                action.setIcon(QtGui.QIcon(core.install_path()+"tick.png"))
            else:
                action.setIcon(QtGui.QIcon())

    def update_turns_window(self):
        if self.running_update == True:
            return
        self.running_update=True
        dlg=TurnUpdate_Dialog()
        dlg.exec_()
        self.running_update = False

    def show_turns_window(self):
        positions.create_index_page()
        webbrowser.open(core.data_path()+'index.html')
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon(core.install_path()+"phoenix_32x32.png"), w)
    tray_icon.show()
    ##  tray_icon.showMessage('Title', 'Hello "Name of logged in ID')
    app.exec_()


if __name__ == '__main__':
    main()



