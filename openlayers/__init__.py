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
 This script initializes the plugin, making it known to QGIS.
"""
def name():
  return "OpenLayers Plugin"
def description():
  return "TMS, Google Maps, Yahoo Maps, Bing Maps layers and more"
def version():
  return "Version 0.1"
def qgisMinimumVersion():
  return "1.5"
def classFactory(iface):
  from openlayersplugin import OpenlayersPlugin
  return OpenlayersPlugin(iface)
