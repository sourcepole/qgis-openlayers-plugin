# -*- coding: utf-8 -*-
"""
/***************************************************************************
    Openlayers Overview  - A QGIS plugin to show map in browser(google maps and others)
                             -------------------
    begin            : 2011-03-01
    copyright        : (C) 2011 by Luiz Motta
    author           : Luiz P. Motta
    email            : motta _dot_ luiz _at_ gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QDockWidget
from openlayers_ovwidget import OpenLayersOverviewWidget


class OLOverview(object):

    def __init__(self, iface, olLayerTypeRegistry):
        self._iface = iface
        self._olLayerTypeRegistry = olLayerTypeRegistry
        self._dockwidget = None
        self._oloWidget = None

    # Private
    def _setDocWidget(self):
        self._dockwidget = QDockWidget(QApplication.translate("OpenLayersOverviewWidget", "OpenLayers Overview"), self._iface.mainWindow())
        self._dockwidget.setObjectName("dwOpenlayersOverview")
        self._oloWidget = OpenLayersOverviewWidget(self._iface, self._dockwidget, self._olLayerTypeRegistry)
        self._dockwidget.setWidget(self._oloWidget)

    def _initGui(self):
        self._setDocWidget()
        self._iface.addDockWidget(Qt.LeftDockWidgetArea, self._dockwidget)

    def _unload(self):
        self._dockwidget.close()
        self._iface.removeDockWidget(self._dockwidget)
        del self._oloWidget
        self._dockwidget = None

    # Public
    def setVisible(self, visible):
        if visible:
            if self._dockwidget is None:
                self._initGui()
        else:
            if not self._dockwidget is None:
                self._unload()
