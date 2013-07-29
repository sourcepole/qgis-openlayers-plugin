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

from PyQt4 import QtCore, QtGui, QtNetwork
from qgis import core, gui, utils

from tools_network import getProxy
import bindogr

from openlayers_ovwidgetbase import Ui_Form

class MarkerCursor(QtCore.QObject):
  def __init__(self, mapCanvas, srsOL):
    QtCore.QObject.__init__(self)
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
  @QtCore.pyqtSlot(str)    
  def changeMarker(self, strListExtent):
    if not self.__showMarker:
      return
    # left, bottom, right, top
    left, bottom, right, top = [ float(item) for item in strListExtent.split(',') ]
    pointCenter = core.QgsRectangle(core.QgsPoint(left, top), core.QgsPoint(right, bottom)).center() 
    srsCanvas = self.__canvas.mapRenderer().destinationSrs() 
    if self.__srsOL != srsCanvas:
      coodTrans = core.QgsCoordinateTransform(self.__srsOL, srsCanvas)
      pointCenter = coodTrans.transform(pointCenter, core.QgsCoordinateTransform.ForwardTransform)
    self.__refresh(pointCenter)

class OpenLayersOverviewWidget(QtGui.QWidget,Ui_Form):
  def __init__(self, iface, dockwidget, olLayerTypeRegistry):
    QtGui.QWidget.__init__(self)
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
      self.__manager = QtNetwork.QNetworkAccessManager()
      self.__manager.setProxy(proxy)
      self.webViewMap.page().setNetworkAccessManager(self.__manager)
  def __del__(self):
    self.__marker.reset()
    # Disconnect Canvas 
    # Canvas
    self.disconnect(self.__canvas, QtCore.SIGNAL("extentsChanged()"), 
                 self.__signal_canvas_extentsChanged)
    # Doc WidgetparentWidget
    self.disconnect(self.__dockwidget, QtCore.SIGNAL("visibilityChanged (bool)"), 
                 self.__signal_DocWidget_visibilityChanged)
  def __populateButtonBox(self):
    pathPlugin = "%s%s%%s" % ( os.path.dirname( __file__ ), os.path.sep )
    self.pbRefresh.setIcon(QtGui.QIcon( pathPlugin % "mActionDraw.png" ))
    self.pbRefresh.setEnabled(False)
    self.pbAddRaster.setIcon(QtGui.QIcon( pathPlugin % "mActionAddRasterLayer.png" ))
    self.pbAddRaster.setEnabled(False)
    self.pbCopyKml.setIcon(QtGui.QIcon( pathPlugin % "kml.png" ))
    self.pbCopyKml.setEnabled(False)
    self.pbSaveImg.setIcon(QtGui.QIcon( pathPlugin % "mActionSaveMapAsImage.png"))
    self.pbSaveImg.setEnabled(False)
  def __populateTypeMapGUI(self):
    pathPlugin = "%s%s%%s" % ( os.path.dirname( __file__ ), os.path.sep )
    totalLayers = len( self.__olLayerTypeRegistry.types() )
    for idx in range( totalLayers ):
      layer = self.__olLayerTypeRegistry.getByIdx( idx )
      title  = QtCore.QString( layer.title )
      icon  = QtGui.QIcon( pathPlugin % layer.icon )
      self.comboBoxTypeMap.addItem(icon, title, layer.name)
  def __setConnections(self):
    # Check Box
    self.connect(self.checkBoxEnableMap, QtCore.SIGNAL("stateChanged (int)"),
                 self.__signal_checkBoxEnableMap_stateChanged)
    self.connect(self.checkBoxHideCross, QtCore.SIGNAL("stateChanged (int)"),
                 self.__signal_checkBoxHideCross_stateChanged)
    # comboBoxTypeMap
    self.connect(self.comboBoxTypeMap, QtCore.SIGNAL(" currentIndexChanged (int)"),
                 self.__signal_comboBoxTypeMap_currentIndexChanged)
    # Canvas
    self.connect(self.__canvas, QtCore.SIGNAL("extentsChanged()"), 
                 self.__signal_canvas_extentsChanged)
    # Doc WidgetparentWidget
    self.connect(self.__dockwidget, QtCore.SIGNAL("visibilityChanged (bool)"), 
                 self.__signal_DocWidget_visibilityChanged)
    # WebView Map
    self.connect(self.webViewMap.page().mainFrame(), QtCore.SIGNAL("javaScriptWindowObjectCleared()"), 
                 self.__registerObjJS)
    # Push Button
    self.connect(self.pbRefresh, QtCore.SIGNAL("clicked (bool)"), 
                 self.__signal_pbRefresh_clicked)
    self.connect(self.pbAddRaster, QtCore.SIGNAL("clicked (bool)"), 
                 self.__signal_pbAddRaster_clicked)
    self.connect(self.pbCopyKml, QtCore.SIGNAL("clicked (bool)"), 
                 self.__signal_pbCopyKml_clicked)
    self.connect(self.pbSaveImg, QtCore.SIGNAL("clicked (bool)"), 
                 self.__signal_pbSaveImg_clicked)
  def __registerObjJS(self):
    self.webViewMap.page().mainFrame().addToJavaScriptWindowObject("MarkerCursorQGis", self.__marker)
  def __signal_checkBoxEnableMap_stateChanged(self, state):
    enable = False
    if state == QtCore.Qt.Unchecked:
      self.__marker.reset()
    else:
      if self.__canvas.layerCount() == 0:
        QtGui.QMessageBox.warning(self, QtGui.QApplication.translate("OpenLayersOverviewWidget", "OpenLayers Overview"), QtGui.QApplication.translate("OpenLayersOverviewWidget", "At least one layer in map canvas required"))
        self.checkBoxEnableMap.setCheckState (QtCore.Qt.Unchecked)
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
    if state == QtCore.Qt.Checked:
      self.__marker.reset()
      self.__marker.setVisible(False)
    else:
      self.__marker.setVisible(True)
      self.__refreshMapOL()
  def __signal_DocWidget_visibilityChanged(self, visible):
    if self.__canvas.layerCount() == 0:
      return
    self.checkBoxEnableMap.setCheckState(QtCore.Qt.Unchecked)
    self.__signal_checkBoxEnableMap_stateChanged(QtCore.Qt.Unchecked)
  def __signal_comboBoxTypeMap_currentIndexChanged(self, index):
    self.__setWebViewMap( index )
  def __signal_canvas_extentsChanged(self):
    if self.__canvas.layerCount() == 0 or not self.webViewMap.isVisible():
      return
    if self.checkBoxEnableMap.checkState() == QtCore.Qt.Checked:
      self.__refreshMapOL()
  def __signal_pbRefresh_clicked(self, checked):
    index = self.comboBoxTypeMap.currentIndex()
    self.__setWebViewMap( index )
  def __signal_pbAddRaster_clicked(self, checked):
    index = self.comboBoxTypeMap.currentIndex()
    layer = self.__olLayerTypeRegistry.getByIdx( index )
    layer.addLayer()
  def __signal_pbCopyKml_clicked(self, cheked):
    # Extent Openlayers
    action = "map.getExtent().toGeometry().toString();" 
    wkt = self.webViewMap.page().mainFrame().evaluateJavaScript(action).toString()
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
    clipBoard = QtGui.QApplication.clipboard()
    clipBoard.setText(kml)
  def __signal_pbSaveImg_clicked(self, cheked):
    fileName = QtGui.QFileDialog.getSaveFileName(self, QtGui.QApplication.translate("OpenLayersOverviewWidget", "Save image"), self.__fileNameImg, QtGui.QApplication.translate("OpenLayersOverviewWidget", "Image(*.jpg)"))
    if not fileName == '':
      self.__fileNameImg = fileName
    else:
      return
    img = QtGui.QImage(self.webViewMap.page().mainFrame().contentsSize(), QtGui.QImage.Format_ARGB32_Premultiplied)
    imgPainter = QtGui.QPainter()
    imgPainter.begin(img)
    self.webViewMap.page().mainFrame().render(imgPainter)
    imgPainter.end()
    img.save( fileName, "JPEG")
  def __signal_webViewMap_loadFinished(self, ok):
    if ok == False:
      QtGui.QMessageBox.warning(self, QtGui.QApplication.translate("OpenLayersOverviewWidget", "OpenLayers Overview"), QtGui.QApplication.translate("OpenLayersOverviewWidget", "Error loading page!"))
    else:
      self.__refreshMapOL()
    self.lbStatusRead.setVisible( False )
    self.webViewMap.setVisible( True )
    self.disconnect(self.webViewMap.page().mainFrame(), QtCore.SIGNAL("loadFinished (bool)"),
                 self.__signal_webViewMap_loadFinished)
  def __setWebViewMap(self, idComboTypMap):
    layer = self.__olLayerTypeRegistry.getByIdx( idComboTypMap )
    self.lbStatusRead.setText( QtGui.QApplication.translate("OpenLayersOverviewWidget", "Loading %1...").arg( layer.name ) )
    self.lbStatusRead.setVisible( True )
    self.webViewMap.setVisible( False )
    self.connect(self.webViewMap.page().mainFrame(), QtCore.SIGNAL("loadFinished (bool)"),
                 self.__signal_webViewMap_loadFinished)
    self.webViewMap.page().mainFrame().load( QtCore.QUrl( layer.fileUrl() ) )
  def __refreshMapOL(self):
    action = "map.setCenter(new OpenLayers.LonLat(%f, %f));" % self.__getCenterLongLat2OL()
    self.webViewMap.page().mainFrame().evaluateJavaScript(action)
    action = "map.zoomToScale(%f);" % self.__canvas.scale()
    self.webViewMap.page().mainFrame().evaluateJavaScript(action)
    self.webViewMap.page().mainFrame().evaluateJavaScript("oloMarker.changeMarker();")
  def __getCenterLongLat2OL(self):
    pntCenter = self.__canvas.extent().center()
    srsCanvas = self.__canvas.mapRenderer().destinationSrs()
    if srsCanvas != self.__srsOL:
      coodTrans = core.QgsCoordinateTransform(srsCanvas, self.__srsOL)
      pntCenter = coodTrans.transform(pntCenter, core.QgsCoordinateTransform.ForwardTransform)
    return tuple( [ pntCenter.x(),pntCenter.y() ] )
