#!/usr/bin/env python
# This script uploads a plugin package on the server
#
# Author: A. Pasotti, V. Picavet

import xmlrpclib, sys, os
import getpass
from optparse import OptionParser

# Configuration
PROTOCOL='http'
SERVER='plugins.qgis.org'
PORT='80'
ENDPOINT='/plugins/RPC2/'
VERBOSE=False

def main(options, args):
    address = "%s://%s:%s@%s:%s%s" % (PROTOCOL, options.username, options.password,
            options.server, options.port, ENDPOINT)
    print "Connecting to: %s" % hidepassword(address)
    
    server = xmlrpclib.ServerProxy(address, verbose=VERBOSE)
    
    try:
        plugin_id, version_id = server.plugin.upload(xmlrpclib.Binary(open(args[0]).read()))
        print "Plugin ID: %s" % plugin_id
        print "Version ID: %s" % version_id
    except xmlrpclib.ProtocolError, err:
        print "A protocol error occurred"
        print "URL: %s" % hidepassword(err.url, 0)
        print "HTTP/HTTPS headers: %s" % err.headers
        print "Error code: %d" % err.errcode
        print "Error message: %s" % err.errmsg
    except xmlrpclib.Fault, err:
        print "A fault occurred"
        print "Fault code: %d" % err.faultCode
        print "Fault string: %s" % err.faultString

def hidepassword(url, start = 6):
    """Returns the http url with password part replaced with '*'."""
    passdeb = url.find(':', start) + 1
    passend = url.find('@')
    return "%s%s%s" % (url[:passdeb], '*' * (passend - passdeb), url[passend:])


if __name__ == "__main__":
    parser = OptionParser(usage="%prog [options] plugin.zip")
    parser.add_option("-w", "--password", dest="password",
            help="Password for plugin site", metavar="******")
    parser.add_option("-u", "--username", dest="username",
            help="Username of plugin site", metavar="user")
    parser.add_option("-p", "--port", dest="port",
            help="Server port to connect to", metavar="80")
    parser.add_option("-s", "--server", dest="server",
            help="Specify server name", metavar="plugins.qgis.org")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        print "Please specify zip file.\n"
        parser.print_help()
        sys.exit(1)
    if not options.server:
        options.server = SERVER
    if not options.port:
        options.port = PORT
    if not options.username:
        # interactive mode
        username = getpass.getuser()
        print "Please enter user name [%s] :"%username,
        res = raw_input()
        if res != "":
            options.username = res
        else:
            options.username = username
    if not options.password:
        # interactive mode
        options.password = getpass.getpass()
    main(options, args)

