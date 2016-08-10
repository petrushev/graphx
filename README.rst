Graphx
======

A thin rest api over networkx, can serve as a graph database.


API documentation
-----------------

* `Graphs, nodes, edges <doc/api.rst>`_
* `Paths <doc/paths.rst>`_


Persistence
-----------

All graphs are loaded into memory and persisted in compressed binary pickles.
This is done periodically and on server shutdown.


Requirements
------------

See `requirements.txt <requirements.txt>`_


Configuration and deployment
----------------------------

The following environment variables can be set:

  * ``GRAPHX_PERSIST_PATH`` : location where the graphs will be persisted, default: current dir

  * ``GRAPHX_PERSIST_INTERVAL`` : interval for periodic persistance, default: 30 seconds

  * ``GRAPHX_BIND_ADDRESS`` : bind address for the server, default: localhost

  * ``GRAPHX_PORT`` : port for the server, default: 8070


Run: ::

    twistd -y graphservice.py
