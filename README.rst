Graphx
======

A thin rest api over networkx, can serve as a graph database.


Graphs
------

* POST ``/graphs``

    Create a new graph

    body:

      - name
      - attributes: dictionary, default: empty

    returns:

      - graph
          - name
          - created: timestamp
          - attributes: dictionary

* GET ``/graphs/<name>``

    Retrieve graph

    returns:

      - names: list of graph names

* DELETE ``/graphs/<name>``

    Delete graph

    body:

      - force: boolean, default: none, use to delete non-empty graph

* GET ``/graphs``

    List graphs

    url parameters:

      - offset
      - count

    returns:

       - list of graphs


Nodes
-----

* POST ``/graphs/<graph>/nodes``

    Create a new node on a specific graph

    body:

      - nodeName
      - attributes: dictionary, default: empty

    returns:

      - node
          - name
          - graph
          - created
          - attributes: dictionary

* GET ``/graphs/<graph>/nodes/<nodeName>``

    Retrieve node

    returns:

      - node

* DELETE ``/graphs/<graph>/nodes/<nodeName>``

    Delete node

* GET ``/graphs/<graph>/nodes``

    List nodes, optional filtering

    url parameters:

      - offset
      - count

    body:

      - dictionary of filter attributes

    returns:

      - list of nodes


Edges
-----

* POST ``/graphs/<graph>/edges/<start>/<end>``

    Create edge between two specific nodes

    body:

      - attributes: dictionary, default: empty

    returns:

      - edge:
          - graph
          - start: name of start node
          - end: name of end node
          - created
          - attributes: dictionary

* GET ``/graphs/<graph>/edges/<start>/<end>``

    Retrieve edge

    returns:

      - edge

* DELETE ``/graphs/<graph>/edges/<start>/<end>``

    Delete edge

* GET ``/graphs/<graph>/edges/<start>``

    List edges linked to a specific node

    url parameters:

      - offset
      - count

    body:

      - dictionary of filter attributes

    returns:

      - dictionary:

          - key: name of end node
          - value: attributes of edge


Persistence
-----------

All graphs are loaded into memory and persisted in GraphML format periodically
and on server shutdown.


Requirements
------------

See ``requirements.txt``.


Configuration and deployment
----------------------------

The following environment variables can be set:

  * ``GRAPHX_PERSIST_PATH`` : location where the graphs will be persisted, default: current dir

  * ``GRAPHX_PERSIST_INTERVAL`` : interval for periodic persistance, default: 30 seconds

  * ``GRAPHX_BIND_ADDRESS`` : bind address for the server, default: localhost

  * ``GRAPHX_PORT`` : port for the server, default: 8070


Run: ::

    twistd -y graphservice.py
