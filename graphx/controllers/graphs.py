from datetime import datetime
from itertools import islice, imap
from operator import itemgetter
from functools import wraps

from twisted.web.http import CONFLICT, CREATED, NOT_FOUND
from werkzeug.urls import url_unquote

import networkx as nx

from graphx.common import DATETIME_FORMAT, _getPaging

itemgetter0 = itemgetter(0)


def _reprGraph(graph):
    data = dict(graph.graph)
    data['name'] = graph.name
    return data

def create(request):
    data = request.json()
    name = data['name']

    if name in request.app.graphs:
        return request.respondJson({'message': 'graph exists'},
                                   CONFLICT)
    graph = nx.DiGraph(**data.get('attributes', {}))
    graph.graph['created'] = datetime.utcnow().strftime(DATETIME_FORMAT)
    request.app.graphs[name] = graph
    graph.name = name

    request.respondJson(_reprGraph(graph), CREATED)

def loadGraph(argName='graph'):

    def decorator(fc):

        @wraps(fc)
        def wrapped(request, **kwargs):
            graphName = kwargs.pop(argName)
            graphName = url_unquote(graphName)
            try:
                graph = request.app.graphs[graphName]
            except KeyError:
                return request.respondJson({'message': 'graph {0} not found'.format(graphName)},
                                           NOT_FOUND)

            graph.name = graphName
            kwargs[argName] = graph

            return fc(request, **kwargs)

        return wrapped

    return decorator

@loadGraph()
def show(request, graph):
    request.respondJson(_reprGraph(graph))

@loadGraph()
def delete(request, graph):
    try:
        next(graph.nodes_iter())
    except StopIteration:
        # graph empty, proceed to delete
        pass
    else:
        # graph not empty
        force = request.json().get('force')
        if force:
            # 'force' flag set, proceed to delete
            pass
        else:
            # flag is false or not set
            return request.respondJson({'message': 'graph not empty'},
                                       CONFLICT)

    del request.app.graphs[graph.name]

    request.respondJson({'message': 'deleted successfuly'})

def _reprNode(g, nodeName):
    try:
        node = g.node[nodeName]
    except KeyError:
        raise KeyError('node not in graph')
    data = dict(node)
    data['name'] = nodeName
    data['graph'] = g.name
    return data

@loadGraph()
def createNode(request, graph):
    data = request.json()
    nodeName = data['nodeName']

    if graph.has_node(nodeName):
        return request.respondJson({'message': 'node exists'},
                                   CONFLICT)

    attrib = data.get('attributes', {})
    attrib['created'] = datetime.utcnow().strftime(DATETIME_FORMAT)
    graph.add_node(nodeName, **attrib)

    request.respondJson(_reprNode(graph, nodeName),
                        CREATED)

@loadGraph()
def showNode(request, graph, nodeName):
    nodeName = url_unquote(nodeName)
    try:
        data = _reprNode(graph, nodeName)
    except KeyError, err:
        return request.respondJson({'message': err.message},
                                   NOT_FOUND)
    request.respondJson(data)

@loadGraph()
def deleteNode(request, graph, nodeName):
    nodeName = url_unquote(nodeName)
    if not graph.has_node(nodeName):
        return request.respondJson({'message': 'node not in graph'},
                                   NOT_FOUND)
    try:
        next(graph.neighbors_iter(nodeName))
    except StopIteration:
        # no neighbours, ok to delete
        pass
    else:
        return request.respondJson({'message': 'node has edges'},
                                   CONFLICT)

    graph.remove_node(nodeName)
    request.respondJson({'message': 'node deleted'})

def listGraphs(request):
    igraphs = iter(request.app.graphs)
    offset, limit = _getPaging(request)
    igraphs = islice(igraphs, offset, offset + limit)
    data = {'names': tuple(igraphs)}
    request.respondJson(data)

def _iterFilterNodes(nodes, attrib):
    if len(attrib) == 0:
        for nodeName, nodeData in nodes:
            yield nodeName, nodeData
    else:
        attrib = attrib.items()
        for nodeName, nodeData in nodes:
            match = True
            for k, v in attrib:
                if nodeData.get(k) != v:
                    match = False
                    break
            if match:
                yield nodeName, nodeData

def _iterNeigborsEdges(graph, start):
    ineighbors = graph.neighbors_iter(start)
    start_ = graph[start]
    for end in ineighbors:
        edge = start_[end]
        yield end, edge

def _iterFilterEdges(edges, attrib):
    if len(attrib) == 0:
        for edge in edges:
            yield edge
    else:
        attrib = attrib.items()
        for end, edge in edges:
            match = True
            for k, v in attrib:
                if edge.get(k) != v:
                    match = False
                    break
            if match:
                yield end, edge

@loadGraph()
def listNodes(request, graph):
    inodes = graph.nodes_iter(data=True)
    attrib = request.json()
    inodes = _iterFilterNodes(inodes, attrib)
    offset, limit = _getPaging(request)
    inodes = islice(inodes, offset, offset + limit)
    inodes = imap(itemgetter0, inodes)

    data = {'names': tuple(inodes)}
    request.respondJson(data)

@loadGraph()
def createEdge(request, graph, startNode, endNode):
    start = url_unquote(startNode)
    end = url_unquote(endNode)
    if not (graph.has_node(start) and graph.has_node(end)):
        return request.respondJson({'message': 'node not in graph'},
                                   NOT_FOUND)

    attrib = request.json()
    attrib['created'] = datetime.utcnow().strftime(DATETIME_FORMAT)

    graph.add_edge(start, end, **attrib)
    data = graph.edge[start][end]
    data.update({'start': start, 'end': end,
                 'graph': graph.name})

    request.respondJson(data, CREATED)

@loadGraph()
def showEdge(request, graph, startNode, endNode):
    start = url_unquote(startNode)
    end = url_unquote(endNode)
    try:
        edge = graph.edge[start][end]
    except KeyError:
        return request.respondJson(
            {'message': 'nodes not in graph or not linked'},
            NOT_FOUND)

    edge = dict(edge)
    edge.update({'start': start, 'end': end,
                 'graph': graph.name})
    request.respondJson(edge)

@loadGraph()
def deleteEdge(request, graph, startNode, endNode):
    start = url_unquote(startNode)
    end = url_unquote(endNode)
    try:
        _edge = graph.edge[start][end]
    except KeyError:
        return request.respondJson({'message': 'edge not in graph'},
                                   NOT_FOUND)

    graph.remove_edge(start, end)
    request.respondJson({'message': 'edge deleted'})

@loadGraph()
def listEdges(request, graph, startNode):
    if not graph.has_node(startNode):
        return request.respondJson({'message': 'node not in graph'},
                                   NOT_FOUND)

    start = url_unquote(startNode)
    iNeighborsEdges = _iterNeigborsEdges(graph, start)

    attrib = request.json()
    iNeighborsEdges = _iterFilterEdges(iNeighborsEdges, attrib)

    offset, limit = _getPaging(request)
    iNeighborsEdges = islice(iNeighborsEdges, offset, offset + limit)

    request.respondJson({'neighbors': dict(iNeighborsEdges)})
