from django.test.client import RequestFactory
from django import http
from django.utils import datastructures
import warnings
import sys
import re
BOUNDARY = 'BoUnDaRyStRiNg'
MULTIPART_CONTENT = 'multipart/form-data; boundary=%s' % BOUNDARY
CONTENT_TYPE_RE = re.compile('.*; charset=([\w\d-]+);?')
from response_dispatcher import CustomResponseDispatcher


class UnreadablePostError(IOError):
    pass
        

class BaseRequest(object):
    """equivalent to HttpRequest"""
    _encoding = None
    
    def __init__(self):
        self.GET, self.POST, self.META
        self.method = None
        self._post_parse_error = False
        self._read_started = False
    
    @property
    def body(self):
        if not hasattr(self, '_body'):
            if self._read_started:
                raise Exception("You cannot access body after reading from request's data stream")
            try:
                self._body = self.read()
            except IOError, e:
                raise UnreadablePostError, e, sys.exc_traceback
        return self._body

    @property
    def raw_post_data(self):
        warnings.warn('HttpRequest.raw_post_data has been deprecated. Use HttpRequest.body instead.', PendingDeprecationWarning)
        return self.body

    def _mark_post_parse_error(self):
        self._post = {}
        self._post_parse_error = True

    def _load_post_and_files(self):
        # Populates self._post only no self._files here
        if not hasattr(self, '_post'):
            self._post = self.environ['post_data']
            self._files = None

    def read(self, *args, **kwargs):
        self._read_started = True
        return self._post 
 

class CustomRequest(BaseRequest):
    """Equivalent to WSGIRequest """
    def __init__(self, environ):
        self.environ = environ
        self.META = environ
        self.method = environ['REQUEST_METHOD'].upper()
        self.user = environ['USER']        
        self._post = self.environ.get('post_data')
        self._read_started = False
        self._files = None

    def _get_request(self):
        if not hasattr(self, '_request'):
            self._request = datastructures.MergeDict(self.POST, self.GET)
        return self._request

    def _get_get(self):
        if not hasattr(self, '_get'):
            # The WSGI spec says 'QUERY_STRING' may be absent.
            self._get = http.QueryDict(self.environ.get('QUERY_STRING', ''), encoding=self._encoding)
        return self._get

    def _set_get(self, get):
        self._get = get

    def _get_post(self):
        if not hasattr(self, '_post'):
            self._load_post_and_files()
        return self._post

    def _set_post(self, post):
        self._post = post

    GET = property(_get_get, _set_get)
    POST = property(_get_post, _set_post)
    REQUEST = property(_get_request)


class CustomRequestFactory(RequestFactory):
    def _base_environ(self, **request):
        """
        The base environment for a request.
        """
        # This is a minimal valid WSGI environ dictionary, plus:
        # - HTTP_COOKIE: for cookie support,
        # - REMOTE_ADDR: often useful, see #8551.
        # See http://www.python.org/dev/peps/pep-3333/#environ-variables
        environ = {
            'HTTP_COOKIE':       self.cookies.output(header='', sep='; '),
            'USER':              None,
            'PATH_INFO':         '/',
            'REMOTE_ADDR':       '127.0.0.1',
            'REQUEST_METHOD':    'GET',
            'SCRIPT_NAME':       '',
            'SERVER_NAME':       'testserver',
            'SERVER_PORT':       '80',
            
        }
        environ.update(self.defaults)
        environ.update(request)
        return environ            
        
    def get(self, user, qs, **extra):
        "Construct a GET request."

        r = {
            'QUERY_STRING':    qs,
            'REQUEST_METHOD': 'GET',
            'USER': user,

        }
        r.update(extra)
        return self.request(**r)

    def post(self, user, data, accept_type, content_type=MULTIPART_CONTENT, **extra):
        "Construct a POST request."

        ##fuck still something to do with http exists
        ##http_accept
        
        r = {
            'CONTENT_LENGTH': len(data),
            'REQUEST_METHOD': 'POST',
            'post_data':      data,
            'USER':           user,
            'HTTP_ACCEPT':    accept_type
        }
        r.update(extra)
        return self.request(**r)    

    def delete(self, user, **extra):
        "Construct a DELETE request."

        r = {
            'REQUEST_METHOD': 'DELETE',
            'USER': user
        }
        r.update(extra)
        return self.request(**r)                                              

    def request(self, **request):
        return CustomRequest(self._base_environ(**request))


from tastypie import response_router_obj
response_router_obj[CustomRequest] = CustomResponseDispatcher()
