from PyQt4 import QtCore, QtGui
from ui_about_dialog import Ui_dlgAbout


class AboutDialog(QtGui.QDialog):
    def __init__(self, topics):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_dlgAbout()
        self.ui.setupUi(self)
