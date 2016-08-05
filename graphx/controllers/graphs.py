from datetime import datetime
from itertools import islice, imap
from operator import itemgetter

from twisted.web.http import CONFLICT, CREATED, NOT_FOUND
from werkzeug.urls import url_unquote

import networkx as nx

from graphx.common import DATETIME_FORMAT


def _graphRepr(name, g):
    data = dict(g.graph)
    data['name'] = name
    data.pop('node_default', None)
    data.pop('edge_default', None)
    return data

def create(request):
    data = request.json()
    name = data['name']

    if name in request.app.graphs:
        return request.respondJson({'message': 'graph exists'},
                                   CONFLICT)
    g = nx.DiGraph(**data.get('attributes', {}))
    g.graph['created'] = datetime.utcnow().strftime(DATETIME_FORMAT)
    request.app.graphs[name] = g

    request.respondJson(_graphRepr(name, g), CREATED)

def show(request, name):
    name = url_unquote(name)
    g = _load(request, name)
    if g is None:
        return

    request.respondJson(_graphRepr(name, g))

def delete(request, name):
    name = url_unquote(name)
    g = _load(request, name)
    if g is None:
        return

    try:
        next(g.nodes_iter())
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

    del request.app.graphs[name]

    request.respondJson({'message': 'deleted successfuly'})

def _load(request, name):
    try:
        g = request.app.graphs[name]
    except KeyError:
        return request.respondJson({'message': 'graph {0} not found'.format(name)},
                            NOT_FOUND)
    return g

def _reprNode(graphName, nodeName, node):
    node = dict(node)
    node['name'] = nodeName
    node['graph'] = graphName
    return node

def createNode(request, graphName):
    graphName = url_unquote(graphName)
    g = _load(request, graphName)
    if g is None:
        return

    data = request.json()
    nodeName = data['nodeName']

    if g.has_node(nodeName):
        return request.respondJson({'message': 'node exists'},
                                   CONFLICT)

    attrib = data.get('attributes', {})
    attrib['created'] = datetime.utcnow().strftime(DATETIME_FORMAT)
    g.add_node(nodeName, **attrib)

    request.respondJson(_reprNode(graphName, nodeName, g.node[nodeName]),
                        CREATED)

def showNode(request, graphName, nodeName):
    graphName = url_unquote(graphName)
    g = _load(request, graphName)
    if g is None:
        return

    nodeName = url_unquote(nodeName)
    try:
        node = g.node[nodeName]
    except KeyError:
        return request.respondJson({'message': 'node not in graph'},
                                   NOT_FOUND)
    request.respondJson(_reprNode(graphName, nodeName, node))

def deleteNode(request, graphName, nodeName):
    graphName = url_unquote(graphName)
    g = _load(request, graphName)
    if g is None:
        return

    nodeName = url_unquote(nodeName)
    if not g.has_node(nodeName):
        return request.respondJson({'message': 'node not in graph'},
                                   NOT_FOUND)

    try:
        next(g.neighbors_iter(nodeName))
    except StopIteration:
        # no neighbours, ok to delete
        pass
    else:
        return request.respondJson({'message': 'node has edges'},
                                   CONFLICT)

    g.remove_node(nodeName)
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

def _iterNeigborsEdges(g, start, neighbors):
    start_ = g[start]
    for end in neighbors:
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

def listNodes(request, graphName):
    graphName = url_unquote(graphName)
    g = _load(request, graphName)
    if g is None:
        return

    inodes = g.nodes_iter(data=True)
    attrib = request.json()
    inodes = _iterFilterNodes(inodes, attrib)
    offset, limit = _getPaging(request)
    inodes = islice(inodes, offset, offset + limit)
    inodes = imap(itemgetter(0), inodes)

    data = {'names': tuple(inodes)}
    request.respondJson(data)

def _getPaging(request):
    offset = int(request.args.get('offset', [0])[0])
    limit = int(request.args.get('count', [30])[0])
    if offset < 0: offset = 0
    if limit < 1: limit = 1
    if limit > 30: limit = 30
    return offset, limit

def createEdge(request, graphName, startNode, endNode):
    graphName = url_unquote(graphName)
    g = _load(request, graphName)
    if g is None:
        return

    start = url_unquote(startNode)
    end = url_unquote(endNode)
    if not (g.has_node(start) and g.has_node(end)):
        return request.respondJson({'message': 'node not in graph'},
                                   NOT_FOUND)

    attrib = request.json()
    attrib['created'] = datetime.utcnow().strftime(DATETIME_FORMAT)

    g.add_edge(start, end, **attrib)
    data = g.edge[start][end]
    data.update({'start': start, 'end': end,
                 'graph': graphName})

    request.respondJson(data, CREATED)

def showEdge(request, graphName, startNode, endNode):
    graphName = url_unquote(graphName)
    g = _load(request, graphName)
    if g is None:
        return

    start = url_unquote(startNode)
    end = url_unquote(endNode)
    try:
        edge = g.edge[start][end]
    except KeyError:
        return request.respondJson(
            {'message': 'nodes not in graph or not linked'},
            NOT_FOUND)

    edge = dict(edge)
    edge.update({'start': start, 'end': end,
                 'graph': graphName})
    request.respondJson(edge)

def deleteEdge(request, graphName, startNode, endNode):
    graphName = url_unquote(graphName)
    g = _load(request, graphName)
    if g is None:
        return

    start = url_unquote(startNode)
    end = url_unquote(endNode)
    try:
        _edge = g.edge[start][end]
    except KeyError:
        return request.respondJson({'message': 'edge not in graph'},
                                   NOT_FOUND)

    g.remove_edge(start, end)
    request.respondJson({'message': 'edge deleted'})

def listEdges(request, graphName, startNode):
    graphName = url_unquote(graphName)
    g = _load(request, graphName)
    if g is None:
        return

    if not g.has_node(startNode):
        return request.respondJson({'message': 'node not in graph'},
                                   NOT_FOUND)

    start = url_unquote(startNode)
    ineighbors = g.neighbors_iter(start)

    iNeighborsEdges = _iterNeigborsEdges(g, start, ineighbors)

    attrib = request.json()
    iNeighborsEdges = _iterFilterEdges(iNeighborsEdges, attrib)

    offset, limit = _getPaging(request)
    iNeighborsEdges = islice(iNeighborsEdges, offset, offset + limit)
    data = {'neighbors': dict(iNeighborsEdges)}
    request.respondJson(data)
