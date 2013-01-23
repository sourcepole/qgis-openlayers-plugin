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
 This script initializes the plugin, making it known to QGIS.
"""

##lines for eclipse debug. Comment me when publishing.
##Use DEBUG Perspective and Start the pydev server
#import os, sys
#sys.path.append(r"C:\eclipse\plugins\org.python.pydev.debug_1.6.5.2011022818\pysrc")
#import pydevd
#pydevd.settrace()
##end of eclipse debug

def name():
  return "OpenLayers Plugin"
def description():
  return "OpenStreetMap, Google Maps, Bing Maps layers and more"
def version():
  return "1.1.0"
def qgisMinimumVersion():
  return "1.7.4"
def author():
  return "Sourcepole, Luiz Motta &amp; other contributors"
def email():
  return "pka@sourcepole.ch"
def icon():
  return "openlayers.png"

def homepage():
  return "http://hub.qgis.org/projects/openlayers/wiki"
def classFactory(iface):
  from openlayers_plugin import OpenlayersPlugin
  return OpenlayersPlugin(iface)
