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


class OlYahooMapsLayer(WebLayer3857):

    emitsLoadEnd = False

    def __init__(self, name, html):
        WebLayer3857.__init__(self, groupName="Yahoo Maps", groupIcon="yahoo_icon.png",
                              name=name, html=html)


class OlYahooStreetLayer(OlYahooMapsLayer):

    def __init__(self):
        OlYahooMapsLayer.__init__(self, name='Yahoo Street', html='yahoo_street.html')


class OlYahooHybridLayer(OlYahooMapsLayer):

    def __init__(self):
        OlYahooMapsLayer.__init__(self, name='Yahoo Hybrid', html='yahoo_hybrid.html')


class OlYahooSatelliteLayer(OlYahooMapsLayer):

    def __init__(self):
        OlYahooMapsLayer.__init__(self, name='Yahoo Satellite', html='yahoo_satellite.html')
