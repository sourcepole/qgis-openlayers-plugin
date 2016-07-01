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
from qgis.gui import *

from tools_network import getProxy


debuglevel = 4  # 0 (none) - 4 (all)


def debug(msg, verbosity=1):
    if debuglevel >= verbosity:
        try:
            qDebug(msg)
        except:
            pass


class OLWebPage(QWebPage):
    def __init__(self, parent=None):
        QWebPage.__init__(self, parent)
        self.__manager = None  # Need persist for PROXY
        # Set Proxy in webpage
        proxy = getProxy()
        if proxy is not None:
            self.__manager = QNetworkAccessManager()
            self.__manager.setProxy(proxy)
            self.setNetworkAccessManager(self.__manager)

        self.loaded = False

        self.extent = None
        self.olResolutions = None

        self.lastExtent = None
        self.lastViewPortSize = None
        self.lastLogicalDpi = None
        self.lastOutputDpi = None
        self.lastMapUnitsPerPixel = None

    def resolutions(self):
        if self.olResolutions is None:
            # get OpenLayers resolutions
            jsResolutions = self.mainFrame().evaluateJavaScript("map.layers[0].resolutions")
            debug("Detected OpenLayers resolutions: %s" % jsResolutions)
            self.olResolutions = jsResolutions
        return self.olResolutions or []

    def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
        qDebug("%s[%d]: %s" % (sourceID, lineNumber, message))


class OpenlayersController(QObject):
    """
    Helper class that deals with QWebPage.
    The object lives in GUI thread, its request() slot is asynchronously called from worker thread.
    See https://github.com/wonder-sk/qgis-mtr-example-plugin for basic example
    1. Load Web Page with OpenLayers map
    2. Update OL map extend according to QGIS canvas extent
    """

    # signal that reports to the worker thread that the image is ready
    finished = pyqtSignal()

    def __init__(self, parent, context, webPage, layerType):
        QObject.__init__(self, parent)

        debug("OpenlayersController.__init__", 3)
        self.context = context
        self.layerType = layerType

        self.img = QImage()

        self.page = webPage
        self.page.loadFinished.connect(self.pageLoaded)
        # initial size for map
        self.page.setViewportSize(QSize(1, 1))

        self.timerMapReady = QTimer()
        self.timerMapReady.setSingleShot(True)
        self.timerMapReady.setInterval(20)
        self.timerMapReady.timeout.connect(self.checkMapReady)

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.checkMapUpdate)

        self.timerMax = QTimer()
        self.timerMax.setSingleShot(True)
        self.timerMax.setInterval(5000)  # TODO: different timeouts for map types
        self.timerMax.timeout.connect(self.mapTimeout)

    @pyqtSlot()
    def request(self):
        debug("[GUI THREAD] Processing request", 3)
        self.cancelled = False

        if not self.page.loaded:
            self.init_page()
        else:
            self.setup_map()

    def init_page(self):
        url = self.layerType.html_url()
        debug("page file: %s" % url)
        self.page.mainFrame().load(QUrl(url))
        # wait for page to finish loading
        debug("OpenlayersWorker waiting for page to load", 3)

    def pageLoaded(self):
        debug("[GUI THREAD] pageLoaded", 3)
        if self.cancelled:
            self.emitErrorImage()
            return

        # wait until OpenLayers map is ready
        self.checkMapReady()

    def checkMapReady(self):
        debug("[GUI THREAD] checkMapReady", 3)
        if self.page.mainFrame().evaluateJavaScript("map != undefined"):
            # map ready
            self.page.loaded = True
            self.setup_map()
        else:
            # wait for map
            self.timerMapReady.start()

    def setup_map(self):
        rendererContext = self.context

        self.outputDpi = rendererContext.painter().device().logicalDpiX()  # FIXME: self.mapSettings.outputDpi()
        debug(" extent: %s" % rendererContext.extent().toString(), 3)
        debug(" center: %lf, %lf" % (rendererContext.extent().center().x(), rendererContext.extent().center().y()), 3)
        debug(" size: %d, %d" % (rendererContext.painter().viewport().size().width(),
              rendererContext.painter().viewport().size().height()), 3)
        debug(" logicalDpiX: %d" % rendererContext.painter().device().logicalDpiX(), 3)
        debug(" outputDpi: %lf" % self.outputDpi)
        debug(" mapUnitsPerPixel: %f" % rendererContext.mapToPixel().mapUnitsPerPixel(), 3)
        #debug(" rasterScaleFactor: %s" % str(rendererContext.rasterScaleFactor()), 3)
        #debug(" outputSize: %d, %d" % (self.iface.mapCanvas().mapRenderer().outputSize().width(), self.iface.mapCanvas().mapRenderer().outputSize().height()), 3)
        #debug(" scale: %lf" % self.iface.mapCanvas().mapRenderer().scale(), 3)

        # if (self.page.lastExtent == rendererContext.extent()
        #         and self.page.lastViewPortSize == rendererContext.painter().viewport().size()
        #         and self.page.lastLogicalDpi == rendererContext.painter().device().logicalDpiX()
        #         and self.page.lastOutputDpi == self.outputDpi
        #         and self.page.lastMapUnitsPerPixel == rendererContext.mapToPixel().mapUnitsPerPixel()):
        #     self.renderMap()
        #     self.finished.emit()
        #     return

        self.targetSize = rendererContext.painter().viewport().size()
        if rendererContext.painter().device().logicalDpiX() != int(self.outputDpi):
            # use screen dpi for printing
            sizeFact = self.outputDpi / 25.4 / rendererContext.mapToPixel().mapUnitsPerPixel()
            self.targetSize.setWidth(rendererContext.extent().width() * sizeFact)
            self.targetSize.setHeight(rendererContext.extent().height() * sizeFact)
        debug(" targetSize: %d, %d" % (self.targetSize.width(), self.targetSize.height()), 3)

        # find matching OL resolution
        qgisRes = rendererContext.extent().width() / self.targetSize.width()
        olRes = None
        for res in self.page.resolutions():
            if qgisRes >= res:
                olRes = res
                break
        if olRes is None:
            debug("No matching OL resolution found (QGIS resolution: %f)" % qgisRes)
            self.emitErrorImage()
            return

        # adjust OpenLayers viewport to match QGIS extent
        olWidth = rendererContext.extent().width() / olRes
        olHeight = rendererContext.extent().height() / olRes
        debug("    adjust viewport: %f -> %f: %f x %f" % (qgisRes, olRes, olWidth, olHeight), 3)
        olSize = QSize(int(olWidth), int(olHeight))
        self.page.setViewportSize(olSize)
        self.page.mainFrame().evaluateJavaScript("map.updateSize();")
        self.img = QImage(olSize, QImage.Format_ARGB32_Premultiplied)

        self.page.extent = rendererContext.extent()
        debug("map.zoomToExtent (%f, %f, %f, %f)" % (
            self.page.extent.xMinimum(), self.page.extent.yMinimum(),
            self.page.extent.xMaximum(), self.page.extent.yMaximum()), 3)
        self.page.mainFrame().evaluateJavaScript(
            "map.zoomToExtent(new OpenLayers.Bounds(%f, %f, %f, %f), true);" % (
                self.page.extent.xMinimum(), self.page.extent.yMinimum(),
                self.page.extent.xMaximum(), self.page.extent.yMaximum()))
        olextent = self.page.mainFrame().evaluateJavaScript("map.getExtent();")
        debug("Resulting OL extent: %s" % olextent, 3)
        if olextent is None or not hasattr(olextent, '__getitem__'):
            debug("map.zoomToExtent failed")
            #map.setCenter and other operations throw "undefined[0]: TypeError: 'null' is not an object" on first page load
            #We ignore that and render the initial map with wrong extents
            #self.emitErrorImage()
            #return
        else:
            reloffset = abs((self.page.extent.yMaximum()-olextent["top"])/self.page.extent.xMinimum())
            debug("relative offset yMaximum %f" % reloffset, 3)
            if reloffset > 0.1:
                debug("OL extent shift failure: %s" % reloffset)
                self.emitErrorImage()
                return
        self.mapFinished = False
        self.timer.start()
        self.timerMax.start()

    def checkMapUpdate(self):
        if self.layerType.emitsLoadEnd:
            # wait for OpenLayers to finish loading
            loadEndOL = self.page.mainFrame().evaluateJavaScript("loadEnd")
            debug("waiting for loadEnd: renderingStopped=%r loadEndOL=%r" % (
                  self.context.renderingStopped(), loadEndOL), 4)
            if not loadEndOL is None:
                self.mapFinished = loadEndOL
            else:
                debug("OpenlayersLayer Warning: Could not get loadEnd")

        if self.mapFinished:
            self.timerMax.stop()
            self.timer.stop()

            self.renderMap()

            self.finished.emit()

    def renderMap(self):
        rendererContext = self.context
        if rendererContext.painter().device().logicalDpiX() != int(self.outputDpi):
            printScale = 25.4 / self.outputDpi  # OL DPI to printer pixels
            rendererContext.painter().scale(printScale, printScale)

        # render OpenLayers to image
        painter = QPainter(self.img)
        self.page.mainFrame().render(painter)
        painter.end()

        if self.img.size() != self.targetSize:
            targetWidth = self.targetSize.width()
            targetHeight = self.targetSize.height()
            # scale using QImage for better quality
            debug("    scale image: %i x %i -> %i x %i" % (self.img.width(), self.img.height(),
                  targetWidth, targetHeight), 3)
            self.img = self.img.scaled(targetWidth, targetHeight, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # save current state
        self.page.lastExtent = rendererContext.extent()
        self.page.lastViewPortSize = rendererContext.painter().viewport().size()
        self.page.lastLogicalDpi = rendererContext.painter().device().logicalDpiX()
        self.page.lastOutputDpi = self.outputDpi
        self.page.lastMapUnitsPerPixel = rendererContext.mapToPixel().mapUnitsPerPixel()

    def mapTimeout(self):
        debug("mapTimeout reached")
        self.timer.stop()
        #if not self.layerType.emitsLoadEnd:
        self.renderMap()
        self.finished.emit()

    def emitErrorImage(self):
        self.img = QImage()
        self.targetSize = self.img.size
        self.finished.emit()


class OpenlayersRenderer(QgsMapLayerRenderer):
    def __init__(self, layer, context, webPage, layerType):
        """ Initialize the object. This function is still run in the GUI thread.
            Should refrain from doing any heavy work.
        """
        QgsMapLayerRenderer.__init__(self, layer.id())
        self.context = context
        self.controller = OpenlayersController(None, context, webPage, layerType)
        self.loop = None

    def render(self):
        """ do the rendering. This function is called in the worker thread """

        debug("[WORKER THREAD] Calling request() asynchronously", 3)
        QMetaObject.invokeMethod(self.controller, "request")

        # setup a timer that checks whether the rendering has not been stopped in the meanwhile
        timer = QTimer()
        timer.setInterval(50)
        timer.timeout.connect(self.onTimeout)
        timer.start()

        debug("[WORKER THREAD] Waiting for the async request to complete", 3)
        self.loop = QEventLoop()
        self.controller.finished.connect(self.loop.exit)
        self.loop.exec_()

        debug("[WORKER THREAD] Async request finished", 3)

        painter = self.context.painter()
        painter.drawImage(0, 0, self.controller.img)
        return True

    def onTimeout(self):
        """ periodically check whether the rendering should not be stopped """
        if self.context.renderingStopped():
            debug("[WORKER THREAD] Cancelling rendering", 3)
            self.loop.exit()


class OpenlayersLayer(QgsPluginLayer):

    LAYER_TYPE = "openlayers"
    LAYER_PROPERTY = "ol_layer_type"
    MAX_ZOOM_LEVEL = 15
    SCALE_ON_MAX_ZOOM = 13540  # QGIS scale for 72 dpi

    def __init__(self, iface, olLayerTypeRegistry):
        QgsPluginLayer.__init__(self, OpenlayersLayer.LAYER_TYPE, "OpenLayers plugin layer")
        self.setValid(True)

        self.olLayerTypeRegistry = olLayerTypeRegistry
        self.layerType = None

        self.iface = iface
        self.olWebPage = OLWebPage(self)

    def readXml(self, node):
        # early read of custom properties
        self.readCustomProperties(node)

        # get layer type
        ol_layer_type = None
        ol_layer_type_name = self.customProperty(OpenlayersLayer.LAYER_PROPERTY, "")
        if ol_layer_type_name != "":
            ol_layer_type = self.olLayerTypeRegistry.getByName(ol_layer_type_name)
        else:
            # handle ol_layer_type idx stored in layer node (OL plugin <= 1.1.2)
            ol_layer_type_idx = int(node.toElement().attribute("ol_layer_type", "-1"))
            if ol_layer_type_idx != -1:
                ol_layer_type = self.olLayerTypeRegistry.getById(ol_layer_type_idx)

        if ol_layer_type is not None:
            self.setLayerType(ol_layer_type)
        else:
            # Set default layer type
            self.setLayerType(self.olLayerTypeRegistry.getByName("OpenStreetMap"))
            if QGis.QGIS_VERSION_INT >= 20300:
                msg = "Obsolete or unknown layer type '%s', using OpenStreetMap instead" % ol_layer_type_name
                self.iface.messageBar().pushMessage("OpenLayers Plugin", msg, level=QgsMessageBar.WARNING)
                QgsMessageLog.logMessage(msg, "OpenLayers Plugin", QgsMessageLog.WARNING)

        return True

    def writeXml(self, node, doc):
        element = node.toElement()
        # write plugin layer type to project (essential to be read from project)
        element.setAttribute("type", "plugin")
        element.setAttribute("name", OpenlayersLayer.LAYER_TYPE)
        return True

    def setLayerType(self, layerType):
        qDebug(" setLayerType: %s" % layerType.layerTypeName)
        self.layerType = layerType
        self.setCustomProperty(OpenlayersLayer.LAYER_PROPERTY, layerType.layerTypeName)
        coordRefSys = self.layerType.coordRefSys(None)  # FIXME
        self.setCrs(coordRefSys)
        #TODO: get extent from layer type
        self.setExtent(QgsRectangle(-20037508.34, -20037508.34, 20037508.34, 20037508.34))

    def createMapRenderer(self, context):
        return OpenlayersRenderer(self, context, self.olWebPage, self.layerType)
