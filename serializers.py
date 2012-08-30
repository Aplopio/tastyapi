from tastypie.serializers import Serializer
from uris import ResourceURI


class RboxSerializer(Serializer):
    formats = ['json', 'jsonp', 'xml', 'yaml', 'html', 'plist', 'rbox']

    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'xml': 'application/xml',
        'yaml': 'text/yaml',
        'html': 'text/html',
        'plist': 'application/x-plist',
        'rbox': 'application/rbox'
    }

    def get_data_class(self, data):
        return data.__class__.__name__.lower()    
    
    def to_simple(self, data, options):
        extra_types = options.get('extra_types', [])
        if isinstance(data, tuple(extra_types)):
            try:
                method = getattr(self, 'to_simple_%s' % self.get_data_class(data))
                return method(data, options)
                
            except AttributeError:
                raise AttributeError('to_simple method for the extra data type was not found')

        return super(RboxSerializer, self).to_simple(data, options)

    def to_simple_resourceuri(self, data, options):
        return data

    def to_rbox(self, data, options=None):
        options = {'extra_types':  [ResourceURI]}
        data = self.to_simple(data, options)
        return data

    def from_rbox(self, content):
        return content
        

        

