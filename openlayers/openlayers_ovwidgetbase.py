# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openlayers_ovwidgetbase.ui'
#
# Created: Thu Mar 03 15:46:30 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(457, 467)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.checkBoxEnableMap = QtGui.QCheckBox(Form)
        self.checkBoxEnableMap.setObjectName(_fromUtf8("checkBoxEnableMap"))
        self.horizontalLayout.addWidget(self.checkBoxEnableMap)
        self.comboBoxTypeMap = QtGui.QComboBox(Form)
        self.comboBoxTypeMap.setObjectName(_fromUtf8("comboBoxTypeMap"))
        self.horizontalLayout.addWidget(self.comboBoxTypeMap)
        self.pbAddRaster = QtGui.QPushButton(Form)
        self.pbAddRaster.setText(_fromUtf8(""))
        self.pbAddRaster.setObjectName(_fromUtf8("pbAddRaster"))
        self.horizontalLayout.addWidget(self.pbAddRaster)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pbSaveImg = QtGui.QPushButton(Form)
        self.pbSaveImg.setText(_fromUtf8(""))
        self.pbSaveImg.setObjectName(_fromUtf8("pbSaveImg"))
        self.horizontalLayout.addWidget(self.pbSaveImg)
        self.pbCopyKml = QtGui.QPushButton(Form)
        self.pbCopyKml.setText(_fromUtf8(""))
        self.pbCopyKml.setObjectName(_fromUtf8("pbCopyKml"))
        self.horizontalLayout.addWidget(self.pbCopyKml)
        self.pbRefresh = QtGui.QPushButton(Form)
        self.pbRefresh.setText(_fromUtf8(""))
        self.pbRefresh.setObjectName(_fromUtf8("pbRefresh"))
        self.horizontalLayout.addWidget(self.pbRefresh)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lbStatusRead = QtGui.QLabel(Form)
        self.lbStatusRead.setText(_fromUtf8(""))
        self.lbStatusRead.setTextFormat(QtCore.Qt.PlainText)
        self.lbStatusRead.setObjectName(_fromUtf8("lbStatusRead"))
        self.verticalLayout.addWidget(self.lbStatusRead)
        self.webViewMap = QtWebKit.QWebView(Form)
        self.webViewMap.setObjectName(_fromUtf8("webViewMap"))
        self.verticalLayout.addWidget(self.webViewMap)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxEnableMap.setText(QtGui.QApplication.translate("Form", "Enable map", None, QtGui.QApplication.UnicodeUTF8))
        self.pbAddRaster.setToolTip(QtGui.QApplication.translate("Form", "Add map", None, QtGui.QApplication.UnicodeUTF8))
        self.pbSaveImg.setToolTip(QtGui.QApplication.translate("Form", "Save this image", None, QtGui.QApplication.UnicodeUTF8))
        self.pbCopyKml.setToolTip(QtGui.QApplication.translate("Form", "Copy rectangle (KML) of map to clipboard", None, QtGui.QApplication.UnicodeUTF8))
        self.pbRefresh.setToolTip(QtGui.QApplication.translate("Form", "Refresh map", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import QtWebKit
