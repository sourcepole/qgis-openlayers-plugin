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


class OlOSMLayer(WebLayer3857):

    emitsLoadEnd = True

    def __init__(self, name, html, gdalTMS=None):
        WebLayer3857.__init__(self, groupName="OpenStreetMap", groupIcon="osm_icon.png",
                              name=name, html=html, gdalTMS=gdalTMS)


class OlOpenStreetMapLayer(OlOSMLayer):

    def __init__(self):
        OlOSMLayer.__init__(self, name='OpenStreetMap', html='osm.html', gdalTMS='osm.xml')


class OlOpenCycleMapLayer(OlOSMLayer):

    def __init__(self):
        OlOSMLayer.__init__(self, name='OpenCycleMap', html='ocm.html', gdalTMS='ocm.xml')


class OlOCMLandscapeLayer(OlOSMLayer):

    def __init__(self):
        OlOSMLayer.__init__(self, name='OCM Landscape', html='ocm_landscape.html', gdalTMS='ocm_landscape.xml')


class OlOCMPublicTransportLayer(OlOSMLayer):

    def __init__(self):
        OlOSMLayer.__init__(self, name='OCM Public Transport', html='ocm_transport.html', gdalTMS='ocm_transport.xml')


class OlOSMHumanitarianDataModelLayer(OlOSMLayer):

    def __init__(self):
        OlOSMLayer.__init__(self, name='OSM Humanitarian Data Model', html='osm_hdm.html', gdalTMS='osm_hdm.xml')
