from itertools import islice

from twisted.web.http import NOT_FOUND, BAD_REQUEST
from werkzeug.urls import url_unquote

import networkx as nx
from networkx.exception import NetworkXUnfeasible

from graphx.common import _getPaging, matchAttributes
from graphx.controllers.graphs import loadGraph


@loadGraph()
def simple(request, graph, startNode, endNode):
    start = url_unquote(startNode)
    end = url_unquote(endNode)
    if not (graph.has_node(start) and graph.has_node(end)):
        return request.respondJson({'message': 'node not in graph'},
                                   NOT_FOUND)

    ipaths = nx.shortest_simple_paths(graph, start, end)

    data = {'paths': tuple(ipaths)}
    request.respondJson(data)

@loadGraph()
def cycles(request, graph):
    offset, limit = _getPaging(request)

    icycles = nx.simple_cycles(graph)
    icycles = islice(icycles, offset, offset + limit)

    request.respondJson({'cycles': tuple(icycles)})

@loadGraph()
def topologicalSort(request, graph):
    try:
        sorted_ = nx.topological_sort(graph)
    except NetworkXUnfeasible, err:
        return request.respondJson({'message': err.message}, NOT_FOUND)

    request.respondJson({'nodes': sorted_})

@loadGraph()
def longestPath(request, graph):
    try:
        path_ = nx.dag_longest_path(graph)
    except NetworkXUnfeasible, err:
        return request.respondJson({'message': err.message}, NOT_FOUND)

    request.respondJson({'longestPath': path_})

@loadGraph()
def query(request, graph):
    data = request.json()
    nodeAttributes = data['nodeAttributes']
    edgeAttributes = data['edgeAttributes']

    if len(edgeAttributes) != len(nodeAttributes) - 1:
        return request.respondJson({'message': 'incompatible filter attributes'},
                                   BAD_REQUEST)

    startAttr = nodeAttributes.pop(0)

    start = startAttr.pop('name', None)
    if start is not None:
        if graph.has_node(start) and matchAttributes(graph.node[start], startAttr):
            paths = [(start,)]
        else:
            return request.respondJson({'paths': []})

    else:
        istart = graph.nodes_iter(data=True)
        paths = [(start,)
                 for start, startData in istart
                 if matchAttributes(startData, startAttr)]

    for edgeAttr, targetAttr in zip(edgeAttributes, nodeAttributes):
        paths = _iterExpandPaths(graph, paths, targetAttr, edgeAttr)

    request.respondJson({'paths': tuple(paths)})

def _iterExpandPaths(graph, paths, targetAttr, edgeAttr):
    targetFilterName = targetAttr.pop('name', None)
    for currentPath in paths:
        currentStart = currentPath[-1]
        currentStartNode = graph[currentStart]

        for target in graph.successors_iter(currentStart):
            if targetFilterName is not None and target != targetFilterName:
                continue

            # check for cycle
            if target in currentPath:
                continue

            # filter edges
            edge = currentStartNode[target]
            if not matchAttributes(edge, edgeAttr):
                continue

            # filter target
            if not matchAttributes(graph.node[target], targetAttr):
                continue

            yield currentPath + (target,)
