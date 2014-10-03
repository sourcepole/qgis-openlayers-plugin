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

from weblayer import WebLayerGroup


class WebLayerTypeRegistry:
    """Registry of OL web Layers"""
    def __init__(self, plugin):
        self._plugin = plugin
        self._groups = {}
        self._olLayerTypes = {}
        self._layerTypeId = 0  # Sequence for ID
        self._olLayerTypeNames = {}

    def group(self, name, icon):
        """Create group and register in registry"""
        if name not in self._groups:
            self._groups[name] = WebLayerGroup(name, icon)
        return self._groups[name]

    def groups(self):
        return self._groups.values()

    def register(self, layerType):
        layerType.group = self.group(layerType.groupName, layerType.groupIcon)
        layerType.setAddLayerCallback(self._plugin.addLayer)
        layerType.layerTypeId = self._layerTypeId
        self._olLayerTypes[self._layerTypeId] = layerType
        self._layerTypeId += 1
        self._olLayerTypeNames[layerType.layerTypeName] = layerType

    def types(self):
        return self._olLayerTypes.values()

    def getById(self, id):
        if self._olLayerTypes.has_key(id):
            return self._olLayerTypes[id]
        else:
            return None

    def getByName(self, name):
        if self._olLayerTypeNames.has_key(name):
            return self._olLayerTypeNames[name]
        else:
            return None

    def groupLayerTypes(self, group):
        lst = []
        for lyr in self.types():
            if lyr.group == group:
                lst.append(lyr)
        return lst
