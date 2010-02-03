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
    self.creatorId = QgsPluginLayerRegistry.instance().addPluginLayerType(OpenlayersPluginLayerType())

  def unload(self):
    # Remove the plugin menu item and icon
    self.iface.removePluginMenu("OpenLayers plugin",self.action)
    self.iface.removeToolBarIcon(self.action)

    # Unregister plugin layer type
    QgsPluginLayerRegistry.instance().removePluginLayerType(OpenlayersLayer.LAYER_TYPE)

  def run(self):
    layer = OpenlayersLayer()
    if layer.isValid():
      QgsMapLayerRegistry.instance().addMapLayer(layer)
