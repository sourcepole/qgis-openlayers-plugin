# -*- coding: utf-8 -*-
"""
/***************************************************************************
    Useful network functions
                             -------------------
    begin            : 2011-03-01
    copyright        : (C) 2011 by Luiz Motta
    author           : Luiz P. Motta
    email            : motta _dot_ luiz _at_ gmail.com
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
from PyQt4 import QtCore, QtNetwork

def getProxy():
  # Adaption by source of "Plugin Installer - Version 1.0.10" 
  settings = QtCore.QSettings()
  settings.beginGroup("proxy")
  if settings.value("/proxyEnabled").toBool():
    proxy = QtNetwork.QNetworkProxy()
    proxyType = settings.value( "/proxyType", QtCore.QVariant(0)).toString()
    if proxyType in ["1","Socks5Proxy"]: proxy.setType(QtNetwork.QNetworkProxy.Socks5Proxy)
    elif proxyType in ["2","NoProxy"]: proxy.setType(QtNetwork.QNetworkProxy.NoProxy)
    elif proxyType in ["3","HttpProxy"]: proxy.setType(QtNetwork.QNetworkProxy.HttpProxy)
    elif proxyType in ["4","HttpCachingProxy"] and QT_VERSION >= 0X040400: proxy.setType(QtNetwork.QNetworkProxy.HttpCachingProxy)
    elif proxyType in ["5","FtpCachingProxy"] and QT_VERSION >= 0X040400: proxy.setType(QtNetwork.QNetworkProxy.FtpCachingProxy)
    else: proxy.setType(QtNetwork.QNetworkProxy.DefaultProxy)
    proxy.setHostName(settings.value("/proxyHost").toString())
    proxy.setPort(settings.value("/proxyPort").toUInt()[0])
    proxy.setUser(settings.value("/proxyUser").toString())
    proxy.setPassword(settings.value("/proxyPassword").toString())
    return proxy
  else:
    return None
  settings.endGroup()
