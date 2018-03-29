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

from .weblayer import WebLayer3857
from qgis.PyQt.QtCore import QSettings


class OlOSMThunderforest(WebLayer3857):

    emitsLoadEnd = True

    def __init__(self, name, layer):
        WebLayer3857.__init__(self, groupName="OSM/Thunderforest",
                              groupIcon="osm_icon.png",
                              name=name, html='osm_thunderforest.html',
                              xyzUrl='inline')
        self._layer = layer

    def apiKey(self):
        return QSettings().value("Plugin-OpenLayers/thunderforestApiKey")

    def html_url(self):
        url = WebLayer3857.html_url(self)
        url += "?layer=%s" % self._layer
        if self.apiKey():
            url += "&key=%s" % self.apiKey().strip()
        return url

    def xyzUrlConfig(self):
        if self.apiKey():
            keyarg = self.apiKey().strip()
            return 'https://tile.thunderforest.com/%s/{z}/{x}/{y}.png?apikey=%s' % (self._layer, keyarg)
        else:
            return 'https://tile.thunderforest.com/%s/{z}/{x}/{y}.png' % (self._layer)


class OlOpenCycleMapLayer(OlOSMThunderforest):

    def __init__(self):
        OlOSMThunderforest.__init__(self, name='OpenCycleMap', layer='cycle')


class OlOCMLandscapeLayer(OlOSMThunderforest):

    def __init__(self):
        OlOSMThunderforest.__init__(self, name='OCM Landscape',
                                    layer='landscape')


class OlOCMPublicTransportLayer(OlOSMThunderforest):

    def __init__(self):
        OlOSMThunderforest.__init__(self, name='OCM Public Transport',
                                    layer='transport')


class OlOCMOutdoorstLayer(OlOSMThunderforest):

    def __init__(self):
        OlOSMThunderforest.__init__(self, name='Outdoors', layer='outdoors')


class OlOCMTransportDarkLayer(OlOSMThunderforest):

    def __init__(self):
        OlOSMThunderforest.__init__(self, name='Transport Dark',
                                    layer='transport-dark')


class OlOCMSpinalMapLayer(OlOSMThunderforest):

    def __init__(self):
        OlOSMThunderforest.__init__(self, name='Spinal Map',
                                    layer='spinal-map')


class OlOCMPioneerLayer(OlOSMThunderforest):

    def __init__(self):
        OlOSMThunderforest.__init__(self, name='Pioneer', layer='pioneer')


class OlOCMMobileAtlasLayer(OlOSMThunderforest):

    def __init__(self):
        OlOSMThunderforest.__init__(self, name='Mobile Atlas',
                                    layer='mobile-atlas')


class OlOCMNeighbourhoodLayer(OlOSMThunderforest):

    def __init__(self):
        OlOSMThunderforest.__init__(self, name='Neighbourhood',
                                    layer='neighbourhood')
