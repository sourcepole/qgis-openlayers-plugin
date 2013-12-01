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

import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *

import resources_rc
import math

from openlayers_layer import OpenlayersLayer
from openlayers_plugin_layer_type import OpenlayersPluginLayerType
from openlayers_ovwidget import OpenLayersOverviewWidget
from about_dialog import AboutDialog


class OlLayerType:

  def __init__(self, plugin, name, icon, html, emitsLoadEnd = False):
    self.__plugin = plugin
    self.name = name
    self.icon = icon
    self.html = html
    self.emitsLoadEnd = emitsLoadEnd
    self.id = None

  def addLayer(self):
    self.__plugin.addLayer(self)


class OlLayerTypeRegistry:

  def __init__(self):
    self.__olLayerTypes = {}
    self.__layerTypeId = 0

  def add(self, layerType):
    layerType.id = self.__layerTypeId
    self.__olLayerTypes[self.__layerTypeId] = layerType
    self.__layerTypeId += 1

  def types(self):
    return self.__olLayerTypes.values()

  def getById(self, id):
    return self.__olLayerTypes[id]


class OLOverview(object):

  def __init__(self, iface, olLayerTypeRegistry):
    self.__iface = iface
    self.__olLayerTypeRegistry = olLayerTypeRegistry
    self.__dockwidget = None
    self.__oloWidget = None

  # Private
  def __setDocWidget(self):
    self.__dockwidget = QDockWidget(QApplication.translate("OpenLayersOverviewWidget", "OpenLayers Overview"), self.__iface.mainWindow() )
    self.__dockwidget.setObjectName("dwOpenlayersOverview")
    self.__oloWidget = OpenLayersOverviewWidget(self.__iface, self.__dockwidget, self.__olLayerTypeRegistry)
    self.__dockwidget.setWidget(self.__oloWidget)

  def __initGui(self):
    self.__setDocWidget()
    self.__iface.addDockWidget( Qt.LeftDockWidgetArea, self.__dockwidget)

  def __unload(self):
    self.__dockwidget.close()
    self.__iface.removeDockWidget( self.__dockwidget )
    del self.__oloWidget
    self.__dockwidget = None

  # Public
  def setVisible(self, visible):
    if visible:
      if self.__dockwidget is None:
        self.__initGui()
    else:
      if not self.__dockwidget is None:
        self.__unload()
 

class OpenlayersPlugin:

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface

    # setup locale
    pluginDir = os.path.dirname( __file__ )
    localePath = ""
    locale = QSettings().value("locale/userLocale")[0:2]
    if QFileInfo(pluginDir).exists():
      localePath = pluginDir + "/i18n/openlayers_" + locale + ".qm"
    if QFileInfo(localePath).exists():
      self.translator = QTranslator()
      self.translator.load(localePath)
      if qVersion() > '4.3.3':
        QCoreApplication.installTranslator(self.translator)

    # Layers
    self.olLayerTypeRegistry = OlLayerTypeRegistry()
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Google Physical', 'google_icon.png', 'google_physical.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Google Streets', 'google_icon.png', 'google_streets.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Google Hybrid', 'google_icon.png', 'google_hybrid.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Google Satellite', 'google_icon.png', 'google_satellite.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'OpenStreetMap', 'osm_icon.png', 'osm.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'OpenCycleMap', 'osm_icon.png', 'ocm.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'OCM Landscape', 'osm_icon.png', 'ocm_landscape.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'OCM Public Transport', 'osm_icon.png', 'ocm_transport.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Yahoo Street', 'yahoo_icon.png', 'yahoo_street.html') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Yahoo Hybrid', 'yahoo_icon.png', 'yahoo_hybrid.html') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Yahoo Satellite', 'yahoo_icon.png',  'yahoo_satellite.html') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Bing Road', 'bing_icon.png',   'bing_road.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Bing Aerial', 'bing_icon.png',  'bing_aerial.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Bing Aerial with labels', 'bing_icon.png',  'bing_aerial-labels.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Apple iPhoto map', 'apple_icon.png', 'apple.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Stamen Toner/OSM', 'stamen_icon.png', 'stamen_toner.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Stamen Watercolor/OSM', 'stamen_icon.png', 'stamen_watercolor.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'Stamen Terrain-USA/OSM', 'stamen_icon.png', 'stamen_terrain.html', True) )
    # Overview
    self.olOverview = OLOverview( iface, self.olLayerTypeRegistry )
    self.dlgAbout = AboutDialog(iface)

  def initGui(self):
    # Overview
    self.overviewAddAction = QAction(QApplication.translate("OpenlayersPlugin", "OpenLayers Overview"), self.iface.mainWindow())
    self.overviewAddAction.setCheckable(True)
    self.overviewAddAction.setChecked(False)
    QObject.connect(self.overviewAddAction, SIGNAL("toggled(bool)"), self.olOverview.setVisible )
    self.iface.addPluginToMenu("OpenLayers plugin", self.overviewAddAction)

    self.actionAbout = QAction("Terms of Service / About", self.iface.mainWindow())
    QObject.connect(self.actionAbout, SIGNAL("triggered()"), self.dlgAbout, SLOT("show()"))
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAbout)

    # Layers
    self.layerAddActions = []
    pathPlugin = "%s%s%%s" % ( os.path.dirname( __file__ ), os.path.sep )
    for layerType in self.olLayerTypeRegistry.types():
      # Create actions for adding layers
      #action = QAction(QIcon(pathPlugin % layerType.icon), QApplication.translate("OpenlayersPlugin", "Add %1 layer").arg(layerType.name), self.iface.mainWindow())
      # TODO
      action = QAction(QIcon(pathPlugin % layerType.icon), u"Add "+layerType.name+u" layer", self.iface.mainWindow())
      self.layerAddActions.append(action)
      QObject.connect(action, SIGNAL("triggered()"), layerType.addLayer)
      # Add toolbar button and menu item
      self.iface.addPluginToMenu("OpenLayers plugin", action)

    if not self.__setCoordRSGoogle():
      QMessageBox.critical(self.iface.mainWindow(), "OpenLayers Plugin", QApplication.translate("OpenlayersPlugin", "Could not set Google projection!"))
      return

    # Register plugin layer type
    self.pluginLayerType = OpenlayersPluginLayerType(self.iface, self.setReferenceLayer, self.__coordRSGoogle, self.olLayerTypeRegistry)
    QgsPluginLayerRegistry.instance().addPluginLayerType(self.pluginLayerType)

    self.layer = None
    QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)
    
  def unload(self):
    # Remove the plugin menu item and icon
    for action in self.layerAddActions:
      self.iface.removePluginMenu("OpenLayers plugin", action)

    self.iface.removePluginMenu("OpenLayers plugin", self.actionAbout)  
    self.iface.removePluginMenu("OpenLayers plugin", self.overviewAddAction)  

    # Unregister plugin layer type
    QgsPluginLayerRegistry.instance().removePluginLayerType(OpenlayersLayer.LAYER_TYPE)

    QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)
    
    self.olOverview.setVisible( False )
    del self.olOverview

  def addLayer(self, layerType):

    self.__setMapSrsGoogle()

    layer = OpenlayersLayer(self.iface, self.__coordRSGoogle, self.olLayerTypeRegistry)
    layer.setLayerName(layerType.name)
    layer.setLayerType(layerType)
    if layer.isValid():
      if QGis.QGIS_VERSION_INT >= 10900:
        QgsMapLayerRegistry.instance().addMapLayers([layer])
      else:
        QgsMapLayerRegistry.instance().addMapLayer(layer)

      # last added layer is new reference
      self.setReferenceLayer(layer)

  def setReferenceLayer(self, layer):
    self.layer = layer
    # TODO: update initial scale

  def removeLayer(self, layerId):
    layerToRemove = None
    if QGis.QGIS_VERSION_INT >= 10900:
      if self.layer != None and self.layer.id() == layerId:
        self.layer = None
    else:
      if self.layer != None and self.layer.getLayerID() == layerId:
        self.layer = None
    
      # TODO: switch to next available OpenLayers layer?

  def __setCoordRSGoogle(self):
    self.__coordRSGoogle = QgsCoordinateReferenceSystem()
    if QGis.QGIS_VERSION_INT >= 10900:
      idEpsgRSGoogle = 'EPSG:3857'
      createCrs = self.__coordRSGoogle.createFromOgcWmsCrs(idEpsgRSGoogle)
    else:
      idEpsgRSGoogle = 3857
      createCrs = self.__coordRSGoogle.createFromEpsg(idEpsgRSGoogle)
    if not createCrs:
      google_proj_def = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 "
      google_proj_def += "+units=m +nadgrids=@null +wktext +no_defs"
      isOk = self.__coordRSGoogle.createFromProj4(google_proj_def)
      if isOk:
        return True
      else:
        return False
    else:
      return True

  def __setMapSrsGoogle(self):
    mapCanvas = self.iface.mapCanvas()
    # On the fly
    mapCanvas.mapRenderer().setProjectionsEnabled(True) 
    if QGis.QGIS_VERSION_INT >= 10900:
      theCoodRS = mapCanvas.mapRenderer().destinationCrs()
    else:
      theCoodRS = mapCanvas.mapRenderer().destinationSrs()
    if theCoodRS != self.__coordRSGoogle:
      coodTrans = QgsCoordinateTransform(theCoodRS, self.__coordRSGoogle)
      extMap = mapCanvas.extent()
      extMap = coodTrans.transform(extMap, QgsCoordinateTransform.ForwardTransform)
      if QGis.QGIS_VERSION_INT >= 10900:
        mapCanvas.mapRenderer().setDestinationCrs(self.__coordRSGoogle)
      else:
        mapCanvas.mapRenderer().setDestinationSrs(self.__coordRSGoogle)
      mapCanvas.freeze(False)
      mapCanvas.setMapUnits(self.__coordRSGoogle.mapUnits())
      mapCanvas.setExtent(extMap)
