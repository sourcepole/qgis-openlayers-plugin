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

class OpenlayersLayer(QgsMapLayer):
  def __init__(self, *args):
    QgsMapLayer.__init__(self, *args)

    crs = QgsCoordinateReferenceSystem()
    crs.createFromEpsg(900913)
    self.setCrs(crs)

    self.loaded = False

  def isEditable(self):
    return False

  def __del__(self):
    print "OpenlayersLayer removed"

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
    # write plugin layer type to project
    element.setAttribute("type", "openlayers");
    return True

#------------------------------------------------------------------------------

class OpenlayersLayerCreator(QgsPluginLayerCreator):
  def __init__(self, createCallback):
    QgsPluginLayerCreator.__init__(self)
    self.createCallback = createCallback

  def createLayer(self, layerNode):
    return self.createCallback(layerNode)

#------------------------------------------------------------------------------

class OpenlayersPlugin:

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface

    self.creator = OpenlayersLayerCreator(self.createLayer)
    self.layers = []

  def initGui(self):
    # Create action that will start plugin configuration
    self.action = QAction(QIcon(":/plugins/openlayers/icon.png"), "Add OpenLayers layer", self.iface.mainWindow())
    # connect the action to the run method
    QObject.connect(self.action, SIGNAL("triggered()"), self.run)

    # Add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    self.iface.addPluginToMenu("OpenLayers plugin", self.action)

    self.creatorId = QgsPluginLayerRegistry.instance().addCreator(self.creator)
    # handle layer remove
    QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)

  def unload(self):
    # Remove the plugin menu item and icon
    self.iface.removePluginMenu("OpenLayers plugin",self.action)
    self.iface.removeToolBarIcon(self.action)

    QgsPluginLayerRegistry.instance().removeCreator(self.creatorId)
    QObject.disconnect(QgsMapLayerRegistry.instance(), SIGNAL("layerWillBeRemoved(QString)"), self.removeLayer)

  def run(self):
    layer = OpenlayersLayer(QgsMapLayer.PluginLayer, "Plugin Layer", "")
    if layer.isValid():
      self.layers.append(layer)
      QgsMapLayerRegistry.instance().addMapLayer(layer)

  def createLayer(self, layerNode):
    layer = None

    # read layer type
    element = layerNode.toElement();
    layerType = element.attribute("type");
    if layerType == "openlayers":
      layer = OpenlayersLayer(QgsMapLayer.PluginLayer)
      self.layers.append(layer)

    return layer

  def removeLayer(self, layerId):
    layerToRemove = None
    for layer in self.layers:
      # check if this is one of the plugin's layer
      if layer.getLayerID() == layerId:
        layerToRemove = layer
        break

    if layerToRemove != None:
      self.layers.remove(layerToRemove)
