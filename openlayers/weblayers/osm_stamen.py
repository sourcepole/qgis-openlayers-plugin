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

from weblayer import WebLayer3857


class OlOSMStamenLayer(WebLayer3857):

    emitsLoadEnd = True

    def __init__(self, name, html):
        WebLayer3857.__init__(self, groupName="OSM/Stamen", groupIcon="stamen_icon.png",
                              name=name, html=html)


class OlOSMStamenTonerLayer(OlOSMStamenLayer):

    def __init__(self):
        OlOSMStamenLayer.__init__(self, name='Stamen Toner/OSM', html='stamen_toner.html')


class OlOSMStamenWatercolorLayer(OlOSMStamenLayer):

    def __init__(self):
        OlOSMStamenLayer.__init__(self, name='Stamen Watercolor/OSM', html='stamen_watercolor.html')


class OlOSMStamenTerrainLayer(OlOSMStamenLayer):

    def __init__(self):
        OlOSMStamenLayer.__init__(self, name='Stamen Terrain-USA/OSM', html='stamen_terrain.html')
