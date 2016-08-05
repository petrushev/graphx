import json

from twisted.web.http import Request, HTTPChannel, HTTPFactory, NOT_FOUND, OK, NOT_ALLOWED
from twisted.application.internet import TCPServer as BaseTCPServer

from werkzeug.exceptions import NotFound, MethodNotAllowed

from graphx.app import Application
from graphx.routes import url_map

NOT_FOUND_MESSAGE = {'message': 'Not found!'}
NOT_ALLOWED_MESSAGE = {'message': 'Method not allowed!'}


def getRequestFactory():

    _app = Application()
    _match = url_map.bind('').match

    class RequestFactory(Request):

        app = _app

        def process(self):
            try:
                controller, kwargs = _match(self.path, method = self.method)
            except NotFound:
                return self.respondJson(NOT_FOUND_MESSAGE, NOT_FOUND)
            except MethodNotAllowed:
                return self.respondJson(NOT_ALLOWED_MESSAGE, NOT_ALLOWED)

            self.setResponseCode(OK)
            controller(self, **kwargs)

        def writeJson(self, data):
            self.setHeader('Content-Type', 'text/json')
            self.write(json.dumps(data))

        def respondJson(self, data, code=None):
            if code is not None:
                self.setResponseCode(code)
            self.writeJson(data)
            self.finish()

        def json(self):
            try:
                return json.loads(self.content.getvalue())
            except ValueError:
                return {}

    return RequestFactory


class FrontChannel(HTTPChannel):
    requestFactory = getRequestFactory()


httpFactory = HTTPFactory.forProtocol(FrontChannel)


class TCPServer(BaseTCPServer):

    def startService(self):
        BaseTCPServer.startService(self)

        protocolFactory = self.args[1]
        app = protocolFactory.protocol.requestFactory.app
        app.onStart()

    def stopService(self):
        protocolFactory = self.args[1]
        app = protocolFactory.protocol.requestFactory.app
        app.onStop()

        BaseTCPServer.stopService(self)
