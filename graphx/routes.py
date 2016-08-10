from werkzeug.routing import Rule, Map

from graphx.controllers import index
from graphx.controllers import graphs
from graphx.controllers import paths
from graphx.controllers import service

url_map = Map([
    Rule('/', endpoint=index),
    Rule('/graphs', endpoint=graphs.create, methods=['POST']),
    Rule('/graphs', endpoint=graphs.listGraphs, methods=['GET']),
    Rule('/graphs/<graph>', endpoint=graphs.show, methods=['GET']),
    Rule('/graphs/<graph>', endpoint=graphs.delete, methods=['DELETE']),
    Rule('/graphs/<graph>/nodes', endpoint=graphs.createNode, methods=['POST']),
    Rule('/graphs/<graph>/nodes', endpoint=graphs.listNodes, methods=['GET']),
    Rule('/graphs/<graph>/nodes/<nodeName>', endpoint=graphs.showNode, methods=['GET']),
    Rule('/graphs/<graph>/nodes/<nodeName>', endpoint=graphs.deleteNode, methods=['DELETE']),
    Rule('/graphs/<graph>/edges/<startNode>/<endNode>', endpoint=graphs.createEdge, methods=['POST']),
    Rule('/graphs/<graph>/edges/<startNode>/<endNode>', endpoint=graphs.showEdge, methods=['GET']),
    Rule('/graphs/<graph>/edges/<startNode>/<endNode>', endpoint=graphs.deleteEdge, methods=['DELETE']),
    Rule('/graphs/<graph>/edges/<startNode>', endpoint=graphs.listEdges, methods=['GET']),
    Rule('/graphs/<graph>/paths/simple/<startNode>/<endNode>', endpoint=paths.simple, methods=['GET']),
    Rule('/graphs/<graph>/paths/cycles', endpoint=paths.cycles, methods=['GET']),
    Rule('/graphs/<graph>/paths/longest', endpoint=paths.longestPath, methods=['GET']),
    Rule('/graphs/<graph>/topologicalsort', endpoint=paths.topologicalSort, methods=['GET']),
    Rule('/graphs/<graph>/paths/query', endpoint=paths.query, methods=['GET']),
    Rule('/_/service/stop', endpoint=service.stop, methods=['PUT']),
])
