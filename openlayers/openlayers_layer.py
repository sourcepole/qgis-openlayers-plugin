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

import os.path
import math

class OLWebPage(QWebPage):
  def __init__(self, parent = None):
    QWebPage.__init__(self, parent)
    self.__manager = None # Need persist for PROXY
    # Set Proxy in webpage
    proxy = self.__getProxy()
    if not proxy is None:
      self.__manager = QNetworkAccessManager()
      self.__manager.setProxy(proxy)
      self.setNetworkAccessManager(self.__manager)    

  def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
    qDebug( "%s[%d]: %s" % (sourceID, lineNumber, message) )

  def __getProxy(self):
    # Adaption by source of "Plugin Installer - Version 1.0.10" 
    settings = QSettings()
    settings.beginGroup("proxy")
    if settings.value("/proxyEnabled").toBool():
      proxy = QNetworkProxy()
      proxyType = settings.value( "/proxyType", QVariant(0)).toString()
      if proxyType in ["1","Socks5Proxy"]: proxy.setType(QNetworkProxy.Socks5Proxy)
      elif proxyType in ["2","NoProxy"]: proxy.setType(QNetworkProxy.NoProxy)
      elif proxyType in ["3","HttpProxy"]: proxy.setType(QNetworkProxy.HttpProxy)
      elif proxyType in ["4","HttpCachingProxy"] and QT_VERSION >= 0X040400: proxy.setType(QNetworkProxy.HttpCachingProxy)
      elif proxyType in ["5","FtpCachingProxy"] and QT_VERSION >= 0X040400: proxy.setType(QNetworkProxy.FtpCachingProxy)
      else: proxy.setType(QNetworkProxy.DefaultProxy)
      proxy.setHostName(settings.value("/proxyHost").toString())
      proxy.setPort(settings.value("/proxyPort").toUInt()[0])
      proxy.setUser(settings.value("/proxyUser").toString())
      proxy.setPassword(settings.value("/proxyPassword").toString())
      return proxy
    else:
      return None
    settings.endGroup()


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

  def __init__(self, iface, coordRSGoogle):
    QgsPluginLayer.__init__(self, OpenlayersLayer.LAYER_TYPE, "OpenLayers plugin layer")
    self.setValid(True)
    self.setCrs(coordRSGoogle)

    self.setExtent(QgsRectangle(-20037508.34, -20037508.34, 20037508.34, 20037508.34))

    self.iface = iface
    self.loaded = False
    self.page = OLWebPage()
    self.ext = None

    self.timer = QTimer()
    self.timer.setSingleShot(True)
    self.timer.setInterval(500)
    QObject.connect(self.timer, SIGNAL("timeout()"), self.finalRepaint)

    self.timerMax = QTimer()
    self.timerMax.setSingleShot(True)
    self.timerMax.setInterval(5000) # TODO: different timeouts for google/yahoo?
    QObject.connect(self.timerMax, SIGNAL("timeout()"), self.finalRepaint)

    self.setLayerType(OpenlayersLayer.LAYER_GOOGLE_PHYSICAL)

  def draw(self, rendererContext):
    qDebug("OpenlayersLayer draw")

    if not self.loaded:
      self.page = OLWebPage()
      url = "file:///" + os.path.dirname( __file__ ).replace("\\", "/") + "/html/" + self.html
      qDebug( "page file: %s" % url )
      self.page.mainFrame().load(QUrl(url))
      QObject.connect(self.page, SIGNAL("loadFinished(bool)"), self.loadFinished)
      if self.layerType != OpenlayersLayer.LAYER_OSM:
        QObject.connect(self.page, SIGNAL("repaintRequested(QRect)"), self.pageRepaintRequested)
    else:
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

    if self.layerType == OpenlayersLayer.LAYER_OSM:
      # wait for OpenLayers to finish loading
      # NOTE: does not work with Google and Yahoo layers as they do not emit loadstart and loadend events
      loadEnd = False
      while not loadEnd:
        loadEndOL = self.page.mainFrame().evaluateJavaScript("loadEnd")
        if not loadEndOL.isNull():
          loadEnd = loadEndOL.toBool()
        else:
          qDebug("OpenlayersLayer Warning: Could not get loadEnd")
          break
        qApp.processEvents()
    else:
      # wait for timeout after pageRepaintRequested
      self.repaintEnd = False
      self.timerMax.start()
      while not self.repaintEnd:
        qApp.processEvents()
      self.timerMax.stop()

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

