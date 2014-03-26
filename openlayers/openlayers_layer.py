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

debuglevel = 4  # 0 (none) - 4 (all)


def debug(msg, verbosity=1):
    if debuglevel >= verbosity:
        qDebug(msg)


class OLWebPage(QWebPage):
    def __init__(self, parent=None):
        QWebPage.__init__(self, parent)
        self.__manager = None  # Need persist for PROXY
        # Set Proxy in webpage
        proxy = getProxy()
        if not proxy is None:
            self.__manager = QNetworkAccessManager()
            self.__manager.setProxy(proxy)
            self.setNetworkAccessManager(self.__manager)

    def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
        qDebug("%s[%d]: %s" % (sourceID, lineNumber, message))


# this is a worker class which is responsible for fetching the map
# it resides normally in the gui thread, except when doind paint()
class OpenlayersWorker(QObject):

    startSignal = PyQt4.QtCore.pyqtSignal()
    doneSignal = PyQt4.QtCore.pyqtSignal()

    #def __init__(self, mapSettings, layerType):
    def __init__(self, rendererContext, mapSettings, layerType):

        QObject.__init__(self)

        debug('OpenlayersWorker init - ' + ' - ' + str(QThread.currentThreadId()), 2)
        self.rendererContext = rendererContext
        self.mapSettings = mapSettings
        self.layerType = layerType

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

        self.working = False

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(500)
        QObject.connect(self.timer, SIGNAL("timeout()"), self.finalRepaint)

        self.timerMax = QTimer()
        self.timerMax.setSingleShot(True)
        self.timerMax.setInterval(5000)  # TODO: different timeouts for google/yahoo?
        QObject.connect(self.timerMax, SIGNAL("timeout()"), self.finalRepaint)

        # timeout for loadEnd event
        self.timerLoadEnd = QTimer()
        self.timerLoadEnd.setSingleShot(True)
        self.timerLoadEnd.setInterval(5000)
        QObject.connect(self.timerLoadEnd, SIGNAL("timeout()"), self.loadEndTimeout)

        self.startSignal.connect(self.startRender)

    def startRender(self):
        debug('OpenlayersWorker startRender - ' + str(QThread.currentThreadId()), 2)
        #QThread.currentThread().sleep(2)
        self.working = True
        self.render()
        #self.doneRender()
        self.working = False
        self.doneSignal.emit()
        debug('OpenlayersWorker startRender done', 2)

    # def doneRender(self):
    #     debug('OpenlayersWorker doneRender- '+str(QThread.currentThreadId()), 2)
    #     self.doneSignal.emit()

    # def paint(self):
    #     debug('OpenlayersWorker paint- '+str(QThread.currentThreadId()), 2)

    # below copied from non-MT OpenlayersLayer

    def pageRepaintRequested(self, rect):
        debug("OpenlayersLayer pageRepaintRequested", 2)
        if self.loaded:
            self.timer.stop()
            self.repaintEnd = False
            self.timer.start()
        else:
            self.repaintEnd = True

    def finalRepaint(self):
        debug("OpenlayersLayer finalRepaint")
        self.repaintEnd = True

    def loadFinished(self, ok):
        debug("OpenlayersLayer loadFinished %d" % ok)
        if ok:
            self.loaded = ok
            self.emit(SIGNAL("repaintRequested()"))

    def loadEndTimeout(self):
        debug("OpenlayersLayer loadEndTimeout")
        self.loadEnd = True

    # copied from OpenlayersLayer draw() and render()
    def render(self):
        debug("OpenlayersWorker render " + str(QThread.currentThreadId()))

        rendererContext = self.rendererContext

        if not rendererContext or rendererContext.renderingStopped():
            return False

        if not self.loaded:
            self.page = OLWebPage()
            url = self.layerType.html_url()
            debug("page file: %s" % url)
            self.page.mainFrame().load(QUrl(url))
            QObject.connect(self.page, SIGNAL("loadFinished(bool)"), self.loadFinished)
            if not self.layerType.emitsLoadEnd:
                QObject.connect(self.page, SIGNAL("repaintRequested(QRect)"), self.pageRepaintRequested)

            # wait for page to finish loading
            debug("OpenlayersWorker waiting for page to load", 3)
            while not self.loaded:
                qApp.processEvents()
            debug("OpenlayersWorker page loaded", 3)

        outputDpi = self.mapSettings.outputDpi()
        debug(" extent: %s" % rendererContext.extent().toString(), 3)
        debug(" center: %lf, %lf" % (rendererContext.extent().center().x(), rendererContext.extent().center().y()), 3)
        debug(" size: %d, %d" % (rendererContext.painter().viewport().size().width(), rendererContext.painter().viewport().size().height()), 3)
        debug(" logicalDpiX: %d" % rendererContext.painter().device().logicalDpiX(), 3)
        debug(" outputDpi: %lf" % outputDpi)
        debug(" mapUnitsPerPixel: %f" % rendererContext.mapToPixel().mapUnitsPerPixel(), 3)
        #debug(" rasterScaleFactor: %s" % str(rendererContext.rasterScaleFactor()), 3)
        #debug(" outputSize: %d, %d" % (self.iface.mapCanvas().mapRenderer().outputSize().width(), self.iface.mapCanvas().mapRenderer().outputSize().height()), 3)
        #debug(" scale: %lf" % self.iface.mapCanvas().mapRenderer().scale(), 3)

        painter_saved = False

        if self.lastExtent != rendererContext.extent() or self.lastViewPortSize != rendererContext.painter().viewport().size() or self.lastLogicalDpi != rendererContext.painter().device().logicalDpiX() or self.lastOutputDpi != outputDpi or self.lastMapUnitsPerPixel != rendererContext.mapToPixel().mapUnitsPerPixel():
            olSize = rendererContext.painter().viewport().size()
            if rendererContext.painter().device().logicalDpiX() != int(outputDpi):
                # use screen dpi for printing
                #sizeFact = outputDpi / 25.4 / rendererContext.mapToPixel().mapUnitsPerPixel()
                sizeFact = 1
                olSize.setWidth(rendererContext.extent().width() * sizeFact)
                olSize.setHeight(rendererContext.extent().height() * sizeFact)
            debug(" olSize: %d, %d" % (olSize.width(), olSize.height()), 3)
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
            debug("    adjust viewport: %f -> %f: %f x %f" % (qgisRes, olRes, olWidth, olHeight), 3)
            self.page.setViewportSize(QSize(olWidth, olHeight))

            if rendererContext.extent() != self.ext:
                self.ext = rendererContext.extent()  # FIXME: store seperate for each rendererContext
                debug("updating OpenLayers extent (%f, %f, %f, %f)" % (self.ext.xMinimum(), self.ext.yMinimum(), self.ext.xMaximum(), self.ext.yMaximum()), 3)
                self.page.mainFrame().evaluateJavaScript(
                    "map.zoomToExtent(new OpenLayers.Bounds(%f, %f, %f, %f), true);" %
                    (self.ext.xMinimum(), self.ext.yMinimum(), self.ext.xMaximum(), self.ext.yMaximum()))
                debug("map.zoomToExtent finished", 3)

            if self.layerType.emitsLoadEnd:
                debug('waiting for loadEnd', 3)
                # wait for OpenLayers to finish loading
                # NOTE: does not work with Google and Yahoo layers as they do not emit loadstart and loadend events
                self.loadEnd = False
                self.timerLoadEnd.start()
                while not self.loadEnd:
                    loadEndOL = self.page.mainFrame().evaluateJavaScript("loadEnd")
                    debug('waiting ' + str(rendererContext.renderingStopped()) + ' ' + str(loadEndOL), 4)
                    #debug("loadEndOL: %d" % loadEndOL, 3)
                    #if not loadEndOL.isNull():
                    if not loadEndOL is None:
                        self.loadEnd = loadEndOL
                    else:
                        debug("OpenlayersLayer Warning: Could not get loadEnd")
                        break
                    qApp.processEvents()
                self.timerLoadEnd.stop()
                debug('done waiting for loadEnd', 3)
            else:
                debug('waiting for pageRepaintRequested', 3)
                # wait for timeout after pageRepaintRequested
                self.repaintEnd = False
                self.timerMax.start()
                while not self.repaintEnd:
                    qApp.processEvents()
                self.timerMax.stop()
                debug('done waiting for pageRepaintRequested', 3)

            debug("OpenlayersWorker rendering page to img", 3)

            if not rendererContext or not rendererContext.painter():
                debug("OpenlayersWorker stopping rendering because renderingContext was deleted")
                return True

            if rendererContext.renderingStopped():
                debug("OpenlayersWorker stopping rendering because renderingContext stopped")
                return True

            #Render WebKit page into rendererContext
            debug('before save', 4)
            rendererContext.painter().save()
            debug('after save', 4)
            painter_saved = True
            if rendererContext.painter().device().logicalDpiX() != int(outputDpi):
                printScale = 25.4 / outputDpi  # OL DPI to printer pixels
                rendererContext.painter().scale(printScale, printScale)

            # render OpenLayers to image
            img = QImage(olWidth, olHeight, QImage.Format_ARGB32_Premultiplied)
            painter = QPainter(img)
            self.page.mainFrame().render(painter)
            painter.end()

            if olWidth != targetWidth or olHeight != targetHeight:
                # scale using QImage for better quality
                img = img.scaled(targetWidth, targetHeight, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                debug("    scale image: %i x %i -> %i x %i" % (olWidth, olHeight, targetWidth, targetHeight), 3)

        else:
            debug("OpenlayersWorker using cached img", 3)
            img = self.lastRenderedImage

        debug("OpenlayersWorker rendering img to painter", 3)

        # draw to rendererContext
        rendererContext.painter().drawImage(0, 0, img)
        if painter_saved:
            rendererContext.painter().restore()

        debug("OpenlayersWorker done rendering img to painter", 3)

        # save current state
        self.lastRenderedImage = img
        self.lastExtent = rendererContext.extent()
        self.lastViewPortSize = rendererContext.painter().viewport().size()
        self.lastLogicalDpi = rendererContext.painter().device().logicalDpiX()
        self.lastOutputDpi = self.mapSettings.outputDpi()
        self.lastMapUnitsPerPixel = rendererContext.mapToPixel().mapUnitsPerPixel()

        debug("OpenlayersWorker render done")

    #def scaleFromExtent(self, extent):

    def resolutions(self):
        if self.olResolutions is None:
            # get OpenLayers resolutions
            resVariant = self.page.mainFrame().evaluateJavaScript("map.layers[0].resolutions")
            self.olResolutions = resVariant
            #for res in resVariant.toList():
            #    self.olResolutions.append(res.toDouble()[0])
        return self.olResolutions


# this is a map renderer which resides in a worker thread, and uses a OpenlayersWorker
# which resides in the gui thread to do fetch the map
class OpenlayersRenderer(QgsMapLayerRenderer):

    def __init__(self, layerID, rendererContext, mapSettings, layerType):
        QgsMapLayerRenderer.__init__(self, layerID)
        debug('OpenlayersRenderer __init__ ' + self.layerID() + ' - ' + str(QThread.currentThreadId()))
        #self.worker = worker
        self.worker = OpenlayersWorker(rendererContext, mapSettings, layerType)

        #self.worker.startSignal.connect(self.worker.startRender)

    #def __del__(self):
    #    debug('OpenlayersRenderer __del__')
    #    self.worker.startSignal.disconnect(self.worker.startRender)

#    def setRendererContext(self, rendererContext):
#        self.worker.rendererContext = rendererContext

    def render(self):
        debug('OpenlayersRenderer render - ' + str(QThread.currentThreadId()), 3)

        self.worker.moveToThread(QApplication.instance().thread())
        self.worker.working = True
        self.worker.startSignal.emit()

        #loop = QEventLoop()
        #QObject.connect(self.worker, SIGNAL("doneSignal()"), loop, SLOT("quit()"), Qt.QueuedConnection)
        ##debug('OpenlayersRenderer start loop - '+str(QThread.currentThreadId()))
        #loop.exec_()
        ##debug('OpenlayersRenderer done loop - '+str(QThread.currentThreadId()))
        #QObject.disconnect(self.worker, SIGNAL("doneSignal()"), loop, SLOT("quit()"))

        while self.worker.working and not self.worker.rendererContext.renderingStopped():
            #print('waiting')
            qApp.processEvents()
            QThread.currentThread().msleep(100)
        if debug > 2:
            print('done waiting')

        debug('OpenlayersRenderer render done', 3)

        #self.worker.paint()

        return True

    # def done(self):
    #     debug('OpenlayersRenderer done - '+str(QThread.currentThreadId()))


class OpenlayersLayer(QgsPluginLayer):

    LAYER_TYPE = "openlayers"
    MAX_ZOOM_LEVEL = 15
    SCALE_ON_MAX_ZOOM = 13540  # QGIS scale for 72 dpi

    def __init__(self, iface, olLayerTypeRegistry):
        debug("OpenlayersLayer init - " + str(QThread.currentThreadId()))
        QgsPluginLayer.__init__(self, OpenlayersLayer.LAYER_TYPE, "OpenLayers plugin layer")
        self.setValid(True)
        self.olLayerTypeRegistry = olLayerTypeRegistry

        self.iface = iface

        #Set default layer type
        self.setLayerType(self.olLayerTypeRegistry.getById(0))

        self.mapRenderer = None

    #def draw(self, rendererContext):
    #    debug("OpenlayersLayer draw "+str(QThread.currentThreadId ()))
    #    return True

    def readXml(self, node):
        # custom properties
        self.setLayerType(self.olLayerTypeRegistry.getById(int(node.toElement().attribute("ol_layer_type", "0"))))
        return True

    def writeXml(self, node, doc):
        element = node.toElement()
        # write plugin layer type to project (essential to be read from project)
        element.setAttribute("type", "plugin")
        element.setAttribute("name", OpenlayersLayer.LAYER_TYPE)
        # custom properties
        element.setAttribute("ol_layer_type", str(self.layerType.id))
        return True

    def setLayerType(self, layerType):
        self.layerType = layerType
        coordRefSys = self.layerType.coordRefSys(None)  # FIXME
        self.setCrs(coordRefSys)
        #TODO: get extent from layer type
        self.setExtent(QgsRectangle(-20037508.34, -20037508.34, 20037508.34, 20037508.34))

    def createMapRenderer(self, rendererContext):
        debug('OpenLayers createMapRenderer ' + str(QThread.currentThreadId()) + ' - ' + str(rendererContext.mapToPixel().mapUnitsPerPixel()), 3)
        #self.worker.rendererContext = rendererContext
        #self.mapRenderer = OpenlayersRenderer(self.id(), self.worker)#, rendererContext, self.iface.mapCanvas().mapSettings(), self.layerType)
        self.mapRenderer = OpenlayersRenderer(self.id(), rendererContext, self.iface.mapCanvas().mapSettings(), self.layerType)
        return self.mapRenderer
