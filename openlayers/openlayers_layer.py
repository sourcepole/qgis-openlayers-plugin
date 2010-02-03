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

class OpenlayersLayer(QgsPluginLayer):

  LAYER_TYPE="openlayers"

  def __init__(self):
    QgsPluginLayer.__init__(self, OpenlayersLayer.LAYER_TYPE, "OpenLayers plugin layer")
    self.setValid(True)

    crs = QgsCoordinateReferenceSystem()
    crs.createFromEpsg(900913)
    self.setCrs(crs)

    self.loaded = False

  def draw(self, rendererContext):
    print "OpenlayersLayer draw"

    if not self.loaded:
      self.page = QWebPage()
      self.page.mainFrame().load(QUrl("file:///home/pi/apps/share/qgis/python/plugins/openlayers/html/google.html"))
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
    print "size", rendererContext.painter().viewport().size()

    self.page.setViewportSize(rendererContext.painter().viewport().size())
    self.page.mainFrame().render(rendererContext.painter())

    #Example http://doc.trolltech.com/4.6/qwebpage.html#details
    #self.page.setViewportSize(self.page.mainFrame().contentsSize())
    #image = QImage(self.page.viewportSize(), QImage.Format_ARGB32)
    #webpainter = QPainter(image)
    #self.page.mainFrame().render(webpainter)
    #webpainter.end()

    ##QImage thumbnail = image.scaled(400, 400);
    ##thumbnail.save("thumbnail.png");

    #painter = rendererContext.painter()
    #painter.drawImage(QPoint(0,0), image)

  def writeXml(self, node, doc):
    element = node.toElement();
    # write plugin layer type to project (essential to be read from project)
    element.setAttribute("type", "plugin")
    element.setAttribute("name", OpenlayersLayer.LAYER_TYPE);
    return True
