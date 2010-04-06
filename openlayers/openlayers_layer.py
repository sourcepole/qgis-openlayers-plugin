# -*- coding: utf-8 -*-
"""
/***************************************************************************
OpenLayers Plugin
A QGIS plugin

                             -------------------
begin                : 2010-02-03
copyright            : (C) 2010 by Pirmin Kalberer, Sourcepole
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

import os.path
import math

class OLWebPage(QWebPage):
  def __init__(self, parent = None):
    QWebPage.__init__(self, parent)

  def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
    qDebug( "%s[%d]: %s" % (sourceID, lineNumber, message) )

class OpenlayersLayer(QgsPluginLayer):

  LAYER_TYPE = "openlayers"
  MAX_ZOOM_LEVEL = 15
  SCALE_ON_MAX_ZOOM = 13540 # QGIS scale for 72 dpi

  LAYER_GOOGLE_PHYSICAL =  0
  LAYER_GOOGLE_STREETS =   1
  LAYER_GOOGLE_HYBRID =    2
  LAYER_GOOGLE_SATELLITE = 3
  LAYER_OSM =              4
  LAYER_YAHOO_STREET =     5
  LAYER_YAHOO_HYBRID =     6
  LAYER_YAHOO_SATELLITE =  7

  # use Proj4 result of QGIS Google Mercator
  SPHERICAL_MERCATOR_PROJ4 = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"

  def __init__(self, iface):
    QgsPluginLayer.__init__(self, OpenlayersLayer.LAYER_TYPE, "OpenLayers plugin layer")
    self.setValid(True)

    crs = QgsCoordinateReferenceSystem()
    crs.createFromProj4(OpenlayersLayer.SPHERICAL_MERCATOR_PROJ4)
    self.setCrs(crs)

    self.setExtent(QgsRectangle(-20037508.34, -20037508.34, 20037508.34, 20037508.34))

    self.iface = iface
    self.loaded = False
    self.page = None
    self.ext = None

    self.setLayerType(OpenlayersLayer.LAYER_GOOGLE_PHYSICAL)

  def draw(self, rendererContext):
    qDebug("OpenlayersLayer draw")

    if not self.loaded:
      self.page = OLWebPage()
      url = "file:///" + os.path.dirname( __file__ ).replace("\\", "/") + "/html/" + self.html
      qDebug( "page file: %s" % url )
      self.page.mainFrame().load(QUrl(url))
      QObject.connect(self.page, SIGNAL("loadFinished(bool)"), self.loadFinished)
    else:
      self.render(rendererContext)

    return True

  def loadFinished(self, ok):
    qDebug("OpenlayersLayer loadFinished %d" % ok)
    if ok:
      self.loaded = ok
      self.emit(SIGNAL("repaintRequested()"))

  def render(self, rendererContext):
    qDebug(" extent: %s" % rendererContext.extent().toString() )
    qDebug(" center: %lf, %lf" % (rendererContext.extent().center().x(), rendererContext.extent().center().y() ) )
    qDebug(" size: %d, %d" % (rendererContext.painter().viewport().size().width(), rendererContext.painter().viewport().size().height() ) )

    self.page.setViewportSize(rendererContext.painter().viewport().size())

    if rendererContext.extent() != self.ext:
      self.ext = rendererContext.extent()
      self.page.mainFrame().evaluateJavaScript("map.zoomToExtent(new OpenLayers.Bounds(%f, %f, %f, %f));" % (self.ext.xMinimum(), self.ext.yMinimum(), self.ext.xMaximum(), self.ext.yMaximum()))
      #Workaround: wait for images to be loaded. Use OL event listener instead
      QTimer.singleShot(1000, self, SIGNAL("repaintRequested()"))

    rendererContext.painter().save()

    self.page.mainFrame().render(rendererContext.painter())
    rendererContext.painter().restore()

  def readXml(self, node):
    # custom properties
    self.setLayerType( int(node.toElement().attribute("ol_layer_type", "%d" % OpenlayersLayer.LAYER_GOOGLE_PHYSICAL)) )
    return True

  def writeXml(self, node, doc):
    element = node.toElement();
    # write plugin layer type to project (essential to be read from project)
    element.setAttribute("type", "plugin")
    element.setAttribute("name", OpenlayersLayer.LAYER_TYPE);
    # custom properties
    element.setAttribute("ol_layer_type", str(self.layerType))
    return True

  def setLayerType(self, layerType):
    self.layerType = layerType
    layerSelect = {
      OpenlayersLayer.LAYER_GOOGLE_PHYSICAL : "google_physical.html",
      OpenlayersLayer.LAYER_GOOGLE_STREETS : "google_streets.html",
      OpenlayersLayer.LAYER_GOOGLE_HYBRID : "google_hybrid.html",
      OpenlayersLayer.LAYER_GOOGLE_SATELLITE : "google_satellite.html",
      OpenlayersLayer.LAYER_OSM : "osm.html",
      OpenlayersLayer.LAYER_YAHOO_STREET : "yahoo_street.html",
      OpenlayersLayer.LAYER_YAHOO_HYBRID : "yahoo_hybrid.html",
      OpenlayersLayer.LAYER_YAHOO_SATELLITE : "yahoo_satellite.html"
    }
    self.html = layerSelect.get(layerType, "google_physical.html")

  def scaleFromExtent(self, extent):
    if self.page != None:
      # get OpenLayers scale
      self.page.mainFrame().evaluateJavaScript("map.zoomToExtent(new OpenLayers.Bounds(%f, %f, %f, %f));" % (extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()))
      scale = self.page.mainFrame().evaluateJavaScript("map.getScale()")
      if scale.isNull():
        print "OpenlayersLayer Warning: Could not get scale from OpenLayers map"
        return 0.0
      else:
        return float(scale.toString())
    else:
      return 0.0
