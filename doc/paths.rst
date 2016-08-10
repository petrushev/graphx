API Documentation: Paths
========================

* GET ``/graphs/<name>/paths/simple/<start>/<end>``

    Retrieve simple paths from start to end

    returns:

      - paths: path is list of node names, includes start and end

* GET ``/graphs/<name>/paths/cycles``

    Retrieve all cycles in the graphs, if any.

    returns:

      - cycles: path is list of node names, every path is a cycle

* GET ``/graphs/<name>/paths/longes``

    Retrive the longes path in the graph.
    Needs to be acyclic graph

    returns:

      - longestPath: list of node names

* GET ``/graphs/<name>/topologicalsort``

    Topological sort of graph.
    Needs to be acyclic graph

    returns:

      - nodes: list of node names

* GET ``/graphs/<name>/paths/query``

    Query for a path matching certain conditions

    body:

      - nodeAttributes: list of dictionaries with name and attribute filters
      - edgeAttributes: list of dictionaries with edge attribute filters

    returns:

      - paths: path is list of node names
