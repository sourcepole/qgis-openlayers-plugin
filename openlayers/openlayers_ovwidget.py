# -*- coding: utf-8 -*-
"""
/***************************************************************************
    Openlayers Overview  - A QGIS plugin to show map in browser(google maps and others)
                             -------------------
    begin            : 2011-03-01
    copyright        : (C) 2011 by Luiz Motta
    author           : Luiz P. Motta
    email            : motta _dot_ luiz _at_ gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from qgis import core, gui, utils

try:
    from PyQt4.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = type("")

from tools_network import getProxy
import bindogr

from ui_openlayers_ovwidget import Ui_Form

class MarkerCursor(QObject):
  def __init__(self, mapCanvas, srsOL):
    QObject.__init__(self)
    self.__srsOL = srsOL
    self.__canvas = mapCanvas
    self.__marker = None
    self.__showMarker = True

  def __del__(self):
    self.reset()

  def __refresh(self, pointCenter):
    if not self.__marker is None:
      self.reset()
    self.__marker = gui.QgsVertexMarker(self.__canvas)
    self.__marker.setCenter(pointCenter)
    self.__marker.setIconType(gui.QgsVertexMarker.ICON_X )
    self.__marker.setPenWidth(4)

  def setVisible(self, visible):
    self.__showMarker = visible

  def reset(self):
    self.__canvas.scene().removeItem(self.__marker)
    del self.__marker
    self.__marker = None
  @pyqtSlot(str)
  def changeMarker(self, strListExtent):
    if not self.__showMarker:
      return
    # left, bottom, right, top
    left, bottom, right, top = [ float(item) for item in strListExtent.split(',') ]
    pointCenter = core.QgsRectangle(core.QgsPoint(left, top), core.QgsPoint(right, bottom)).center()
    crsCanvas = self.__canvas.mapRenderer().destinationCrs()
    if self.__srsOL != crsCanvas:
      coodTrans = core.QgsCoordinateTransform(self.__srsOL, crsCanvas)
      pointCenter = coodTrans.transform(pointCenter, core.QgsCoordinateTransform.ForwardTransform)
    self.__refresh(pointCenter)

class OpenLayersOverviewWidget(QWidget,Ui_Form):
  def __init__(self, iface, dockwidget, olLayerTypeRegistry):
    QWidget.__init__(self)
    Ui_Form.__init__(self)
    self.setupUi(self)
    self.__canvas = iface.mapCanvas()
    self.__dockwidget = dockwidget
    self.__olLayerTypeRegistry = olLayerTypeRegistry
    self.__initLayerOL = False
    self.__fileNameImg = ''
    self.__srsOL = core.QgsCoordinateReferenceSystem(3857, core.QgsCoordinateReferenceSystem.EpsgCrsId)
    self.__marker = MarkerCursor(self.__canvas, self.__srsOL)
    self.__manager = None # Need persist for PROXY
    bindogr.initOgr()
    self.__init()

  def __init(self):
    self.checkBoxHideCross.setEnabled(False)
    self.__populateTypeMapGUI()
    self.__populateButtonBox()
    self.__registerObjJS()
    self.lbStatusRead.setVisible( False )
    self.__setConnections()
    # Proxy
    proxy = getProxy()
    if not proxy is None:
      self.__manager = QNetworkAccessManager()
      self.__manager.setProxy(proxy)
      self.webViewMap.page().setNetworkAccessManager(self.__manager)

    self.__timerMapReady = QTimer()
    self.__timerMapReady.setSingleShot(True)
    self.__timerMapReady.setInterval(20)
    self.__timerMapReady.timeout.connect(self.__checkMapReady)

  def __del__(self):
    self.__marker.reset()
    # Disconnect Canvas
    # Canvas
    self.disconnect(self.__canvas, SIGNAL("extentsChanged()"),
                 self.__signal_canvas_extentsChanged)
    # Doc WidgetparentWidget
    self.disconnect(self.__dockwidget, SIGNAL("visibilityChanged (bool)"),
                 self.__signal_DocWidget_visibilityChanged)

  def __populateButtonBox(self):
    pathPlugin = "%s%s%%s" % ( os.path.dirname( __file__ ), os.path.sep )
    self.pbRefresh.setIcon(QIcon( pathPlugin % "mActionDraw.png" ))
    self.pbRefresh.setEnabled(False)
    self.pbAddRaster.setIcon(QIcon( pathPlugin % "mActionAddRasterLayer.png" ))
    self.pbAddRaster.setEnabled(False)
    self.pbCopyKml.setIcon(QIcon( pathPlugin % "kml.png" ))
    self.pbCopyKml.setEnabled(False)
    self.pbSaveImg.setIcon(QIcon( pathPlugin % "mActionSaveMapAsImage.png"))
    self.pbSaveImg.setEnabled(False)

  def __populateTypeMapGUI(self):
    pathPlugin = "%s%s%%s" % ( os.path.dirname( __file__ ), os.path.sep )
    totalLayers = len( self.__olLayerTypeRegistry.types() )
    for id in range( totalLayers ):
      layer = self.__olLayerTypeRegistry.getById( id )
      name  = QString( layer.displayName )
      icon  = QIcon( pathPlugin % layer.groupIcon )
      self.comboBoxTypeMap.addItem(icon, name, id)

  def __setConnections(self):
    # Check Box
    self.connect(self.checkBoxEnableMap, SIGNAL("stateChanged (int)"),
                 self.__signal_checkBoxEnableMap_stateChanged)
    self.connect(self.checkBoxHideCross, SIGNAL("stateChanged (int)"),
                 self.__signal_checkBoxHideCross_stateChanged)
    # comboBoxTypeMap
    self.connect(self.comboBoxTypeMap, SIGNAL(" currentIndexChanged (int)"),
                 self.__signal_comboBoxTypeMap_currentIndexChanged)
    # Canvas
    self.connect(self.__canvas, SIGNAL("extentsChanged()"),
                 self.__signal_canvas_extentsChanged)
    # Doc WidgetparentWidget
    self.connect(self.__dockwidget, SIGNAL("visibilityChanged (bool)"),
                 self.__signal_DocWidget_visibilityChanged)
    # WebView Map
    self.connect(self.webViewMap.page().mainFrame(), SIGNAL("javaScriptWindowObjectCleared()"),
                 self.__registerObjJS)
    # Push Button
    self.connect(self.pbRefresh, SIGNAL("clicked (bool)"),
                 self.__signal_pbRefresh_clicked)
    self.connect(self.pbAddRaster, SIGNAL("clicked (bool)"),
                 self.__signal_pbAddRaster_clicked)
    self.connect(self.pbCopyKml, SIGNAL("clicked (bool)"),
                 self.__signal_pbCopyKml_clicked)
    self.connect(self.pbSaveImg, SIGNAL("clicked (bool)"),
                 self.__signal_pbSaveImg_clicked)

  def __registerObjJS(self):
    self.webViewMap.page().mainFrame().addToJavaScriptWindowObject("MarkerCursorQGis", self.__marker)

  def __signal_checkBoxEnableMap_stateChanged(self, state):
    enable = False
    if state == Qt.Unchecked:
      self.__marker.reset()
    else:
      if self.__canvas.layerCount() == 0:
        QMessageBox.warning(self, QApplication.translate("OpenLayersOverviewWidget", "OpenLayers Overview"), QApplication.translate("OpenLayersOverviewWidget", "At least one layer in map canvas required"))
        self.checkBoxEnableMap.setCheckState (Qt.Unchecked)
      else:
        enable = True
        if not self.__initLayerOL:
          self.__initLayerOL = True
          self.__setWebViewMap( 0 )
        else:
          self.__refreshMapOL()
    # GUI
    if enable:
      self.lbStatusRead.setVisible( False )
      self.webViewMap.setVisible( True )
    else:
      self.lbStatusRead.setText("")
      self.lbStatusRead.setVisible( True )
      self.webViewMap.setVisible( False )
    self.webViewMap.setEnabled( enable )
    self.comboBoxTypeMap.setEnabled(enable)
    self.pbRefresh.setEnabled(enable)
    self.pbAddRaster.setEnabled(enable)
    self.pbCopyKml.setEnabled(enable)
    self.pbSaveImg.setEnabled(enable)
    self.checkBoxHideCross.setEnabled(enable)

  def __signal_checkBoxHideCross_stateChanged(self, state):
    if state == Qt.Checked:
      self.__marker.reset()
      self.__marker.setVisible(False)
    else:
      self.__marker.setVisible(True)
      self.__refreshMapOL()

  def __signal_DocWidget_visibilityChanged(self, visible):
    if self.__canvas.layerCount() == 0:
      return
    self.checkBoxEnableMap.setCheckState(Qt.Unchecked)
    self.__signal_checkBoxEnableMap_stateChanged(Qt.Unchecked)

  def __signal_comboBoxTypeMap_currentIndexChanged(self, index):
    self.__setWebViewMap( index )

  def __signal_canvas_extentsChanged(self):
    if self.__canvas.layerCount() == 0 or not self.webViewMap.isVisible():
      return
    if self.checkBoxEnableMap.checkState() == Qt.Checked:
      self.__refreshMapOL()

  def __signal_pbRefresh_clicked(self, checked):
    index = self.comboBoxTypeMap.currentIndex()
    self.__setWebViewMap( index )

  def __signal_pbAddRaster_clicked(self, checked):
    index = self.comboBoxTypeMap.currentIndex()
    layer = self.__olLayerTypeRegistry.getById( index )
    layer.addLayer()

  def __signal_pbCopyKml_clicked(self, cheked):
    # Extent Openlayers
    action = "map.getExtent().toGeometry().toString();"
    wkt = self.webViewMap.page().mainFrame().evaluateJavaScript(action)
    rect = core.QgsGeometry.fromWkt(wkt).boundingBox()
    srsGE = core.QgsCoordinateReferenceSystem(4326, core.QgsCoordinateReferenceSystem.EpsgCrsId)
    coodTrans = core.QgsCoordinateTransform(self.__srsOL, srsGE)
    rect = coodTrans.transform(rect, core.QgsCoordinateTransform.ForwardTransform)
    line = core.QgsGeometry.fromRect(rect).asPolygon()[0]
    wkt = str(core.QgsGeometry.fromPolyline(line).exportToWkt() )
    # Kml
    proj4 = str( srsGE.toProj4() )
    kmlLine = bindogr.exportKml(wkt, proj4)
    kml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"\
          "<kml xmlns=\"http://www.opengis.net/kml/2.2\" " \
          "xmlns:gx=\"http://www.google.com/kml/ext/2.2\" " \
          "xmlns:kml=\"http://www.opengis.net/kml/2.2\" " \
          "xmlns:atom=\"http://www.w3.org/2005/Atom\">" \
          "<Placemark>" \
          "<name>KML from Plugin Openlayers Overview for QGIS</name>" \
          "<description>Extent of openlayers map from Plugin Openlayers Overview for QGIS</description>"\
          "%s" \
          "</Placemark></kml>" % kmlLine
    clipBoard = QApplication.clipboard()
    clipBoard.setText(kml)

  def __signal_pbSaveImg_clicked(self, cheked):
    fileName = QFileDialog.getSaveFileName(self, QApplication.translate("OpenLayersOverviewWidget", "Save image"), self.__fileNameImg, QApplication.translate("OpenLayersOverviewWidget", "Image(*.jpg)"))
    if not fileName == '':
      self.__fileNameImg = fileName
    else:
      return
    img = QImage(self.webViewMap.page().mainFrame().contentsSize(), QImage.Format_ARGB32_Premultiplied)
    imgPainter = QPainter()
    imgPainter.begin(img)
    self.webViewMap.page().mainFrame().render(imgPainter)
    imgPainter.end()
    img.save( fileName, "JPEG")

  def __signal_webViewMap_loadFinished(self, ok):
    if ok == False:
      QMessageBox.warning(self, QApplication.translate("OpenLayersOverviewWidget", "OpenLayers Overview"), QApplication.translate("OpenLayersOverviewWidget", "Error loading page!"))
    else:
      # wait until OpenLayers map is ready
      self.__checkMapReady()
    self.lbStatusRead.setVisible( False )
    self.webViewMap.setVisible( True )
    self.disconnect(self.webViewMap.page().mainFrame(), SIGNAL("loadFinished (bool)"),
                 self.__signal_webViewMap_loadFinished)

  def __setWebViewMap(self, id):
    layer = self.__olLayerTypeRegistry.getById( id )
    self.lbStatusRead.setText( "Loading " +  layer.displayName + " ...")
    self.lbStatusRead.setVisible( True )
    self.webViewMap.setVisible( False )
    self.connect(self.webViewMap.page().mainFrame(), SIGNAL("loadFinished (bool)"),
                 self.__signal_webViewMap_loadFinished)
    url = layer.html_url()
    self.webViewMap.page().mainFrame().load( QUrl(url) )

  def __checkMapReady(self):
    if self.webViewMap.page().mainFrame().evaluateJavaScript("map != undefined"):
      # map ready
      self.__refreshMapOL()
    else:
      # wait for map
      self.__timerMapReady.start()

  def __refreshMapOL(self):
    action = "map.setCenter(new OpenLayers.LonLat(%f, %f));" % self.__getCenterLongLat2OL()
    self.webViewMap.page().mainFrame().evaluateJavaScript(action)
    action = "map.zoomToScale(%f);" % self.__canvas.scale()
    self.webViewMap.page().mainFrame().evaluateJavaScript(action)
    self.webViewMap.page().mainFrame().evaluateJavaScript("oloMarker.changeMarker();")

  def __getCenterLongLat2OL(self):
    pntCenter = self.__canvas.extent().center()
    crsCanvas = self.__canvas.mapRenderer().destinationCrs()
    if crsCanvas != self.__srsOL:
      coodTrans = core.QgsCoordinateTransform(crsCanvas, self.__srsOL)
      pntCenter = coodTrans.transform(pntCenter, core.QgsCoordinateTransform.ForwardTransform)
    return tuple( [ pntCenter.x(),pntCenter.y() ] )
