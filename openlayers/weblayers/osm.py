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


class OlOSMLayer(WebLayer3857):

    emitsLoadEnd = True

    def __init__(self, name, html, xyzUrl=None):
        WebLayer3857.__init__(self, groupName="OpenStreetMap",
                              groupIcon="osm_icon.png",
                              name=name, html=html, xyzUrl=xyzUrl)


class OlOpenStreetMapLayer(OlOSMLayer):

    def __init__(self):
        tmsUrl = 'http://tile.openstreetmap.org/{z}/{x}/{y}.png'
        OlOSMLayer.__init__(self, name='OpenStreetMap', html='osm.html',
                            xyzUrl=tmsUrl)


class OlOSMHumanitarianDataModelLayer(OlOSMLayer):

    def __init__(self):
        tmsUrl = 'http://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png'
        OlOSMLayer.__init__(self, name='OSM Humanitarian Data Model',
                            html='osm_hdm.html', xyzUrl=tmsUrl)
