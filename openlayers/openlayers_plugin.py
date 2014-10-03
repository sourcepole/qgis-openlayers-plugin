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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import resources_rc
from about_dialog import AboutDialog
from openlayers_overview import OLOverview
from openlayers_layer import OpenlayersLayer
from openlayers_plugin_layer_type import OpenlayersPluginLayerType
from weblayers.weblayer_registry import WebLayerTypeRegistry
from weblayers.google_maps import OlGooglePhysicalLayer, OlGoogleStreetsLayer, OlGoogleHybridLayer, OlGoogleSatelliteLayer
from weblayers.osm import OlOpenStreetMapLayer, OlOpenCycleMapLayer, OlOCMLandscapeLayer, OlOCMPublicTransportLayer, OlOSMHumanitarianDataModelLayer
from weblayers.bing_maps import OlBingRoadLayer, OlBingAerialLayer, OlBingAerialLabelledLayer
from weblayers.apple_maps import OlAppleiPhotoMapLayer
from weblayers.osm_stamen import OlOSMStamenTonerLayer, OlOSMStamenWatercolorLayer, OlOSMStamenTerrainLayer
from weblayers.map_quest import OlMapQuestOSMLayer, OlMapQuestOpenAerialLayer
import os.path


class OpenlayersPlugin:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, "i18n", "openlayers_{}.qm".format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self._olLayerTypeRegistry = WebLayerTypeRegistry(self)
        self.olOverview = OLOverview(iface, self._olLayerTypeRegistry)
        self.dlgAbout = AboutDialog()

    def initGui(self):
        self._olMenu = QMenu("OpenLayers plugin")
        self._olMenu.setIcon(QIcon(":/plugins/openlayers/openlayers.png"))

        # Overview
        self.overviewAddAction = QAction(QApplication.translate("OpenlayersPlugin", "OpenLayers Overview"), self.iface.mainWindow())
        self.overviewAddAction.setCheckable(True)
        self.overviewAddAction.setChecked(False)
        QObject.connect(self.overviewAddAction, SIGNAL("toggled(bool)"), self.olOverview.setVisible)
        self._olMenu.addAction(self.overviewAddAction)

        self._actionAbout = QAction("Terms of Service / About", self.iface.mainWindow())
        QObject.connect(self._actionAbout, SIGNAL("triggered()"), self.dlgAbout, SLOT("show()"))
        #? self._actionAbout.triggered.connect(self.dlgAbout, SLOT("show()"))
        self._olMenu.addAction(self._actionAbout)

        self._olLayerTypeRegistry.register(OlGooglePhysicalLayer())
        self._olLayerTypeRegistry.register(OlGoogleStreetsLayer())
        self._olLayerTypeRegistry.register(OlGoogleHybridLayer())
        self._olLayerTypeRegistry.register(OlGoogleSatelliteLayer())

        self._olLayerTypeRegistry.register(OlOpenStreetMapLayer())
        self._olLayerTypeRegistry.register(OlOpenCycleMapLayer())
        self._olLayerTypeRegistry.register(OlOCMLandscapeLayer())
        self._olLayerTypeRegistry.register(OlOCMPublicTransportLayer())
        self._olLayerTypeRegistry.register(OlOSMHumanitarianDataModelLayer())

        self._olLayerTypeRegistry.register(OlBingRoadLayer())
        self._olLayerTypeRegistry.register(OlBingAerialLayer())
        self._olLayerTypeRegistry.register(OlBingAerialLabelledLayer())

        self._olLayerTypeRegistry.register(OlOSMStamenTonerLayer())
        self._olLayerTypeRegistry.register(OlOSMStamenWatercolorLayer())
        self._olLayerTypeRegistry.register(OlOSMStamenTerrainLayer())

        self._olLayerTypeRegistry.register(OlMapQuestOSMLayer())
        self._olLayerTypeRegistry.register(OlMapQuestOpenAerialLayer())

        self._olLayerTypeRegistry.register(OlAppleiPhotoMapLayer())

        for group in self._olLayerTypeRegistry.groups():
            groupMenu = group.menu()
            for layer in self._olLayerTypeRegistry.groupLayerTypes(group):
                layer.addMenuEntry(groupMenu, self.iface.mainWindow())
            self._olMenu.addMenu(groupMenu)

        #Create Web menu, if it doesn't exist yet
        self.iface.addPluginToWebMenu("_tmp", self._actionAbout)
        self._menu = self.iface.webMenu()
        self._menu.addMenu(self._olMenu)
        self.iface.removePluginWebMenu("_tmp", self._actionAbout)

        # Register plugin layer type
        self.pluginLayerType = OpenlayersPluginLayerType(self.iface, self.setReferenceLayer,
                                                    self._olLayerTypeRegistry)
        QgsPluginLayerRegistry.instance().addPluginLayerType(self.pluginLayerType)

    def unload(self):
        self.iface.webMenu().removeAction(self._olMenu.menuAction())

        self.olOverview.setVisible(False)
        del self.olOverview

        # Unregister plugin layer type
        QgsPluginLayerRegistry.instance().removePluginLayerType(OpenlayersLayer.LAYER_TYPE)

    def addLayer(self, layerType):
        layer = OpenlayersLayer(self.iface, self._olLayerTypeRegistry)
        layer.setLayerName(layerType.displayName)
        layer.setLayerType(layerType)
        if layer.isValid():
            coordRefSys = layerType.coordRefSys(self.canvasCrs())
            self.setMapCrs(coordRefSys)
            QgsMapLayerRegistry.instance().addMapLayer(layer)

            # last added layer is new reference
            self.setReferenceLayer(layer)

    def setReferenceLayer(self, layer):
        self.layer = layer

    def removeLayer(self, layerId):
        if self.layer is not None:
            if QGis.QGIS_VERSION_INT >= 10900:
                if self.layer.id() == layerId:
                    self.layer = None
            else:
                if self.layer.getLayerID() == layerId:
                    self.layer = None
            # TODO: switch to next available OpenLayers layer?

    def canvasCrs(self):
        mapCanvas = self.iface.mapCanvas()
        if QGis.QGIS_VERSION_INT >= 20300:
            #crs = mapCanvas.mapRenderer().destinationCrs()
            crs = mapCanvas.mapSettings().destinationCrs()
        elif QGis.QGIS_VERSION_INT >= 10900:
            crs = mapCanvas.mapRenderer().destinationCrs()
        else:
            crs = mapCanvas.mapRenderer().destinationSrs()
        return crs

    def setMapCrs(self, coordRefSys):
        mapCanvas = self.iface.mapCanvas()
        # On the fly
        if QGis.QGIS_VERSION_INT >= 20300:
            mapCanvas.setCrsTransformEnabled(True)
        else:
            mapCanvas.mapRenderer().setProjectionsEnabled(True)
        canvasCrs = self.canvasCrs()
        if canvasCrs != coordRefSys:
            coordTrans = QgsCoordinateTransform(canvasCrs, coordRefSys)
            extMap = mapCanvas.extent()
            extMap = coordTrans.transform(extMap, QgsCoordinateTransform.ForwardTransform)
            if QGis.QGIS_VERSION_INT >= 20300:
                mapCanvas.setDestinationCrs(coordRefSys)
            elif QGis.QGIS_VERSION_INT >= 10900:
                mapCanvas.mapRenderer().setDestinationCrs(coordRefSys)
            else:
                mapCanvas.mapRenderer().setDestinationSrs(coordRefSys)
            mapCanvas.freeze(False)
            mapCanvas.setMapUnits(coordRefSys.mapUnits())
            mapCanvas.setExtent(extMap)
