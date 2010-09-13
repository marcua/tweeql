"""
A very simple WSGI interface to the module
"""

from Weather import *
from urllib import unquote
from datetime import datetime
import os

titler = lambda x: ' '.join(map(lambda y: y.title(), x.split('_')))


def html(station):
    """
    Yields HTML source for given station
    """
    yield '<html><head><title>%s</title></head><body>'%station
    yield '<table><tr><td><h2>%s</h2><p><b>%s</b></p></td>'%\
        (station,station.data.get('weather',''))
    yield '<td><img src="%s"></td></tr>'%station.icon()
    yield '<tr><td><p>Currently: %s  -  '%\
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    yield 'Time of observation: %s</p></td></tr>'%station.datetime()
    yield '</table><hr><table><tr><th><h3>URLs</h3></th><th><h3>Metrics</h3></th><th><h3>Info</h3></th></tr>'
    urls,metrics,info = [],[],[]
    for k,v in station.items():
        if not v: continue
        k = titler(k)
        tr = '<tr><th align="right">%s</th><td>%s</td></tr>'
        if type(v) == type(0.):
            metrics.append(tr%(k,'%.3f'%v))
        elif v.startswith('http'):
            urls.append(tr%(k,'<a href="%s">%s</a>'%(v,filter(None,v.split('/'))[-1])))
        else:
            info.append(tr%(k,v))
    r = ['<td valign="top"><table>%s</table></td>'%''.join(locals()[x]) \
          for x in ('urls','metrics','info')]
    yield '<tr>%s</tr></table>'%''.join(r)
    yield '</body></html>'


def detail(environ, response):
    response('200 OK', [('Content-type','text/html')])
    return html(Station(environ['QUERY_STRING']))

def zip(environ, response):
    response('200 OK', [('Content-type','text/html')])
    return html(zip2station(environ['QUERY_STRING']))

def location(environ, response):
    response('200 OK', [('Content-type','text/html')])
    return html(location2station(unquote(environ['QUERY_STRING'])))

def list(environ, response):
    response('200 OK', [('Content-type','text/html')])
    yield '<ul>'
    for station in stations():
        yield '<li><a href="detail?%s">%s</a></li>'%(station,station)
    yield '</ul>'

def dispatch(environ, response):
    return eval(environ['PATH_INFO'][1:])(environ, response)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    print "Serving HTTP on port 8000..."
    make_server('', 8000, dispatch).serve_forever()

