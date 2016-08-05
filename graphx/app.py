from os import environ, walk
from os.path import dirname, abspath
from os.path import join as path_join

import networkx as nx
from xml.etree.cElementTree import ParseError

from twisted.internet import reactor
from twisted.internet.task import deferLater


PERSIST_INTERVAL = int(environ.get('GRAPHX_PERSIST_INTERVAL', 300))

try:
    PERSIST_PATH = environ['GRAPHX_PERSIST_PATH']
except KeyError:
    PERSIST_PATH = dirname(dirname(abspath(__file__)))


class Application(object):

    def persistGraph(self, name, g):
        filepath = path_join(self._persistPath, name)
        nx.write_graphml(g, filepath)

    def periodicPersist(self):
        for name, g in self.graphs.iteritems():
            self.persistGraph(name, g)

        deferLater(reactor, PERSIST_INTERVAL, self.periodicPersist)

    def loadGraph(self, filename):
        filepath = path_join(self._persistPath, filename)
        try:
            g = nx.read_graphml(filepath)
        except (nx.NetworkXError, ParseError, IndexError):
            return
        name = filename
        self.graphs[name] = g

    def loadAll(self):
        for curDir, _dirNames, filenames in walk(self._persistPath):
            if curDir != self._persistPath:
                continue
            map(self.loadGraph, filenames)

    def onStart(self):
        self.graphs = {}

        self._persistPath = PERSIST_PATH
        self.loadAll()

        deferLater(reactor, PERSIST_INTERVAL, self.periodicPersist)

    def onStop(self):
        while self.graphs:
            name, g = self.graphs.popitem()
            self.persistGraph(name, g)
