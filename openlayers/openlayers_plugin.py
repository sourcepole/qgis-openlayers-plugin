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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *

import resources
import math

from openlayers_layer import OpenlayersLayer
from openlayers_plugin_layer_type import OpenlayersPluginLayerType
from openlayers_ovwidget import OpenLayersOverviewWidget

class OlLayerType:

  def __init__(self, plugin, id, name, icon, html, emitsLoadEnd = False):
    self.plugin = plugin
    self.id = id
    self.name = name
    self.icon = icon
    self.html = html
    self.emitsLoadEnd = emitsLoadEnd

  def addLayer(self):
    self.plugin.addLayer(self)


class OlLayerTypeRegistry:

  def __init__(self):
    self.olLayerTypes = {}

  def add(self, layerType):
    self.olLayerTypes[layerType.id] = layerType

  def types(self):
    return self.olLayerTypes.values()

  def getById(self, id):
    return self.olLayerTypes[id]


class OLOverview(object):

  def __init__(self, iface, olLayerTypeRegistry):
    self.__iface = iface
    self.__olLayerTypeRegistry = olLayerTypeRegistry
    self.__dockwidget = None
    self.__oloWidget = None

  # Private
  def __setDocWidget(self):
    self.__dockwidget = QDockWidget("Openlayers Overview" , self.__iface.mainWindow() )
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
    # Layers
    self.olLayerTypeRegistry = OlLayerTypeRegistry()
    self.olLayerTypeRegistry.add( OlLayerType(self, 0, 'Google Physical',  'google_icon.png', 'google_physical.html') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 1, 'Google Streets',   'google_icon.png', 'google_streets.html') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 2, 'Google Hybrid',    'google_icon.png', 'google_hybrid.html') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 3, 'Google Satellite', 'google_icon.png', 'google_satellite.html') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 4, 'OpenStreetMap',    'osm_icon.png',    'osm.html', True) )
    self.olLayerTypeRegistry.add( OlLayerType(self, 5, 'Yahoo Street',     'yahoo_icon.png',  'yahoo_street.html') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 6, 'Yahoo Hybrid',     'yahoo_icon.png',  'yahoo_hybrid.html') )
    self.olLayerTypeRegistry.add( OlLayerType(self, 7, 'Yahoo Satellite',  'yahoo_icon.png',  'yahoo_satellite.html') )
    # Overview
    self.olOverview = OLOverview( iface, self.olLayerTypeRegistry )

  def initGui(self):
    # Overview
    self.overviewAddAction = QAction("Openlayers Overview", self.iface.mainWindow())
    self.overviewAddAction.setCheckable(True)
    self.overviewAddAction.setChecked(False)
    QObject.connect(self.overviewAddAction, SIGNAL(" toggled(bool)"), self.olOverview.setVisible )
    self.iface.addPluginToMenu("OpenLayers plugin", self.overviewAddAction)
    # Layers
    self.layerAddActions = []
    for layerType in self.olLayerTypeRegistry.types():
      # Create actions for adding layers
      action = QAction(QIcon(":/plugins/openlayers/%s" % layerType.icon), "Add %s layer" % layerType.name, self.iface.mainWindow())
      self.layerAddActions.append(action)
      QObject.connect(action, SIGNAL("triggered()"), layerType.addLayer)
      # Add toolbar button and menu item
      self.iface.addPluginToMenu("OpenLayers plugin", action)

    if not self.__setCoordRSGoogle():
      QMessageBox.critical(self.iface.mainWindow(), "OpenLayers Plugin", "Could not set Google projection!")
      return

    # Register plugin layer type
    QgsPluginLayerRegistry.instance().addPluginLayerType(OpenlayersPluginLayerType(self.iface, self.setReferenceLayer, self.__coordRSGoogle, self.olLayerTypeRegistry))

    self.layer = None
    QObject.connect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.scaleChanged)
    QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)
    
  def unload(self):
    # Remove the plugin menu item and icon
    for action in self.layerAddActions:
      self.iface.removePluginMenu("OpenLayers plugin", action)

    self.iface.removePluginMenu("OpenLayers plugin", self.overviewAddAction)  

    # Unregister plugin layer type
    QgsPluginLayerRegistry.instance().removePluginLayerType(OpenlayersLayer.LAYER_TYPE)

    QObject.disconnect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.scaleChanged)
    QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)
    
    self.olOverview.setVisible( False )
    del self.olOverview

  def addLayer(self, layerType):

    self.__setMapSrsGoogle()

    layer = OpenlayersLayer(self.iface, self.__coordRSGoogle, self.olLayerTypeRegistry)
    layer.setLayerName(layerType.name)
    layer.setLayerType(layerType)
    if layer.isValid():
      QgsMapLayerRegistry.instance().addMapLayer(layer)

      # last added layer is new reference
      self.setReferenceLayer(layer)

  def scaleChanged(self, scale):
    if scale > 0 and self.layer != None:
      # get OpenLayers scale for this extent
      olScale = self.layer.scaleFromExtent(self.iface.mapCanvas().extent())
      if olScale > 0.0:
        # calculate QGIS scale
        targetScale = olScale * self.iface.mapCanvas().mapRenderer().outputDpi() / 72.0
        qDebug("scaleChanged: %f - olScale: %f -> Canvas scale: %f" % (scale, olScale, targetScale) )
        # NOTE: use a slightly smaller scale to avoid zoomout feedback loop
        targetScale *= 0.999
        if math.fabs(scale - targetScale)/scale > 0.001:
          # override scale
          self.iface.mapCanvas().zoomByFactor(targetScale / scale)

  def setReferenceLayer(self, layer):
    self.layer = layer
    # TODO: update initial scale

  def removeLayer(self, layerId):
    layerToRemove = None
    if self.layer != None and self.layer.getLayerID() == layerId:
      self.layer = None
      # TODO: switch to next available OpenLayers layer?

  def __setCoordRSGoogle(self):
    idEpsgRSGoogle = 900913
    self.__coordRSGoogle = QgsCoordinateReferenceSystem()
    if not self.__coordRSGoogle.createFromEpsg(idEpsgRSGoogle):
      google_proj_def = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1 "
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
    theCoodRS = mapCanvas.mapRenderer().destinationSrs()
    if theCoodRS != self.__coordRSGoogle:
      coodTrans = QgsCoordinateTransform(theCoodRS, self.__coordRSGoogle)
      extMap = mapCanvas.extent()
      extMap = coodTrans.transform(extMap, QgsCoordinateTransform.ForwardTransform)
      mapCanvas.mapRenderer().setDestinationSrs(self.__coordRSGoogle)
      mapCanvas.freeze(False)
      mapCanvas.setMapUnits(self.__coordRSGoogle.mapUnits())
      mapCanvas.setExtent(extMap)
