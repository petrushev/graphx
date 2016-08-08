from os import environ, walk
from os.path import dirname, abspath
from os.path import join as path_join
import pickle

from twisted.internet import reactor
from twisted.internet.task import deferLater


PERSIST_INTERVAL = int(environ.get('GRAPHX_PERSIST_INTERVAL', 300))

try:
    PERSIST_PATH = environ['GRAPHX_PERSIST_PATH']
except KeyError:
    PERSIST_PATH = dirname(dirname(abspath(__file__)))


class Application(object):

    def persistGraph(self, g):
        name = g.name
        filepath = path_join(self._persistPath, name)
        with open(filepath + '.pickle', 'wb') as f:
            f.write(pickle.dumps(g, pickle.HIGHEST_PROTOCOL))

    def periodicPersist(self):
        for g in self.graphs.itervalues():
            self.persistGraph(g)

        deferLater(reactor, PERSIST_INTERVAL, self.periodicPersist)

    def loadGraph(self, filename):
        filepath = path_join(self._persistPath, filename)

        if not filepath.endswith('.pickle'):
            return
        try:
            f = open(filename, 'rb')
        except IOError:
            return
        data = f.read()
        try:
            g = pickle.loads(data)
        except pickle.UnpicklingError:
            return

        name = filename[:-7]
        g.name = name
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
            _, g = self.graphs.popitem()
            self.persistGraph(g)
