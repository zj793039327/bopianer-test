import functools
import json
import logging
from datetime import date, datetime
from django.http import HttpResponse


def fields(request):
    f = request.GET.get('fields')
    if f:
        return f.split(',')
    return []


def ok(data, bid=None, page=None):
    resp = {
        'status': 0,
        'message': 'ok',
        'data': data,
    }
    if page is not None:
        resp['page'] = page
    if bid is not None:
        resp['bid'] = bid

    return HttpResponse(content=json.dumps(resp, cls=APIEncoder),
                        content_type='application/json')


def error(msg, status=1):
    resp = {
        'status': status,
        'message': 'error:' + msg,
    }
    return HttpResponse(content=json.dumps(resp, cls=APIEncoder),
                        content_type='application/json')


def exception(e):
    logger = logging.getLogger('django')
    logger.error("error " + e.message)
    resp = {
        'status': 500,
        'message': 'Unknown exception.',
        'data': e.message
    }
    return HttpResponse(content=json.dumps(resp), status=500,
                        content_type='application/json')


def catch(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            # fixme print log
            print e
            return exception(e)

    return inner


class APIEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, o)
