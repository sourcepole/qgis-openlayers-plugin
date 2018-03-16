# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_openlayers_ovwidget.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(457, 467)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.lytEnableMap = QtWidgets.QHBoxLayout()
        self.lytEnableMap.setObjectName("lytEnableMap")
        self.checkBoxEnableMap = QtWidgets.QCheckBox(Form)
        self.checkBoxEnableMap.setChecked(False)
        self.checkBoxEnableMap.setObjectName("checkBoxEnableMap")
        self.lytEnableMap.addWidget(self.checkBoxEnableMap)
        self.comboBoxTypeMap = QtWidgets.QComboBox(Form)
        self.comboBoxTypeMap.setObjectName("comboBoxTypeMap")
        self.lytEnableMap.addWidget(self.comboBoxTypeMap)
        self.pbAddRaster = QtWidgets.QPushButton(Form)
        self.pbAddRaster.setText("")
        self.pbAddRaster.setObjectName("pbAddRaster")
        self.lytEnableMap.addWidget(self.pbAddRaster)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.lytEnableMap.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.lytEnableMap)
        self.lbStatusRead = QtWidgets.QLabel(Form)
        self.lbStatusRead.setText("")
        self.lbStatusRead.setTextFormat(QtCore.Qt.PlainText)
        self.lbStatusRead.setObjectName("lbStatusRead")
        self.verticalLayout_2.addWidget(self.lbStatusRead)
        self.webViewMap = QtWebKitWidgets.QWebView(Form)
        self.webViewMap.setObjectName("webViewMap")
        self.verticalLayout_2.addWidget(self.webViewMap)
        self.lytHideCross = QtWidgets.QHBoxLayout()
        self.lytHideCross.setObjectName("lytHideCross")
        self.checkBoxHideCross = QtWidgets.QCheckBox(Form)
        self.checkBoxHideCross.setObjectName("checkBoxHideCross")
        self.lytHideCross.addWidget(self.checkBoxHideCross)
        self.pbRefresh = QtWidgets.QPushButton(Form)
        self.pbRefresh.setText("")
        self.pbRefresh.setObjectName("pbRefresh")
        self.lytHideCross.addWidget(self.pbRefresh)
        self.pbSaveImg = QtWidgets.QPushButton(Form)
        self.pbSaveImg.setText("")
        self.pbSaveImg.setObjectName("pbSaveImg")
        self.lytHideCross.addWidget(self.pbSaveImg)
        self.pbCopyKml = QtWidgets.QPushButton(Form)
        self.pbCopyKml.setText("")
        self.pbCopyKml.setObjectName("pbCopyKml")
        self.lytHideCross.addWidget(self.pbCopyKml)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.lytHideCross.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.lytHideCross)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.checkBoxEnableMap.setText(_translate("Form", "Enable map"))
        self.pbAddRaster.setToolTip(_translate("Form", "Add map"))
        self.checkBoxHideCross.setText(_translate("Form", "Hide cross in map"))
        self.pbRefresh.setToolTip(_translate("Form", "Refresh map"))
        self.pbSaveImg.setToolTip(_translate("Form", "Save this image"))
        self.pbCopyKml.setToolTip(_translate("Form", "Copy rectangle (KML) of map to clipboard"))

from PyQt5 import QtWebKitWidgets
