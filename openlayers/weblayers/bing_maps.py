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


class OlBingMapsLayer(WebLayer3857):

    emitsLoadEnd = True

    def __init__(self, name, html):
        WebLayer3857.__init__(self, groupName="Bing Maps", groupIcon="bing_icon.png",
                              name=name, html=html)


class OlBingRoadLayer(OlBingMapsLayer):

    def __init__(self):
        OlBingMapsLayer.__init__(self, name='Bing Road', html='bing_road.html')


class OlBingAerialLayer(OlBingMapsLayer):

    def __init__(self):
        OlBingMapsLayer.__init__(self, name='Bing Aerial', html='bing_aerial.html')


class OlBingAerialLabelledLayer(OlBingMapsLayer):

    def __init__(self):
        OlBingMapsLayer.__init__(self, name='Bing Aerial with labels', html='bing_aerial-labels.html')
