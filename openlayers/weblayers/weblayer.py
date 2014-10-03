# -*- coding: utf-8 -*-
"""
/***************************************************************************
OpenLayers Plugin
A QGIS plugin

                             -------------------
begin                : 2009-11-30
copyright            : (C) 2009 by Pirmin Kalberer, Sourcepole
email                : pka at sourcepole.ch
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

from PyQt4.QtGui import QAction, QIcon, QMenu
from qgis.core import QGis, QgsCoordinateReferenceSystem
import os
import sys


class WebLayerGroup:
    """Group in menu"""

    def __init__(self, name, icon):
        self._menu = QMenu(name)
        self._menu.setIcon(QIcon(os.path.join(":/plugins/openlayers/weblayers/icons", icon)))

    def menu(self):
        return self._menu


class WebLayer:
    """Base class for OpenLayers layers"""

    displayName = None
    """Layer type name in menu"""

    layerTypeName = None
    """Layer type identificator used to store in project"""

    layerTypeId = None
    """Numerical ID used in versions < 2.3"""
    #GOOGLE_TERRAIN => 0,
    #GOOGLE_ROADMAP => 1,
    #GOOGLE_HYBRID => 2,
    #GOOGLE_SATELLITE => 3,
    #OSM => 4,
    #OCM => 5,
    #OCM_LANDSCAPE => 6,
    #OCM_PUBLIC_TRANSPORT => 7,
    #YAHOO_STREET => 8,
    #YAHOO_HYBRID => 9,
    #YAHOO_SATELLITE => 10,
    #BING_ROAD => 11,
    #BING_AERIAL => 12,
    #BING_AERIAL_WITH_LABELS => 13,
    #APPLE_IPHOTO => 14

    groupName = None
    """Group in menu"""

    groupIcon = None
    """Group icon in menu"""

    epsgList = []
    """Supported EPSG projections, ordered by preference"""

    fullExtent = [-180.0, -90.0, 180.0, 90.0]
    """WGS84 bounds"""

    emitsLoadEnd = True

    def __init__(self, groupName, groupIcon, name, html):
        self.groupName = groupName
        self.groupIcon = groupIcon
        self.displayName = name
        self.layerTypeName = name
        self._html = html

    def addMenuEntry(self, groupMenu, parent):
        self._actionAddLayer = QAction(self.displayName, parent)
        self._actionAddLayer.triggered.connect(self.addLayer)
        groupMenu.addAction(self._actionAddLayer)

    def setAddLayerCallback(self, addLayerCallback):
        self._addLayerCallback = addLayerCallback

    def addLayer(self):
        self._addLayerCallback(self)

    def html_url(self):
        dir = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
        url = "file:///%s/html/%s" % (dir.replace("\\", "/"), self._html)
        return url

    def coordRefSys(self, mapCoordSys):
        epsg = self.epsgList[0]  # TODO: look for matching coord
        coordRefSys = QgsCoordinateReferenceSystem()
        createCrs = coordRefSys.createFromOgcWmsCrs("EPSG:%d" % epsg)
        if not createCrs:
            return None
        return coordRefSys


class WebLayer3857(WebLayer):

    epsgList = [3857]

    MAX_ZOOM_LEVEL = 15
    SCALE_ON_MAX_ZOOM = 13540  # QGIS scale for 72 dpi

    def coordRefSys(self, mapCoordSys):
        epsg = self.epsgList[0]
        coordRefSys = QgsCoordinateReferenceSystem()
        if QGis.QGIS_VERSION_INT >= 10900:
            idEpsgRSGoogle = "EPSG:%d" % epsg
            createCrs = coordRefSys.createFromOgcWmsCrs(idEpsgRSGoogle)
        else:
            idEpsgRSGoogle = epsg
            createCrs = coordRefSys.createFromEpsg(idEpsgRSGoogle)
        if not createCrs:
            google_proj_def = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 "
            google_proj_def += "+units=m +nadgrids=@null +wktext +no_defs"
            isOk = coordRefSys.createFromProj4(google_proj_def)
            if not isOk:
                return None
        return coordRefSys
