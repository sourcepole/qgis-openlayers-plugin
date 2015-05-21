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


class OlMapQuestLayer(WebLayer3857):

    emitsLoadEnd = True

    def __init__(self, name, html, gdalTMS=None):
        WebLayer3857.__init__(self, groupName="MapQuest", groupIcon="map_quest_icon.png",
                              name=name, html=html, gdalTMS=gdalTMS)


class OlMapQuestOSMLayer(OlMapQuestLayer):

    def __init__(self):
        OlMapQuestLayer.__init__(self, name='MapQuest-OSM', html='map_quest_osm.html', gdalTMS='map_quest_osm.xml')


class OlMapQuestOpenAerialLayer(OlMapQuestLayer):

    def __init__(self):
        OlMapQuestLayer.__init__(self, name='MapQuest Open Aerial', html='map_quest_open_aerial.html', gdalTMS='map_quest_open_aerial.xml')
