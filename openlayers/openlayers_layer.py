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

class OpenlayersLayer(QgsPluginLayer):

  LAYER_TYPE = "openlayers"
  MAX_ZOOM_LEVEL = 15
  SCALE_ON_MAX_ZOOM = 13540 # QGIS scale for 72 dpi

  LAYER_GOOGLE_PHYSICAL =  0
  LAYER_GOOGLE_STREETS =   1
  LAYER_GOOGLE_HYBRID =    2
  LAYER_GOOGLE_SATELLITE = 3

  # use Proj4 result of QGIS Google Mercator
  SPHERICAL_MERCATOR_PROJ4 = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0+units=m +nadgrids=@null +no_defs"

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

    self.setLayerType(OpenlayersLayer.LAYER_GOOGLE_PHYSICAL)

  def draw(self, rendererContext):
    print "OpenlayersLayer draw"

    if not self.loaded:
      self.page = QWebPage()
      self.page.mainFrame().load(QUrl(os.path.dirname( __file__ ) + "/html/" + self.html))
      QObject.connect(self.page, SIGNAL("loadFinished(bool)"), self.loadFinished)
      QObject.connect(self.page, SIGNAL("loadProgress(int)"), self.loadProgress)
    else:
      self.render(rendererContext)

    return True

  def loadProgress(self, progress):
    print "OpenlayersLayer loadProgress", progress

  def loadFinished(self, ok):
    print "OpenlayersLayer loadFinished", ok
    if ok:
      self.loaded = ok
      self.emit(SIGNAL("repaintRequested()"))

  def render(self, rendererContext):
    print "extent", rendererContext.extent().toString()
    print "center", rendererContext.extent().center().x(), rendererContext.extent().center().y()
    print "size", rendererContext.painter().viewport().size()

    self.page.setViewportSize(rendererContext.painter().viewport().size())

    extent = rendererContext.extent()
    self.page.mainFrame().evaluateJavaScript("map.zoomToExtent(new OpenLayers.Bounds(%f, %f, %f, %f));" % (extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()))

    rendererContext.painter().save()

    # draw transparent on intermediate zoom levels
    qgisScale = self.iface.mapCanvas().scale()
    zoom = OpenlayersLayer.zoomFromScale(qgisScale, self.iface.mapCanvas().mapRenderer().outputDpi())
    zoomLevel = math.floor(zoom + 0.5)
    if math.fabs(zoom - zoomLevel) < 0.000001:
      # draw normal
      self.page.mainFrame().render(rendererContext.painter())
    else:
      # draw transparent
      image = QImage(self.page.viewportSize(), QImage.Format_ARGB32)
      imgPainter = QPainter(image)
      self.page.mainFrame().render(imgPainter)
      imgPainter.end()
      rendererContext.painter().setOpacity(0.2)
      rendererContext.painter().drawImage(QPoint(0,0), image)

    rendererContext.painter().restore()

  def readXml(self, node):
    # custom properties
    self.setLayerType( node.toElement().attribute("ol_layer_type", "%d" % OpenlayersLayer.LAYER_GOOGLE_PHYSICAL) )
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
    }
    self.html = layerSelect.get(layerType, "google_physical.html")

  def scaleFromZoom(zoom, dpi):
    scale_on_max_zoom = OpenlayersLayer.SCALE_ON_MAX_ZOOM * dpi / 72.0
    return math.pow(2, (OpenlayersLayer.MAX_ZOOM_LEVEL - zoom)) * scale_on_max_zoom
  scaleFromZoom = staticmethod(scaleFromZoom)

  def zoomFromScale(scale, dpi):
    scale_on_max_zoom = OpenlayersLayer.SCALE_ON_MAX_ZOOM * dpi / 72.0
    return OpenlayersLayer.MAX_ZOOM_LEVEL - math.log((scale / scale_on_max_zoom), 2)
  zoomFromScale = staticmethod(zoomFromScale)
