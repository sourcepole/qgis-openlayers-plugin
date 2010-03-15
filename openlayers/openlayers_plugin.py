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
    # connect the action to the run method
    QObject.connect(self.actionAddOSM, SIGNAL("triggered()"), self.addOSM)
    QObject.connect(self.actionAddGooglePhysical, SIGNAL("triggered()"), self.addGooglePhysical)
    QObject.connect(self.actionAddGoogleStreets, SIGNAL("triggered()"), self.addGoogleStreets)
    QObject.connect(self.actionAddGoogleHybrid, SIGNAL("triggered()"), self.addGoogleHybrid)
    QObject.connect(self.actionAddGoogleSatellite, SIGNAL("triggered()"), self.addGoogleSatellite)

    # Add toolbar button and menu item
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddOSM)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddGooglePhysical)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddGoogleStreets)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddGoogleHybrid)
    self.iface.addPluginToMenu("OpenLayers plugin", self.actionAddGoogleSatellite)

    # Register plugin layer type
    QgsPluginLayerRegistry.instance().addPluginLayerType(OpenlayersPluginLayerType(self.iface, self.setReferenceLayer))

    self.layer = None
    QObject.connect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.scaleChanged)
    QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)

    # find or create Spherical Mercator SRS
    crs = QgsCoordinateReferenceSystem()
    crs.createFromProj4(OpenlayersLayer.SPHERICAL_MERCATOR_PROJ4)
    self.sphericalMercatorSrsId = crs.srsid()
    self.sphericalMercatorEpsg = crs.epsg()
    print "Spherical Mercator coordinate reference system is:\n  %s\n  EPSG:%d\n  SRS ID = %d" % (crs.description(), crs.epsg(), crs.srsid())

  def unload(self):
    # Remove the plugin menu item and icon
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddOSM)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddGooglePhysical)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddGoogleStreets)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddGoogleHybrid)
    self.iface.removePluginMenu("OpenLayers plugin",self.actionAddGoogleSatellite)

    # Unregister plugin layer type
    QgsPluginLayerRegistry.instance().removePluginLayerType(OpenlayersLayer.LAYER_TYPE)

    QObject.disconnect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.scaleChanged)
    QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)

  def addLayer(self, layerName, layerType):
    # show instructions how to setup project
    if not self.iface.mapCanvas().hasCrsTransformEnabled() or self.iface.mapCanvas().mapRenderer().destinationSrs().srsid() != self.sphericalMercatorSrsId:
      QMessageBox.information(None, "OpenLayers Plugin", "Use the following project properties for OpenLayers layers:\n\n- Enable on the fly projection\n- Select Google Mercator SRS (EPSG:%d)" % self.sphericalMercatorEpsg)

    layer = OpenlayersLayer(self.iface)
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

  def scaleChanged(self, scale):
    if scale > 0 and self.layer != None:
      # get OpenLayers scale for this extent
      olScale = self.layer.scaleFromExtent(self.iface.mapCanvas().extent())
      if olScale > 0.0:
        # calculate QGIS scale
        targetScale = olScale * self.iface.mapCanvas().mapRenderer().outputDpi() / 72.0
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
