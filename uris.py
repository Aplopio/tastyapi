from requests import CustomRequestFactory


def mock_get_request(user, _format, **extra):
    qs = "format=%s" % _format
    return CustomRequestFactory().get(user, qs, **extra)


def mock_post_request(user, data, accept_type, **extra):
    return CustomRequestFactory().post(user, data, accept_type, **extra)


def mock_delete_request(user, **extra):
    return CustomRequestFactory().delete(user, **extra)


def mock_put_request(user, data, accept_type, **extra):
    extra.update({'REQUEST_METHOD': 'PUT'})
    return mock_post_request(user, data, accept_type, **extra)


def mock_patch_request(user, data, accept_type, **extra):
    extra.update({'REQUEST_METHOD': 'PATCH'})
    return mock_post_request(user, data, accept_type, **extra)    

    
class ResourceListURI(object):
    def __init__(self, resource, parent_related_name=None, parent_obj_pk=None):
        self.resource = resource
        self.kwargs = {}
        if parent_related_name:
            self.kwargs = {parent_related_name: parent_obj_pk}

    def __getitem__(self, pk):
        return self.resource.get_resource_uri_rbox(obj_pk=pk)        

    def __repr__(self):
        return "<ResourceListURI: for %s>" % self.resource
        
    def get(self, user, _format="rbox", **kwargs):
        request = mock_get_request(user=user, _format=_format)
        kwargs.update(self.kwargs)
        return self.resource.wrap_view('dispatch_list')(request, **kwargs)

    def create(self, user, post_data, accept_type="application/rbox", **kwargs):
        kwargs.update(self.kwargs)
        request = mock_post_request(user=user, post_data=post_data, accept_type=accept_type)
        return self.resource.wrap_view('dispatch_list')(request, **kwargs)

    def delete(self, user, **kwargs):
        kwargs.update(self.kwargs)
        request = mock_delete_request(user=user)
        return self.resource.wrap_view('dispatch_list')(request, **kwargs)

    def update(self, user, data, accept_type="application/rbox", **delete_kwargs):
        delete_kwargs.update(self.kwargs)                
        request = mock_put_request(user=user, data=data, accept_type=accept_type)
        return self.resource.wrap_view('dispatch_list')(request, **delete_kwargs)
        

class ResourceURI(object):
    def __init__(self, resource, pk, **kwargs):
        self.resource = resource
        self.pk = pk

    def __repr__(self):
        return "<ResourceURI: for %s with pk = %s>" % (self.resource, self.pk)
        
    def get(self, user, _format="rbox"):
        request = mock_get_request(user=user, _format=_format)
        kwargs = {'pk': self.pk}
        return self.resource.wrap_view('dispatch_detail')(request, **kwargs)

    def delete(self, user):
        request = mock_delete_request(user=user)
        kwargs = {'pk': self.pk}
        return self.resource.wrap_view('dispatch_detail')(request, **kwargs)

    def update(self, user, data, accept_type="application/rbox", **kwargs):
        request = mock_put_request(user=user, data=data, accept_type=accept_type)
        return self.resource.wrap_view('dispatch_detail')(request, **kwargs)

    def patch(self, user, data, accept_type="application/rbox", **kwargs):
        request = mock_patch_request(user=user, data=data, accept_type=accept_type)
        kwargs.update({'pk': self.pk})
        return self.resource.wrap_view('dispatch_detail')(request, **kwargs)