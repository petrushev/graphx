import requests as rq

BASE = 'http://localhost:8070'

data = {'dag':
           {'a':
             {'b': {'color': 'red', 'size': '5'},
              'd': {'color': 'red', 'size': '10'}},
           'b':
             {'c': {'color': 'blue', 'size': '1'},
              'e': {'color': 'green', 'size': '5'},
              'f': {'color': 'black', 'size': '2'}},
           'e':
             {'h': {'color': 'yellow', 'size': '2'}},
           'd':
             {'h': {'color': 'red', 'size': '2'}}},
         'cycled':
           {'a':
              {'b': {},
               'c': {}},
            'b':
              {'d': {}},
            'd':
              {'a': {}},
               'e': {}}}


def setUp():
    for gname, gdata in data.items():
        inserted = set()
        rq.post('{0}/graphs'.format(BASE),
                json={'name': gname})
        for start, nodedata in gdata.items():
            for end, edgedata in nodedata.items():
                if start not in inserted:
                    rq.post('{0}/graphs/{1}/nodes'.format(BASE, gname),
                            json={'nodeName': start})
                    inserted.add(start)
                if end not in inserted:
                    rq.post('{0}/graphs/{1}/nodes'.format(BASE, gname),
                            json={'nodeName': end})
                    inserted.add(end)

                rq.post('{0}/graphs/{1}/edges/{2}/{3}'.format(BASE, gname, start, end),
                        json=edgedata)

def test_path():
    r = rq.get('{0}/graphs/{1}/paths/simple/{2}/{3}'.format(BASE, 'dag', 'a', 'h'))
    response = r.json()
    assert response['paths'][0] == 'a,d,h'.split(',')
    assert len(response['paths']) == 2, response['paths']

def test_query_edges():
    r = rq.get('{0}/graphs/{1}/edges/{2}'.format(BASE, 'dag', 'b'),
               json={'color': 'blue'}).json()
    assert r['neighbors'].keys() == ['c']

def test_cycles():
    r = rq.get('{0}/graphs/{1}/paths/cycles'.format(BASE, 'cycled')).json()
    assert 'cycles' in r
    assert ['a', 'b', 'd'] in r['cycles']

def test_topsort():
    r = rq.get('{0}/graphs/{1}/topologicalsort'.format(BASE, 'dag')).json()
    assert r['nodes'] == ["a", "b", "c", "e", "f", "d", "h"]
    r = rq.get('{0}/graphs/{1}/topologicalsort'.format(BASE, 'cycled'))
    assert r.status_code == 404

def test_longestpath():
    r = rq.get('{0}/graphs/{1}/paths/longest'.format(BASE, 'dag')).json()
    assert r['longestPath'] == ["a", "b", "e", "h"]
    r = rq.get('{0}/graphs/{1}/paths/longest'.format(BASE, 'cycled'))
    assert r.status_code == 404

def tearDown():
    for gname in data:
        rq.delete('{0}/graphs/{1}'.format(BASE, gname),
                  json={'force': True})
