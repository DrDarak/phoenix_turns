import os
import sys
from PySide2 import QtWidgets, QtGui
from dialogs import *

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    """
    CREATE A SYSTEM TRAY ICON CLASS AND ADD MENU
    """

    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'VFX Pipeline Application Build - 3.2.56')
        menu = QtWidgets.QMenu(parent)
        open_app = menu.addAction("Update Turns")
        open_app.triggered.connect(self.update_turns)
        open_app.setIcon(QtGui.QIcon("phoenix_32x32.png"))

        exit_ = menu.addAction("Exit")
        exit_.triggered.connect(lambda: sys.exit())
        exit_.setIcon(QtGui.QIcon("phoenix_32x32.png"))

        menu.addSeparator()
        self.setContextMenu(menu)
        self.activated.connect(self.onTrayIconActivated)

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

    def update_turns(self):
        dlg=TurnUpdate_Dialog()
        dlg.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon("phoenix_32x32.png"), w)
    tray_icon.show()
    ##  tray_icon.showMessage('VFX Pipeline', 'Hello "Name of logged in ID')
    app.exec_()


if __name__ == '__main__':
    main()



