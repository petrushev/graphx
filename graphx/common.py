DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


def _getPaging(request):
    offset = int(request.args.get('offset', [0])[0])
    limit = int(request.args.get('count', [30])[0])
    if offset < 0: offset = 0
    if limit < 1: limit = 1
    if limit > 30: limit = 30
    return offset, limit
