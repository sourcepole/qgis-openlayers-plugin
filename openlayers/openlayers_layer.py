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
import PyQt4
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *
from qgis.core import *

from tools_network import getProxy

import os.path
import math

debug = 3

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


# this is a worker class which is responsible for fetching the map
# it resides normally in the gui thread, except when doind paint()
class OpenlayersWorker(QObject):

  startSignal = PyQt4.QtCore.pyqtSignal()
  doneSignal = PyQt4.QtCore.pyqtSignal()

  #def __init__(self, mapSettings, layerType):
  def __init__(self, rendererContext, mapSettings, layerType):

    QObject.__init__(self)

    if debug > 1:
      qDebug('OpenlayersWorker init - '+' - '+str(QThread.currentThreadId()))
    self.rendererContext = rendererContext
    self.mapSettings = mapSettings
    self.layerType = layerType

    self.loaded = False
    self.layerType = None
    self.page = OLWebPage()
    self.ext = None
    self.olResolutions = None

    self.lastRenderedImage = None
    self.lastExtent = None
    self.lastViewPortSize = None
    self.lastLogicalDpi = None
    self.lastOutputDpi = None
    self.lastMapUnitsPerPixel = None

    self.working = False

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

    self.startSignal.connect(self.startRender)

  def startRender(self):
    if debug > 1:
      qDebug('OpenlayersWorker startRender - '+str(QThread.currentThreadId()))
    #QThread.currentThread().sleep(2)
    self.working = True
    self.render()
    #self.doneRender()
    self.working = False
    self.doneSignal.emit()
    if debug > 1:
      qDebug('OpenlayersWorker startRender done')

#  def doneRender(self):
#    if debug > 1:
#      qDebug('OpenlayersWorker doneRender- '+str(QThread.currentThreadId()))
#    self.doneSignal.emit()

#  def paint(self):
#    if debug > 1:
#      qDebug('OpenlayersWorker paint- '+str(QThread.currentThreadId()))


# below copied from OpenlayersLayer

  def pageRepaintRequested(self, rect):
    if debug > 0:
      qDebug("OpenlayersLayer pageRepaintRequested")
    if self.loaded:
      self.timer.stop()
      self.repaintEnd = False
      self.timer.start()
    else:
      self.repaintEnd = True

  def finalRepaint(self):
    if debug > 0:
      qDebug("OpenlayersLayer finalRepaint")
    self.repaintEnd = True

  def loadFinished(self, ok):
    if debug > 0:
      qDebug("OpenlayersLayer loadFinished %d" % ok)
    if ok:
      self.loaded = ok
      self.emit(SIGNAL("repaintRequested()"))

  def loadEndTimeout(self):
    if debug > 0:
      qDebug("OpenlayersLayer loadEndTimeout")
    self.loadEnd = True

  # copied from OpenlayersLayer draw() and render()
  def render(self):
    
    if debug > 0:
      qDebug("OpenlayersWorker render "+str(QThread.currentThreadId()))

    rendererContext = self.rendererContext

    if not rendererContext or rendererContext.renderingStopped():
      return False

    if not self.loaded:
      self.page = OLWebPage()
      url = "file:///" + os.path.dirname( __file__ ).replace("\\", "/") + "/html/" + self.layerType.html
      if debug > 1:
        qDebug( "page file: %s" % url )
      self.page.mainFrame().load(QUrl(url))
      QObject.connect(self.page, SIGNAL("loadFinished(bool)"), self.loadFinished)
      if not self.layerType.emitsLoadEnd:
        QObject.connect(self.page, SIGNAL("repaintRequested(QRect)"), self.pageRepaintRequested)

      # wait for page to finish loading
      if debug > 2:
        qDebug("OpenlayersWorker waiting for page to load")
      while not self.loaded:
        qApp.processEvents()
      if debug > 2:
        qDebug("OpenlayersWorker page loaded")

    outputDpi = self.mapSettings.outputDpi()
    if debug > 2:
      qDebug(" extent: %s" % rendererContext.extent().toString() )
      qDebug(" center: %lf, %lf" % (rendererContext.extent().center().x(), rendererContext.extent().center().y() ) )
      qDebug(" size: %d, %d" % (rendererContext.painter().viewport().size().width(), rendererContext.painter().viewport().size().height() ) )
      qDebug(" logicalDpiX: %d" % rendererContext.painter().device().logicalDpiX() )
      qDebug(" outputDpi: %lf" %  outputDpi )
      qDebug(" mapUnitsPerPixel: %f" % rendererContext.mapToPixel().mapUnitsPerPixel() )
      #qDebug(" rasterScaleFactor: %s" % str(rendererContext.rasterScaleFactor()) )
      #qDebug(" outputSize: %d, %d" % (self.iface.mapCanvas().mapRenderer().outputSize().width(), self.iface.mapCanvas().mapRenderer().outputSize().height() ) )
      #qDebug(" scale: %lf" % self.iface.mapCanvas().mapRenderer().scale() )

    painter_saved = False

    if self.lastExtent != rendererContext.extent() or self.lastViewPortSize != rendererContext.painter().viewport().size() or self.lastLogicalDpi != rendererContext.painter().device().logicalDpiX() or self.lastOutputDpi != outputDpi or self.lastMapUnitsPerPixel != rendererContext.mapToPixel().mapUnitsPerPixel():
      olSize = rendererContext.painter().viewport().size()
      if rendererContext.painter().device().logicalDpiX() != int(outputDpi):
        # use screen dpi for printing
        #sizeFact = outputDpi / 25.4 / rendererContext.mapToPixel().mapUnitsPerPixel()
        sizeFact = 1
        olSize.setWidth(rendererContext.extent().width() * sizeFact)
        olSize.setHeight(rendererContext.extent().height() * sizeFact)
      if debug > 2:
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
      if debug > 2:
        qDebug("  adjust viewport: %f -> %f: %f x %f" % (qgisRes, olRes, olWidth, olHeight))
      self.page.setViewportSize(QSize(olWidth, olHeight))

      if rendererContext.extent() != self.ext:
        self.ext = rendererContext.extent() #FIXME: store seperate for each rendererContext
        if debug > 2:
          qDebug("updating OpenLayers extent (%f, %f, %f, %f)"  % (self.ext.xMinimum(), self.ext.yMinimum(), self.ext.xMaximum(), self.ext.yMaximum()))
        self.page.mainFrame().evaluateJavaScript("map.zoomToExtent(new OpenLayers.Bounds(%f, %f, %f, %f), true);" % (self.ext.xMinimum(), self.ext.yMinimum(), self.ext.xMaximum(), self.ext.yMaximum()))
        qDebug("OpenLayers extent updated" ) #FIXME: evaluateJavaScript logs "undefined[0]: TypeError: 'null' is not an object" when loading a project. JS var 'map' not initialized yet? 

      if self.layerType.emitsLoadEnd:
      #if False:
        if debug > 2:
          qDebug('waiting for loadEnd')
        # wait for OpenLayers to finish loading
        # NOTE: does not work with Google and Yahoo layers as they do not emit loadstart and loadend events
        self.loadEnd = False
        self.timerLoadEnd.start()
        while not self.loadEnd:
          loadEndOL = self.page.mainFrame().evaluateJavaScript("loadEnd")
          if debug > 3:
            qDebug('waiting '+str(rendererContext.renderingStopped())+' '+str(loadEndOL))
          #qDebug("loadEndOL: %d" % loadEndOL)
          #if not loadEndOL.isNull():
          if not loadEndOL == None:
            self.loadEnd = loadEndOL
          else:
            qDebug("OpenlayersLayer Warning: Could not get loadEnd")
            break
          qApp.processEvents()
        self.timerLoadEnd.stop()
        if debug > 2:
          qDebug('done waiting for loadEnd')
      else:
        if debug > 2:
          qDebug('waiting for pageRepaintRequested')
        # wait for timeout after pageRepaintRequested
        self.repaintEnd = False
        self.timerMax.start()
        while not self.repaintEnd:
          qApp.processEvents()
        self.timerMax.stop()
        if debug > 2:
          qDebug('done waiting for pageRepaintRequested')

      if debug > 2:
        qDebug("OpenlayersWorker rendering page to img")

      if not rendererContext or not rendererContext.painter():
        qDebug("OpenlayersWorker stopping rendering because renderingContext was deleted")
        return True

      if rendererContext.renderingStopped():
        qDebug("OpenlayersWorker stopping rendering because renderingContext stopped")
        return True

      #Render WebKit page into rendererContext
      print('before save')
      rendererContext.painter().save()
      print('after save')
      painter_saved = True
      if rendererContext.painter().device().logicalDpiX() != int(outputDpi):
        printScale = 25.4 / outputDpi # OL DPI to printer pixels
        rendererContext.painter().scale(printScale, printScale)

      # render OpenLayers to image
      img = QImage(olWidth, olHeight, QImage.Format_ARGB32_Premultiplied)
      painter = QPainter(img)
      self.page.mainFrame().render(painter)
      painter.end()

      if olWidth != targetWidth or olHeight != targetHeight:
        # scale using QImage for better quality
        img = img.scaled(targetWidth, targetHeight, Qt.KeepAspectRatio, Qt.SmoothTransformation )
        if debug > 2:
          qDebug("  scale image: %i x %i -> %i x %i" % (olWidth, olHeight, targetWidth, targetHeight,))

    else:

      if debug > 2:
        qDebug("OpenlayersWorker using cached img")

      img = self.lastRenderedImage


    if debug > 2:
      qDebug("OpenlayersWorker rendering img to painter")

    # draw to rendererContext
    rendererContext.painter().drawImage(0, 0, img)
    if painter_saved:
      rendererContext.painter().restore()

    if debug > 2:
      qDebug("OpenlayersWorker done rendering img to painter")

    # save current state
    self.lastRenderedImage = img
    self.lastExtent = rendererContext.extent()
    self.lastViewPortSize = rendererContext.painter().viewport().size()
    self.lastLogicalDpi = rendererContext.painter().device().logicalDpiX()
    self.lastOutputDpi = self.mapSettings.outputDpi()
    self.lastMapUnitsPerPixel = rendererContext.mapToPixel().mapUnitsPerPixel()

    if debug > 0:
      qDebug("OpenlayersWorker render done")

  #def scaleFromExtent(self, extent):

  def resolutions(self):
    if self.olResolutions == None:
      # get OpenLayers resolutions
      resVariant = self.page.mainFrame().evaluateJavaScript("map.layers[0].resolutions")
      self.olResolutions = resVariant
      #for res in resVariant.toList():
      #  self.olResolutions.append(res.toDouble()[0])
    return self.olResolutions


# this is a map renderer which resides in a worker thread, and uses a OpenlayersWorker
# which resides in the gui thread to do fetch the map
class OpenlayersRenderer(QgsMapLayerRenderer):

  def __init__(self, layerID, rendererContext, mapSettings, layerType):
    QgsMapLayerRenderer.__init__(self,layerID)
    if debug > 0:
      qDebug('OpenlayersRenderer __init__ '+self.layerID()+' - '+str(QThread.currentThreadId()))
    #self.worker = worker
    self.worker=OpenlayersWorker(rendererContext, mapSettings, layerType)
    

    #self.worker.startSignal.connect(self.worker.startRender)

  #def __del__(self):
  #  if debug > 0:
  #    qDebug('OpenlayersRenderer __del__') 
  #  self.worker.startSignal.disconnect(self.worker.startRender)

#  def setRendererContext(self, rendererContext):
#    self.worker.rendererContext = rendererContext

  def render(self):
    if debug > 2:
      qDebug('OpenlayersRenderer render - '+str(QThread.currentThreadId()))
    
    self.worker.moveToThread(QApplication.instance().thread())
    self.worker.working = True
    self.worker.startSignal.emit()

    #loop = QEventLoop() 
    #QObject.connect(self.worker, SIGNAL("doneSignal()"), loop, SLOT("quit()"), Qt.QueuedConnection)
    ##qDebug('OpenlayersRenderer start loop - '+str(QThread.currentThreadId()))
    #loop.exec_()
    ##qDebug('OpenlayersRenderer done loop - '+str(QThread.currentThreadId()))
    #QObject.disconnect(self.worker, SIGNAL("doneSignal()"), loop, SLOT("quit()"))

    while self.worker.working and not self.worker.rendererContext.renderingStopped():
      #print('waiting')
      qApp.processEvents()
      QThread.currentThread().msleep(100);
    if debug > 2:
      print('done waiting')

    if debug > 2:
      qDebug('OpenlayersRenderer render done')


    #self.worker.paint()

    return True

#  def done(self):
#    qDebug('OpenlayersRenderer done - '+str(QThread.currentThreadId()))


class OpenlayersLayer(QgsPluginLayer):

  LAYER_TYPE = "openlayers"
  MAX_ZOOM_LEVEL = 15
  SCALE_ON_MAX_ZOOM = 13540 # QGIS scale for 72 dpi

  def __init__(self, iface, coordRSGoogle, olLayerTypeRegistry):

    if debug > 0:
      qDebug("OpenlayersLayer init - "+str(QThread.currentThreadId()))
    QgsPluginLayer.__init__(self, OpenlayersLayer.LAYER_TYPE, "OpenLayers plugin layer")
    self.setValid(True)
    self.setCrs(coordRSGoogle)
    self.olLayerTypeRegistry = olLayerTypeRegistry

    self.setExtent(QgsRectangle(-20037508.34, -20037508.34, 20037508.34, 20037508.34))

    self.iface = iface

    #self.setLayerType( self.olLayerTypeRegistry.getById(0) )
    self.layerType = self.olLayerTypeRegistry.getById(0)

    #self.worker=OpenlayersWorker(self.iface.mapCanvas().mapSettings(), self.layerType)

    self.mapRenderer = None


  #def draw(self, rendererContext):
  #  qDebug("OpenlayersLayer draw "+str(QThread.currentThreadId ()))
  #  return True

  def readXml(self, node):
    # handle ol_layer_type idx stored in layer node (OL plugin <= 1.1.0)
    ol_layer_type_idx = int(node.toElement().attribute("ol_layer_type", "-1"))
    if ol_layer_type_idx != -1:
      ol_layer_type = self.olLayerTypeRegistry.getByIdx(ol_layer_type_idx)
      self.layerType = ol_layer_type
    return True

  def writeXml(self, node, doc):
    element = node.toElement();
    # write plugin layer type to project (essential to be read from project)
    element.setAttribute("type", "plugin")
    element.setAttribute("name", OpenlayersLayer.LAYER_TYPE);
    return True

  def setLayerType(self, layerType):
    qDebug(" setLayerType: %s" % layerType.name )
    self.layerType = layerType
#    if self.worker:
#      self.worker.layerType = layerType

  def createMapRenderer(self, rendererContext):
    if debug > 2:
      qDebug('OpenLayers createMapRenderer '+str(QThread.currentThreadId())+ ' - ' + str(rendererContext.mapToPixel().mapUnitsPerPixel()))
    #self.worker.rendererContext = rendererContext
    #self.mapRenderer = OpenlayersRenderer(self.id(), self.worker)#, rendererContext, self.iface.mapCanvas().mapSettings(), self.layerType)
    self.mapRenderer = OpenlayersRenderer(self.id(), rendererContext, self.iface.mapCanvas().mapSettings(), self.layerType)
    return self.mapRenderer
