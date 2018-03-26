# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_about_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dlgAbout(object):
    def setupUi(self, dlgAbout):
        dlgAbout.setObjectName("dlgAbout")
        dlgAbout.resize(466, 412)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(dlgAbout)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(dlgAbout)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_terms = QtWidgets.QWidget()
        self.tab_terms.setObjectName("tab_terms")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_terms)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.tab_terms)
        self.textBrowser.setUndoRedoEnabled(False)
        self.textBrowser.setReadOnly(True)
        self.textBrowser.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_2.addWidget(self.textBrowser)
        self.tabWidget.addTab(self.tab_terms, "")
        self.tab_about = QtWidgets.QWidget()
        self.tab_about.setObjectName("tab_about")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_about)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.tab_about)
        self.textBrowser_2.setUndoRedoEnabled(False)
        self.textBrowser_2.setReadOnly(True)
        self.textBrowser_2.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.textBrowser_2.setOpenExternalLinks(True)
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.verticalLayout_4.addWidget(self.textBrowser_2)
        self.tabWidget.addTab(self.tab_about, "")
        self.tab_publishing = QtWidgets.QWidget()
        self.tab_publishing.setObjectName("tab_publishing")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_publishing)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.logo = QtWidgets.QLabel(self.tab_publishing)
        self.logo.setAutoFillBackground(False)
        self.logo.setPixmap(QtGui.QPixmap(":/plugins/openlayers/qgiscloud.png"))
        self.logo.setScaledContents(False)
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        self.logo.setObjectName("logo")
        self.verticalLayout_5.addWidget(self.logo)
        self.textBrowser1 = QtWidgets.QTextBrowser(self.tab_publishing)
        self.textBrowser1.setAcceptDrops(False)
        self.textBrowser1.setReadOnly(True)
        self.textBrowser1.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.textBrowser1.setOpenExternalLinks(True)
        self.textBrowser1.setObjectName("textBrowser1")
        self.verticalLayout_5.addWidget(self.textBrowser1)
        self.cb_publishing = QtWidgets.QCheckBox(self.tab_publishing)
        self.cb_publishing.setObjectName("cb_publishing")
        self.verticalLayout_5.addWidget(self.cb_publishing)
        self.tabWidget.addTab(self.tab_publishing, "")
        self.verticalLayout_3.addWidget(self.tabWidget)
        self.widget = QtWidgets.QWidget(dlgAbout)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setMaximumSize(QtCore.QSize(180, 16777215))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_3.addWidget(self.widget)
        self.buttonBox = QtWidgets.QDialogButtonBox(dlgAbout)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.widget.raise_()
        self.tabWidget.raise_()
        self.buttonBox.raise_()

        self.retranslateUi(dlgAbout)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(dlgAbout.accept)
        self.buttonBox.rejected.connect(dlgAbout.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgAbout)

    def retranslateUi(self, dlgAbout):
        _translate = QtCore.QCoreApplication.translate
        dlgAbout.setWindowTitle(_translate("dlgAbout", "About OpenLayers Plugin"))
        self.textBrowser.setHtml(_translate("dlgAbout", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">The terms of service of the used map providers apply!</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">Selected links:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.openstreetmap.org/copyright\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">OpenStreetMap</span></a><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\"> (</span><a href=\"https://operations.osmfoundation.org/policies/tiles/\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">Tile Usage</span></a><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">)</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://developers.google.com/maps/terms\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">Google Maps</span></a></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.microsoft.com/maps/product/terms.html\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">Microsoft® Bing™ Maps</span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt; text-decoration: underline; color:#0057ae;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:600;\">License</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">qgis-openlayers-plugin is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-style:italic;\">Copyright (c) 2010-2017 Pirmin Kalberer &amp; Mathias Walker, Sourcepole AG</span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_terms), _translate("dlgAbout", "Terms of Service"))
        self.textBrowser_2.setHtml(_translate("dlgAbout", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:600;\">Development/Support:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">QGIS OpenLayers plugin is developed and maintained by</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://twitter.com/PirminKalberer\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">@PirminKalberer</span></a><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\"> &amp; Mathias Walker, </span><a href=\"http://sourcepole.com/\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">Sourcepole</span></a><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">, Switzerland</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">Support is available as part of </span><a href=\"http://qgisenterprise.com\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">QGIS Enterprise</span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:600;\">Contributions:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">OpenLayers Overview by Luiz Motta</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">Other contributions by:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Etienne Tourigny</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Minoru Akagi</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Minpa Lee</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Richard Duivenvoorde</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Nathaniel V. Kelso</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Salvatore Larosa</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Jürgen E. Fischer</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Fkili Mohamed</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Morten Agerlin</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Guilhem Vellut</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Vivien Deparday</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Marcelo Soares Souza</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Gerald Rich</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Henry Walshaw</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:600;\">Sponsors:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-BLS Netz AG</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">-Cooperativa Colonizadora Multiactiva Fernheim Ltda.</span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_about), _translate("dlgAbout", "About"))
        self.textBrowser1.setHtml(_translate("dlgAbout", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:11pt;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Noto Sans\'; font-size:11pt;\">Want to publish this map to the Web?</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Noto Sans\'; font-size:11pt;\"><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Noto Sans\'; font-size:11pt;\">Install the QGIS Cloud plugin and publish your map </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Noto Sans\'; font-size:11pt;\">on </span><a href=\"https://qgiscloud.com/?ol\"><span style=\" font-family:\'Noto Sans\'; font-size:11pt; text-decoration: underline; color:#2980b9;\">QGIS Cloud </span></a><span style=\" font-family:\'Noto Sans\'; font-size:11pt;\">with a few mouse clicks!</span></p></body></html>"))
        self.cb_publishing.setText(_translate("dlgAbout", "Don\'t show again"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_publishing), _translate("dlgAbout", "Publishing"))

from . import resources_rc
