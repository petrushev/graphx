import requests as rq

BASE = 'http://localhost:8070'

gdata = {'name': 'my graph',
         'attributes': {'kind': 'test graph'}}
nodedata = {'my_node': {'ttl': 20},
            'end': {}}
edgedata = {'my_node':
                {'end': {'color': 'red'}}}


def test_index():
    response = rq.get(BASE + '/')
    assert response.status_code == 200, response.status_code
    response = response.json()
    assert response['status'] == 'ready', response

def test_create_graph():
    response = rq.post(BASE + '/graphs',
                       json=gdata)
    assert response.status_code == 201, response.status_code
    response = response.json()
    assert response['name'] == gdata['name'], response

    gdata['created'] = response['created']
    for k, v in gdata['attributes'].items():
        assert k in response, response.keys()
        assert response[k] == v, response

def test_create_dupl_graph():
    response = rq.post(BASE + '/graphs',
                       json=gdata)
    assert response.status_code == 409, response.status_code

def test_get_graph():
    response = rq.get(BASE + '/graphs/' + gdata['name'])
    assert response.status_code == 200, response.status_code
    response = response.json()
    assert response['name'] == gdata['name'], response
    assert 'created' in response, response.keys()
    assert response['created'] == gdata['created'], response

def test_create_node():
    nodeName, nodeData = nodedata.items()[0]
    payload = {'nodeName': nodeName, 'attributes': nodeData}
    response = rq.post(BASE + '/graphs/' + gdata['name'] + '/nodes',
                       json=payload)
    assert response.status_code == 201, response.status_code

    response = response.json()
    assert response['graph'] == gdata['name'], response
    assert response['name'] == nodeName, response

    assert 'ttl' in response, response.keys()
    assert response['ttl'] == 20, response

    nodeData['created'] = response['created']

def test_create_dupl_node():
    nodeName, nodeData = nodedata.items()[0]
    payload = {'nodeName': nodeName, 'attributes': nodeData}
    response = rq.post(BASE + '/graphs/' + gdata['name'] + '/nodes',
                       json=payload)
    assert response.status_code == 409, response.status_code

def test_get_node():
    nodeName, nodeData = nodedata.items()[0]
    response = rq.get(BASE + '/graphs/' + gdata['name'] + '/nodes/' + nodeName)
    assert response.status_code == 200, response.status_code

    response = response.json()
    assert response['graph'] == gdata['name'], response
    assert response['name'] == nodeName, response

    for k, v in nodeData.items():
        assert k in response, (k, response.keys())
        assert response[k] == v, (k, response)

def test_graph_list():
    response = rq.get(BASE + '/graphs')
    assert response.status_code == 200, response.status_code
    response = response.json()
    assert 'names' in response
    assert gdata['name'] in response['names']

    response = rq.get(BASE + '/graphs?offset=200')
    response = response.json()
    assert len(response['names']) == 0

def test_add_edge():
    start, end = nodedata.keys()[:2]
    response = rq.post(BASE + '/graphs/' + gdata['name'] + '/nodes',
                       json={'nodeName': end})
    assert response.status_code == 201, response.status_code

    edge = edgedata[start][end]
    response = rq.post(BASE + '/graphs/{0}/edges/{1}/{2}'.format(gdata['name'], start, end),
                       json=edge)
    assert response.status_code == 201, (response.status_code, response.json())
    response = response.json()

    for k, v in edge.items():
        assert k in response, (k, v, response.keys())
        assert response[k] == v, response

def test_node_list():
    url = BASE + '/graphs/' + gdata['name'] + '/nodes'
    response = rq.get(url, json={})
    assert response.status_code == 200, response.status_code
    response = response.json()
    assert 'names' in response
    assert len(response['names']) == 2
    assert nodedata.keys()[0] in response['names']

    response = rq.get(url + '?offset=1', json={})
    response = response.json()
    assert len(response['names']) == 1

    filters = nodedata.values()[0]
    assert len(filters) > 0
    response = rq.get(url, json=filters).json()
    assert len(response) == 1

def test_delete_node_forbidden():
    nodeName = nodedata.keys()[0]
    response = rq.delete(BASE + '/graphs/' + gdata['name'] + '/nodes/' + nodeName)
    assert response.status_code == 409, response.status_code

def test_list_edges():
    start, end = nodedata.keys()[:2]
    url = BASE + '/graphs/' + gdata['name'] + '/edges/' + start
    response = rq.get(url)
    assert response.status_code == 200, response.status_code
    response = response.json()
    assert 'neighbors' in response
    assert len(response['neighbors']) == 1
    assert end in response['neighbors']

    response = rq.get(url + '?offset=2')
    response = response.json()
    assert len(response['neighbors']) == 0

def test_show_single_edge():
    start, end = nodedata.keys()[:2]
    url = BASE + '/graphs/{0}/edges/{1}/{2}'.format(gdata['name'], start, end)
    response = rq.get(url).json()

    for k, v in edgedata[start][end].items():
        assert k in response
        assert response[k] == v

def test_delete_edge():
    start, end = nodedata.keys()[:2]
    url = BASE + '/graphs/{0}/edges/{1}/{2}'.format(gdata['name'], start, end)
    response = rq.delete(url)
    assert response.status_code == 200, response.status_code
    response = rq.get(url)
    assert response.status_code == 404, response.status_code

def test_delete_node():
    nodeName = nodedata.keys()[0]
    response = rq.delete(BASE + '/graphs/' + gdata['name'] + '/nodes/' + nodeName)
    assert response.status_code == 200, response.status_code
    response = rq.get(BASE + '/graphs/' + gdata['name'] + '/nodes/' + nodeName)
    assert response.status_code == 404, response.status_code

def test_delete_graph():
    response = rq.delete(BASE + '/graphs/' + gdata['name'])
    assert response.status_code == 409, response.status_code

    response = rq.get(BASE + '/graphs/' + gdata['name'])
    assert response.status_code == 200, response.status_code

    response = rq.delete(BASE + '/graphs/' + gdata['name'],
                         json={'force': True})
    assert response.status_code == 200, response.status_code

    response = rq.get(BASE + '/graphs/' + gdata['name'])
    assert response.status_code == 404, response.status_code

def tearDown():
    rq.delete(BASE + '/graphs/' + gdata['name'],
                         json={'force': True})
