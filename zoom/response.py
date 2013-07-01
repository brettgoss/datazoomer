"""HTTP responses for various common responses.
"""
__all__ = ['Response','HTMLResponse','PNGResponse','XMLResponse','TextResponse','JavascriptResponse', 'RedirectResponse','FileResponse']

def render_headers(headers):
    return (''.join(["%s: %s\n" % (header, value) for header, value in headers.items()]))

class Response:
    def __init__(self,content):
        self.status = '200 OK'
        self.headers = {}
        self.content = content
    def render_doc(self):
        return self.content
    def render(self):
        doc = self.render_doc()
        length_entry = [('Content-length', '%s' % len(doc))]
        return render_headers(dict(self.headers.items() + length_entry)) + '\n' + doc
    def render_wsgi(self):
        doc = self.render_doc()
        length_entry = [('Content-length', '%s' % len(doc))]
        return self.status, self.headers.items() + length_entry, doc

class PNGResponse(Response):
    def __init__(self, content):
        Response.__init__(self, content)
        self.headers['Content-type']  = 'image/png'

class HTMLResponse(Response):
    """
    Render an HTML response.

    >>> import response
    >>> response.HTMLResponse('test123').render()
    'X-FRAME-OPTIONS: DENY\\nContent-type: text/html\\nContent-length: 7\\nCache-Control: no-cache\\n\\ntest123'

    >>> response.HTMLResponse('test123').render_wsgi()
    ('200 OK', [('X-FRAME-OPTIONS', 'DENY'), ('Content-type', 'text/html'), ('Cache-Control', 'no-cache'), ('Content-length', '7')], 'test123')

    """
    def __init__(self, content='', printed_output=''):
        Response.__init__(self, content)
        self.printed_output = printed_output
        self.headers['Content-type']  = 'text/html'
        self.headers['Cache-Control'] = 'no-cache'
        self.headers['X-FRAME-OPTIONS'] = 'DENY'
    def render_doc(self):
        t = self.content.replace('{*PRINTED*}',self.printed_output)
        doc = t.encode('utf-8')
        return doc

class XMLResponse(Response):
    def __init__(self, content=''):
        Response.__init__(self, content)
        self.headers['Content-type']  = 'text/xml'
        self.headers['Cache-Control'] = 'no-cache'
    def render_doc(self):
        doc = '<?xml version="1.0"?>%s' % self.content
        return doc

class TextResponse(Response):
    def __init__(self,content=''):
        Response.__init__(self,content)
        self.headers['Content-type']  = 'text'
        self.headers['Cache-Control'] = 'no-cache'
    def render_doc(self):
        doc = '%s' % self.content
        return doc

class JavascriptResponse(TextResponse):
    def __init__(self, content):
        TextResponse.__init__(self, content)
        self.headers['Content-type'] = 'application/javascript'

class RedirectResponse(Response):
    def __init__(self,url):
        Response.__init__(self,'')
        self.headers['Location']  = url

class FileResponse(Response):
    def __init__(self,filename,content=None):
        Response.__init__(self,'')
        if content:
            self.content = content
        else:            
            self.content = file(filename,'rb').read()
        import os
        (path,fileonly) = os.path.split(filename)
        self.headers['Content-type']  = 'application/octet-stream'
        self.headers['Content-Disposition'] = 'attachment; filename="%s"' % fileonly
        self.headers['Cache-Control'] = 'no-cache'


if __name__=='__main__':
    import doctest
    doctest.testmod()