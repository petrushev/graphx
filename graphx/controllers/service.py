from twisted.internet import reactor

def stop(request):
    request.respondJson({})
    reactor.callLater(1, reactor.stop)
