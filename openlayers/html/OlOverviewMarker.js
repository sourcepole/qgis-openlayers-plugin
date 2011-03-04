/*
****************************************************************************
Operlayer Overview Marker
                             -------------------
begin                : 2010-03-03
copyright            : (C) 2010 by Luiz Motta
email                : motta.luiz at gamil.com
****************************************************************************

****************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************

Dependences:
 Libray: OpenLayers.js and MarkerCursorQGis(Python binding - @QtCore.pyqtSlot(str) )
 
Usage:
 Inside HTML:
   var oloMarker;
   // Inside init function by HTML(<body onload="init()">)
   oloMarker = OlOverviewMarker(map, getPathUpper(document.URL) + '/x.png') // x.png in upper directory of HTML
 Inside Python:
   evaluateJavaScript("oloMarker.changeMarker();")

*****************************************************************************/

function getPathUpper(url)
{
  var paths = new Array();
  paths = document.URL.split('/');
  paths.pop();paths.pop();
  return paths.join('/');
}

function OlOverviewMarker(map, urlIcon) {
    //Private
    function __createMarker(urlIcon)
    {
      var size = new OpenLayers.Size(16,16);
      var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
      var icon = new OpenLayers.Icon(urlIcon, size, offset);
      marker = new OpenLayers.Marker(new OpenLayers.LonLat(0,0), icon);
      marker.display(false);
    }
    //Public CTRL+Q
    this.changeMarker = function() {
      this.lyrMarker.removeMarker(marker);
      var extent = this.map.getExtent();
      marker.lonlat  = extent.getCenterLonLat();
      marker.display(true);
      this.lyrMarker.addMarker(marker);
      MarkerCursorQGis.changeMarker(extent.toArray().toString());
    };
    this.map = map;
    var marker;
    __createMarker(urlIcon);
    this.lyrMarker = new OpenLayers.Layer.Markers("Marker Overview");
    this.lyrMarker.addMarker(marker);
    map.addLayer(this.lyrMarker);
}
