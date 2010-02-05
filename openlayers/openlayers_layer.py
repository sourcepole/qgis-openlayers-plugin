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

# TODO: add projection to QGIS
# OpenLayers Spherical Mercator
# +proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs

class OpenlayersLayer(QgsPluginLayer):

  LAYER_TYPE="openlayers"

  def __init__(self):
    QgsPluginLayer.__init__(self, OpenlayersLayer.LAYER_TYPE, "OpenLayers plugin layer")
    self.setValid(True)

    crs = QgsCoordinateReferenceSystem()
    crs.createFromProj4("+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs")
    self.setCrs(crs)

    self.loaded = False
    self.page = None

  def draw(self, rendererContext):
    print "OpenlayersLayer draw"

    if not self.loaded:
      self.page = QWebPage()
      self.page.mainFrame().load(QUrl(os.path.dirname( __file__ ) + "/html/google.html"))
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

    # OpenLayers scale (72 dpi) to QGIS scale (90 dpi)
    scale = self.page.mainFrame().evaluateJavaScript("map.getScale()")
    qgis_scale = float(scale.toString()) * 90.0/72.0
    print "OpenLayers scale:", scale.toString(), " -> QGIS Scale: <", qgis_scale

    self.page.mainFrame().render(rendererContext.painter())

  def writeXml(self, node, doc):
    element = node.toElement();
    # write plugin layer type to project (essential to be read from project)
    element.setAttribute("type", "plugin")
    element.setAttribute("name", OpenlayersLayer.LAYER_TYPE);
    return True
