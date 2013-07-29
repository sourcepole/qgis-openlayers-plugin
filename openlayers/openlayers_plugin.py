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

class OlLayerType:

  def __init__(self, plugin, name, title, group, icon, emitsLoadEnd = False):
    self.__plugin = plugin
    self.name = name
    self.title = title
    self.group = group
    self.icon = icon
    self.emitsLoadEnd = emitsLoadEnd

  def fileUrl(self):
    return "file:///" + os.path.dirname( __file__ ).replace("\\", "/") + "/html/" + self.name + ".html"

  def addLayer(self):
    self.__plugin.addLayer(self)


class OlLayerTypeRegistry:

  def __init__(self):
    self.__olLayerTypesList = []
    self.__olLayerTypes = {}

  def add(self, layerType):
    self.__olLayerTypesList.append(layerType)
    self.__olLayerTypes[layerType.name] = layerType

  def types(self):
    return self.__olLayerTypesList

  def getByName(self, name):
    return self.__olLayerTypes[name]

  def getByIdx(self, idx):
    return self.__olLayerTypesList[idx]


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
    locale = QSettings().value("locale/userLocale").toString()[0:2]
    if QFileInfo(pluginDir).exists():
      localePath = pluginDir + "/i18n/openlayers_" + locale + ".qm"
    if QFileInfo(localePath).exists():
      self.translator = QTranslator()
      self.translator.load(localePath)
      if qVersion() > '4.3.3':
        QCoreApplication.installTranslator(self.translator)

    # Layers
    self.olLayerTypeRegistry = OlLayerTypeRegistry()
    self.olLayerTypeRegistry.add( OlLayerType(self, 'google_physical', 'Google Physical', 'Google', 'google_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'google_streets', 'Google Streets', 'Google', 'google_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'google_hybrid', 'Google Hybrid', 'Google', 'google_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'google_satellite', 'Google Satellite', 'Google', 'google_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'osm', 'OpenStreetMap', 'OpenStreetMap', 'osm_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'ocm', 'OpenCycleMap', 'OpenStreetMap', 'osm_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'ocm_landscape', 'OCM Landscape', 'OpenStreetMap', 'osm_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'ocm_transport', 'OCM Public Transport', 'OpenStreetMap', 'osm_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'yahoo_street', 'Yahoo Street', 'Yahoo', 'yahoo_icon.png') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'yahoo_hybrid', 'Yahoo Hybrid', 'Yahoo', 'yahoo_icon.png') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'yahoo_satellite', 'Yahoo Satellite', 'Yahoo', 'yahoo_icon.png') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'bing_road', 'Bing Road', 'Bing', 'bing_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'bing_aerial', 'Bing Aerial', 'Bing', 'bing_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'bing_aerial-labels', 'Bing Aerial with labels', 'Bing', 'bing_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'apple', 'Apple iPhoto map', 'Various', 'apple_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'stamen_toner', 'Stamen Toner/OSM', 'Stamen', 'stamen_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'stamen_watercolor', 'Stamen Watercolor/OSM', 'Stamen', 'stamen_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'stamen_terrain', 'Stamen Terrain-USA/OSM', 'Stamen', 'stamen_icon.png', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 'tomtom_base', 'TomTom Base', 'Various', 'tomtom_icon.png', True) )
    # Overview
    self.olOverview = OLOverview( iface, self.olLayerTypeRegistry )

  def initGui(self):
    # Overview
    self.overviewAddAction = QAction(QApplication.translate("OpenlayersPlugin", "OpenLayers Overview"), self.iface.mainWindow())
    self.overviewAddAction.setCheckable(True)
    self.overviewAddAction.setChecked(False)
    QObject.connect(self.overviewAddAction, SIGNAL("toggled(bool)"), self.olOverview.setVisible )
    if hasattr(self.iface, "addPluginToWebMenu"):
      #menu = self.iface.webMenu()
      self.iface.addPluginToWebMenu("OpenLayers plugin", self.overviewAddAction)
    else:
      #menu = self.iface.pluginMenu()
      self.iface.addPluginToMenu("OpenLayers plugin", self.overviewAddAction)
    # Layers
    self.layerAddActions = []
    pathPlugin = "%s%s%%s" % ( os.path.dirname( __file__ ), os.path.sep )
    for layerType in self.olLayerTypeRegistry.types():
      # Create actions for adding layers
      action = QAction(QIcon(pathPlugin % layerType.icon), QApplication.translate("OpenlayersPlugin", "Add %1 layer").arg(layerType.title), self.iface.mainWindow())
      self.layerAddActions.append(action)
      QObject.connect(action, SIGNAL("triggered()"), layerType.addLayer)
      # Add toolbar button and menu item
      if hasattr(self.iface, "addPluginToWebMenu"):
        self.iface.addPluginToWebMenu("OpenLayers plugin", action)
      else:
        self.iface.addPluginToMenu("OpenLayers plugin", action)

    if not self.__setCoordRSGoogle():
      QMessageBox.critical(self.iface.mainWindow(), "OpenLayers Plugin", QApplication.translate("OpenlayersPlugin", "Could not set Google projection!"))
      return

    # Register plugin layer type
    QgsPluginLayerRegistry.instance().addPluginLayerType(OpenlayersPluginLayerType(self.iface, self.setReferenceLayer, self.__coordRSGoogle, self.olLayerTypeRegistry))

    self.layer = None
    QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)
    
  def unload(self):
    # Remove the plugin menu item and icon
    for action in self.layerAddActions:
      if hasattr(self.iface, "addPluginToWebMenu"):
        self.iface.removePluginWebMenu("OpenLayers plugin", action)
      else:
        self.iface.removePluginMenu("OpenLayers plugin", action)

    if hasattr(self.iface, "addPluginToWebMenu"):
      self.iface.removePluginWebMenu("OpenLayers plugin", self.overviewAddAction)
    else:
      self.iface.removePluginMenu("OpenLayers plugin", self.overviewAddAction)

    # Unregister plugin layer type
    QgsPluginLayerRegistry.instance().removePluginLayerType(OpenlayersLayer.LAYER_TYPE)

    QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)
    
    self.olOverview.setVisible( False )
    del self.olOverview

  def addLayer(self, layerType):

    self.__setMapSrsGoogle()

    layer = OpenlayersLayer(self.iface, self.__coordRSGoogle, self.olLayerTypeRegistry)
    layer.setLayerName(layerType.title)
    layer.setLayerType(layerType)
    if layer.isValid():
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
      return isOk
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
