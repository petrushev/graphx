from itertools import islice

from twisted.web.http import NOT_FOUND
from werkzeug.urls import url_unquote

import networkx as nx
from networkx.exception import NetworkXUnfeasible

from graphx.common import _getPaging
from graphx.controllers.graphs import loadGraph

@loadGraph()
def simple(request, graph, startNode, endNode):
    start = url_unquote(startNode)
    end = url_unquote(endNode)
    if not (graph.has_node(start) and graph.has_node(end)):
        return request.respondJson({'message': 'node not in graph'},
                                   NOT_FOUND)

    ipaths = nx.shortest_simple_paths(graph, start, end)

    data = {'graph': graph.name,
            'start': start, 'end': end,
            'paths': tuple(ipaths)}
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
