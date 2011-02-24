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

class OpenlayersPlugin:

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface

  def initGui(self):
    # Create action that will start plugin configuration
    self.actionAddOSM = QAction(QIcon(":/plugins/openlayers/osm_icon.png"), "Add OpenStreetMap layer", self.iface.mainWindow())
    self.actionAddGooglePhysical = QAction(QIcon(":/plugins/openlayers/google_icon.png"), "Add Google Physical layer", self.iface.mainWindow())
    self.actionAddGoogleStreets = QAction(QIcon(":/plugins/openlayers/google_icon.png"), "Add Google Streets layer", self.iface.mainWindow())
    self.actionAddGoogleHybrid = QAction(QIcon(":/plugins/openlayers/google_icon.png"), "Add Google Hybrid layer", self.iface.mainWindow())
    self.actionAddGoogleSatellite = QAction(QIcon(":/plugins/openlayers/google_icon.png"), "Add Google Satellite layer", self.iface.mainWindow())
    self.actionAddYahooStreet = QAction(QIcon(":/plugins/openlayers/yahoo_icon.png"), "Add Yahoo Street layer", self.iface.mainWindow())
    self.actionAddYahooHybrid = QAction(QIcon(":/plugins/openlayers/yahoo_icon.png"), "Add Yahoo Hybrid layer", self.iface.mainWindow())
    self.actionAddYahooSatellite = QAction(QIcon(":/plugins/openlayers/yahoo_icon.png"), "Add Yahoo Satellite layer", self.iface.mainWindow())

    # connect the action to the run method
    QObject.connect(self.actionAddOSM, SIGNAL("triggered()"), self.addOSM)
    QObject.connect(self.actionAddGooglePhysical, SIGNAL("triggered()"), self.addGooglePhysical)
    QObject.connect(self.actionAddGoogleStreets, SIGNAL("triggered()"), self.addGoogleStreets)
    QObject.connect(self.actionAddGoogleHybrid, SIGNAL("triggered()"), self.addGoogleHybrid)
    QObject.connect(self.actionAddGoogleSatellite, SIGNAL("triggered()"), self.addGoogleSatellite)
    QObject.connect(self.actionAddYahooStreet, SIGNAL("triggered()"), self.addYahooStreet)
    QObject.connect(self.actionAddYahooHybrid, SIGNAL("triggered()"), self.addYahooHybrid)
    QObject.connect(self.actionAddYahooSatellite, SIGNAL("triggered()"), self.addYahooSatellite)

    # Add toolbar button and menu item
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddOSM)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddGooglePhysical)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddGoogleStreets)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddGoogleHybrid)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddGoogleSatellite)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddYahooStreet)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddYahooHybrid)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddYahooSatellite)

    if not self.__setCoordRSGoogle():
      QMessageBox.critical(self.iface.mainWindow(), "OpenLayers Plugin", "Could not set Google projection!")
      return

    # Register plugin layer type
    QgsPluginLayerRegistry.instance().addPluginLayerType(OpenlayersPluginLayerType(self.iface, self.setReferenceLayer, self.__coordRSGoogle))

    self.layer = None
    QObject.connect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.scaleChanged)
    QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)

  def unload(self):
    # Remove the plugin menu item and icon
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddOSM)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddGooglePhysical)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddGoogleStreets)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddGoogleHybrid)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddGoogleSatellite)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddYahooStreet)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddYahooHybrid)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddYahooSatellite)

    # Unregister plugin layer type
    QgsPluginLayerRegistry.instance().removePluginLayerType(OpenlayersLayer.LAYER_TYPE)

    QObject.disconnect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.scaleChanged)
    QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)

  def addLayer(self, layerName, layerType):

    self.__setMapSrsGoogle()

    layer = OpenlayersLayer(self.iface, self.__coordRSGoogle)
    layer.setLayerName(layerName)
    layer.setLayerType(layerType)
    if layer.isValid():
      QgsMapLayerRegistry.instance().addMapLayer(layer)

      # last added layer is new reference
      self.setReferenceLayer(layer)

  def addOSM(self):
    self.addLayer("OpenStreetMap", OpenlayersLayer.LAYER_OSM)

  def addGooglePhysical(self):
    self.addLayer("Google Physical", OpenlayersLayer.LAYER_GOOGLE_PHYSICAL)

  def addGoogleStreets(self):
    self.addLayer("Google Streets", OpenlayersLayer.LAYER_GOOGLE_STREETS)

  def addGoogleHybrid(self):
    self.addLayer("Google Hybrid", OpenlayersLayer.LAYER_GOOGLE_HYBRID)

  def addGoogleSatellite(self):
    self.addLayer("Google Satellite", OpenlayersLayer.LAYER_GOOGLE_SATELLITE)

  def addYahooStreet(self):
    self.addLayer("Yahoo Street", OpenlayersLayer.LAYER_YAHOO_STREET)

  def addYahooHybrid(self):
    self.addLayer("Yahoo Hybrid", OpenlayersLayer.LAYER_YAHOO_HYBRID)

  def addYahooSatellite(self):
    self.addLayer("Yahoo Satellite", OpenlayersLayer.LAYER_YAHOO_SATELLITE)

  def scaleChanged(self, scale):
    if scale > 0 and self.layer != None:
      # get OpenLayers scale for this extent
      olScale = self.layer.scaleFromExtent(self.iface.mapCanvas().extent())
      if olScale > 0.0:
        # calculate QGIS scale
        targetScale = olScale * self.iface.mapCanvas().mapRenderer().outputDpi() / 72.0
        qDebug("scaleChanged: %f - olScale: %f -> Canvas scale: %f" % (scale, olScale, targetScale) )
        # NOTE: use a slightly smaller scale to avoid zoomout feedback loop
        targetScale *= 0.9
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
