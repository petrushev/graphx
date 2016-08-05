from os import environ

from twisted.application.service import Application

from graphx.http import TCPServer, httpFactory

BIND_ADDRESS = environ.get('GRAPHX_BIND_ADDRESS', 'localhost')
PORT = int(environ.get('GRAPHX_PORT', 8070))

application = Application('Graphx')
server = TCPServer(PORT, httpFactory, interface=BIND_ADDRESS)
server.setServiceParent(application)
