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


class WikimediaLayer(WebLayer3857):

    emitsLoadEnd = True

    def __init__(self, name, html, gdalTMS=None):
        WebLayer3857.__init__(self, groupName="Wikimedia Maps",
                              groupIcon="wikimedia_icon.png",
                              name=name, html=html, gdalTMS=gdalTMS)


class WikimediaLabelledLayer(WikimediaLayer):

    def __init__(self):
        WikimediaLayer.__init__(self, name='Wikimedia labelled layer', html='wikimedia.html', gdalTMS='wikimedia.xml')


class WikimediaUnLabelledLayer(WikimediaLayer):

    def __init__(self):
        WikimediaLayer.__init__(self, name='Wikimedia unlabelled layer', html='wikimedia_nolabels.html', gdalTMS='wikimedia_nolabels.xml')

