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
from PyQt4.QtNetwork import *
from qgis.core import *

from tools_network import getProxy

import os.path
import math

class OLWebPage(QWebPage):
  def __init__(self, parent = None):
    QWebPage.__init__(self, parent)
    self.__manager = None # Need persist for PROXY
    # Set Proxy in webpage
    proxy = getProxy()
    if not proxy is None:
      self.__manager = QNetworkAccessManager()
      self.__manager.setProxy(proxy)
      self.setNetworkAccessManager(self.__manager)    

  def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
    qDebug( "%s[%d]: %s" % (sourceID, lineNumber, message) )


class OpenlayersLayer(QgsPluginLayer):

  LAYER_TYPE = "openlayers"
  MAX_ZOOM_LEVEL = 15
  SCALE_ON_MAX_ZOOM = 13540 # QGIS scale for 72 dpi

  def __init__(self, iface, coordRSGoogle, olLayerTypeRegistry):
    QgsPluginLayer.__init__(self, OpenlayersLayer.LAYER_TYPE, "OpenLayers plugin layer")
    self.setValid(True)
    self.setCrs(coordRSGoogle)
    self.olLayerTypeRegistry = olLayerTypeRegistry

    self.setExtent(QgsRectangle(-20037508.34, -20037508.34, 20037508.34, 20037508.34))

    self.iface = iface
    self.loaded = False
    self.page = OLWebPage()
    self.ext = None
    self.olResolutions = None

    self.lastRenderedImage = None
    self.lastExtent = None
    self.lastViewPortSize = None
    self.lastLogicalDpi = None
    self.lastOutputDpi = None
    self.lastMapUnitsPerPixel = None

    self.timer = QTimer()
    self.timer.setSingleShot(True)
    self.timer.setInterval(500)
    QObject.connect(self.timer, SIGNAL("timeout()"), self.finalRepaint)

    self.timerMax = QTimer()
    self.timerMax.setSingleShot(True)
    self.timerMax.setInterval(5000) # TODO: different timeouts for google/yahoo?
    QObject.connect(self.timerMax, SIGNAL("timeout()"), self.finalRepaint)

    # timeout for loadEnd event
    self.timerLoadEnd = QTimer()
    self.timerLoadEnd.setSingleShot(True)
    self.timerLoadEnd.setInterval(5000)
    QObject.connect(self.timerLoadEnd, SIGNAL("timeout()"), self.loadEndTimeout)

    self.setLayerType( self.olLayerTypeRegistry.getById(0) )

  def draw(self, rendererContext):
    qDebug("OpenlayersLayer draw")

    if not self.loaded:
      self.page = OLWebPage()
      url = "file:///" + os.path.dirname( __file__ ).replace("\\", "/") + "/html/" + self.layerType.html
      qDebug( "page file: %s" % url )
      self.page.mainFrame().load(QUrl(url))
      QObject.connect(self.page, SIGNAL("loadFinished(bool)"), self.loadFinished)
      if not self.layerType.emitsLoadEnd:
        QObject.connect(self.page, SIGNAL("repaintRequested(QRect)"), self.pageRepaintRequested)

      # wait for page to finish loading
      while not self.loaded:
        qApp.processEvents()

    self.render(rendererContext)

    return True

  def pageRepaintRequested(self, rect):
    if self.loaded:
      self.timer.stop()
      self.repaintEnd = False
      self.timer.start()
    else:
      self.repaintEnd = True

  def finalRepaint(self):
    self.repaintEnd = True

  def loadFinished(self, ok):
    #qDebug("OpenlayersLayer loadFinished %d" % ok)
    if ok:
      self.loaded = ok
      self.emit(SIGNAL("repaintRequested()"))

  def loadEndTimeout(self):
    self.loadEnd = True

  def render(self, rendererContext):
    qDebug(" extent: %s" % rendererContext.extent().toString() )
    qDebug(" center: %lf, %lf" % (rendererContext.extent().center().x(), rendererContext.extent().center().y() ) )
    qDebug(" size: %d, %d" % (rendererContext.painter().viewport().size().width(), rendererContext.painter().viewport().size().height() ) )
    qDebug(" logicalDpiX: %d" % rendererContext.painter().device().logicalDpiX() )
    qDebug(" outputDpi: %lf" % self.iface.mapCanvas().mapRenderer().outputDpi() )
    qDebug(" mapUnitsPerPixel: %d" % rendererContext.mapToPixel().mapUnitsPerPixel() )
    #qDebug(" rasterScaleFactor: %s" % str(rendererContext.rasterScaleFactor()) )
    #qDebug(" outputSize: %d, %d" % (self.iface.mapCanvas().mapRenderer().outputSize().width(), self.iface.mapCanvas().mapRenderer().outputSize().height() ) )
    #qDebug(" scale: %lf" % self.iface.mapCanvas().mapRenderer().scale() )

    if self.lastExtent != rendererContext.extent() or self.lastViewPortSize != rendererContext.painter().viewport().size() or self.lastLogicalDpi != rendererContext.painter().device().logicalDpiX() or self.lastOutputDpi != self.iface.mapCanvas().mapRenderer().outputDpi() or self.lastMapUnitsPerPixel != rendererContext.mapToPixel().mapUnitsPerPixel():
      olSize = rendererContext.painter().viewport().size()
      if rendererContext.painter().device().logicalDpiX() != int(self.iface.mapCanvas().mapRenderer().outputDpi()):
        # use screen dpi for printing
        sizeFact = self.iface.mapCanvas().mapRenderer().outputDpi() / 25.4 / rendererContext.mapToPixel().mapUnitsPerPixel()
        olSize.setWidth(rendererContext.extent().width() * sizeFact)
        olSize.setHeight(rendererContext.extent().height() * sizeFact)
      qDebug(" olSize: %d, %d" % (olSize.width(), olSize.height()) )
      self.page.setViewportSize(olSize)
      targetWidth = olSize.width()
      targetHeight = olSize.height()

      # find best resolution or use last
      qgisRes = rendererContext.extent().width() / targetWidth
      for res in self.resolutions():
        olRes = res
        if qgisRes >= res:
          break

      # adjust OpenLayers viewport to match QGIS extent
      olWidth = rendererContext.extent().width() / olRes
      olHeight = rendererContext.extent().height() / olRes
      qDebug("  adjust viewport: %f -> %f: %f x %f" % (qgisRes, olRes, olWidth, olHeight))
      self.page.setViewportSize(QSize(olWidth, olHeight))

      if rendererContext.extent() != self.ext:
        qDebug("updating OpenLayers extent" )
        self.ext = rendererContext.extent() #FIXME: store seperate for each rendererContext
        self.page.mainFrame().evaluateJavaScript("map.zoomToExtent(new OpenLayers.Bounds(%f, %f, %f, %f), true);" % (self.ext.xMinimum(), self.ext.yMinimum(), self.ext.xMaximum(), self.ext.yMaximum()))

      if self.layerType.emitsLoadEnd:
        # wait for OpenLayers to finish loading
        # NOTE: does not work with Google and Yahoo layers as they do not emit loadstart and loadend events
        self.loadEnd = False
        self.timerLoadEnd.start()
        while not self.loadEnd:
          loadEndOL = self.page.mainFrame().evaluateJavaScript("loadEnd")
          #if not loadEndOL.isNull():
          if not loadEndOL == None:
            self.loadEnd = loadEndOL
          else:
            qDebug("OpenlayersLayer Warning: Could not get loadEnd")
            break
          qApp.processEvents()
        self.timerLoadEnd.stop()
      else:
        # wait for timeout after pageRepaintRequested
        self.repaintEnd = False
        self.timerMax.start()
        while not self.repaintEnd:
          qApp.processEvents()
        self.timerMax.stop()

      #Render WebKit page into rendererContext
      rendererContext.painter().save()
      if rendererContext.painter().device().logicalDpiX() != int(self.iface.mapCanvas().mapRenderer().outputDpi()):
        printScale = 25.4 / self.iface.mapCanvas().mapRenderer().outputDpi() # OL DPI to printer pixels
        rendererContext.painter().scale(printScale, printScale)

      # render OpenLayers to image
      img = QImage(olWidth, olHeight, QImage.Format_ARGB32_Premultiplied)
      painter = QPainter(img)
      self.page.mainFrame().render(painter)
      painter.end()

      if olWidth != targetWidth or olHeight != targetHeight:
        # scale using QImage for better quality
        img = img.scaled(targetWidth, targetHeight, Qt.KeepAspectRatio, Qt.SmoothTransformation )
        qDebug("  scale image: %i x %i -> %i x %i" % (olWidth, olHeight, targetWidth, targetHeight,))
    else:
      img = self.lastRenderedImage

    # draw to rendererContext
    rendererContext.painter().drawImage(0, 0, img)
    rendererContext.painter().restore()

    self.lastRenderedImage = img
    self.lastExtent = rendererContext.extent()
    self.lastViewPortSize = rendererContext.painter().viewport().size()
    self.lastLogicalDpi = rendererContext.painter().device().logicalDpiX()
    self.lastOutputDpi = self.iface.mapCanvas().mapRenderer().outputDpi()
    self.lastMapUnitsPerPixel = rendererContext.mapToPixel().mapUnitsPerPixel()

  def readXml(self, node):
    # custom properties
    self.setLayerType( self.olLayerTypeRegistry.getById( int(node.toElement().attribute("ol_layer_type", "0")) ) )
    return True

  def writeXml(self, node, doc):
    element = node.toElement();
    # write plugin layer type to project (essential to be read from project)
    element.setAttribute("type", "plugin")
    element.setAttribute("name", OpenlayersLayer.LAYER_TYPE);
    # custom properties
    element.setAttribute("ol_layer_type", str(self.layerType.id))
    return True

  def setLayerType(self, layerType):
    self.layerType = layerType

  def scaleFromExtent(self, extent):
    if self.page != None:
      # get OpenLayers scale
      #self.page.mainFrame().evaluateJavaScript("console.debug(\"[scaleChanged] map.getExtent: \" + map.getExtent());")
      self.page.mainFrame().evaluateJavaScript("map.zoomToExtent(new OpenLayers.Bounds(%f, %f, %f, %f));" % (extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()))
      #self.page.mainFrame().evaluateJavaScript("console.debug(\"[scaleChanged] map.getExtent: \" + map.getExtent());")
      scale = self.page.mainFrame().evaluateJavaScript("map.getScale()")
      if scale.isNull():
        qDebug("OpenlayersLayer Warning: Could not get scale from OpenLayers map")
        return 0.0
      else:
        return float(scale.toString())
    else:
      return 0.0

  def resolutions(self):
    if self.olResolutions == None:
      # get OpenLayers resolutions
      resVariant = self.page.mainFrame().evaluateJavaScript("map.layers[0].resolutions")
      self.olResolutions = resVariant
      #for res in resVariant.toList():
      #  self.olResolutions.append(res.toDouble()[0])
    return self.olResolutions
