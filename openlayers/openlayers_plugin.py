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
import math

from openlayers_layer import OpenlayersLayer
from openlayers_plugin_layer_type import OpenlayersPluginLayerType

class OpenlayersPlugin:

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface

  def initGui(self):
    # Create action that will start plugin configuration
    self.action = QAction(QIcon(":/plugins/openlayers/icon.png"), "Add OpenLayers layer", self.iface.mainWindow())
    # connect the action to the run method
    QObject.connect(self.action, SIGNAL("triggered()"), self.run)

    # Add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    self.iface.addPluginToMenu("OpenLayers plugin", self.action)

    # Register plugin layer type
    QgsPluginLayerRegistry.instance().addPluginLayerType(OpenlayersPluginLayerType(self.iface))

    # Add zoom level slider
    layoutWidget = QWidget()
    layout = QVBoxLayout(layoutWidget)

    self.slider = QSlider(Qt.Horizontal, layoutWidget)
    self.slider.setTickInterval(1)
    self.slider.setTickPosition(QSlider.TicksAbove)
    self.slider.setMinimum(0)
    self.slider.setMaximum(OpenlayersLayer.MAX_ZOOM_LEVEL)
    self.slider.setSingleStep(0)
    self.slider.setPageStep(0)
    self.slider.setTracking(False)
    layout.addWidget(self.slider)

    self.zoomLabel = QLabel(layoutWidget)
    self.zoomLabel.setAlignment(Qt.AlignHCenter)
    layout.addWidget(self.zoomLabel)

    self.dw = QDockWidget("OpenLayers zoom level", None)
    self.dw.setObjectName("OpenLayersZoomLevel")
    self.dw.setAllowedAreas(Qt.LeftDockWidgetArea)
    self.dw.setWidget(layoutWidget)
    self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dw)

    QObject.connect(self.slider, SIGNAL("valueChanged(int)"), self.zoomLevelChanged)
    QObject.connect(self.slider, SIGNAL("sliderReleased()"), self.zoomSliderReleased)
    QObject.connect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.scaleChanged)

  def unload(self):
    # Remove the plugin menu item and icon
    self.iface.removePluginMenu("OpenLayers plugin",self.action)
    self.iface.removeToolBarIcon(self.action)

    # Unregister plugin layer type
    QgsPluginLayerRegistry.instance().removePluginLayerType(OpenlayersLayer.LAYER_TYPE)

    # Remove zoom level slider
    QObject.disconnect(self.slider, SIGNAL("valueChanged(int)"), self.zoomLevelChanged)
    QObject.disconnect(self.slider, SIGNAL("sliderReleased()"), self.zoomSliderReleased)
    QObject.disconnect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.scaleChanged)

    self.iface.removeDockWidget(self.dw)
    del self.dw
    self.dw = None
    del self.slider
    self.slider = None

  def run(self):
    layer = OpenlayersLayer(self.iface)
    if layer.isValid():
      QgsMapLayerRegistry.instance().addMapLayer(layer)

  def zoomLevelChanged(self, zoom):
    scale = self.iface.mapCanvas().mapRenderer().scale()
    if scale > 0:
      # adjust QGIS scale
      targetScale = OpenlayersLayer.scaleFromZoom(zoom)
      QObject.disconnect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.scaleChanged)
      self.iface.mapCanvas().zoomByFactor(targetScale / scale)
      QObject.connect(self.iface.mapCanvas(), SIGNAL("scaleChanged(double)"), self.scaleChanged)

    # update zoom label
    self.zoomLabel.setText("%d" % zoom)

  def zoomSliderReleased(self):
    if self.slider.value() == self.slider.sliderPosition():
      # update scale when clicking on current slider position
      self.zoomLevelChanged(self.slider.value())

  def scaleChanged(self, scale):
    if scale > 0:
      zoom = OpenlayersLayer.zoomFromScale(scale)
      zoomLevel = math.floor(zoom + 0.5)

      # set zoom slider to nearest level
      QObject.disconnect(self.slider, SIGNAL("valueChanged(int)"), self.zoomLevelChanged)
      self.slider.setValue(zoomLevel)
      QObject.connect(self.slider, SIGNAL("valueChanged(int)"), self.zoomLevelChanged)

      # update zoom label
      if math.fabs(zoom - zoomLevel) < 0.000001:
        self.zoomLabel.setText("%d" % zoomLevel)
      else:
        self.zoomLabel.setText("%f" % zoom)
