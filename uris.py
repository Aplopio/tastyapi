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
    def __init__(self, resource):
        self.resource = resource

    def __getitem__(self, pk):
        from django.contrib.auth import User
        user = User.objects.createt(user_name="internal_api_user", password="internal_api_user")
        user.is_superuser = True
        request = mock_get_request(user, _format="rbox")
        del user
        return self.resource.get_resource_uri_rbox(request, obj_pk=pk)        

    def __repr__(self):
        return "<ResourceListURI: for %s>" % self.resource
        
    def get(self, user, _format="rbox", **kwargs):
        request = mock_get_request(user=user, _format=_format)
        return self.resource.wrap_view('dispatch_list')(request, **kwargs)

    def create(self, user, data, accept_type="application/rbox", **kwargs):
        request = mock_post_request(user, data, accept_type)
        return self.resource.wrap_view('dispatch_list')(request, **kwargs)

    def delete(self, user, **kwargs):
        request = mock_delete_request(user=user)
        return self.resource.wrap_view('dispatch_list')(request, **kwargs)

    def update(self, user, data, accept_type="application/rbox", **delete_kwargs):
        request = mock_put_request(user, data, accept_type=accept_type)
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
        request = mock_put_request(user, data, accept_type)
        return self.resource.wrap_view('dispatch_detail')(request, **kwargs)

    def patch(self, user, data, accept_type="application/rbox", **kwargs):
        request = mock_patch_request(user, data, accept_type)
        kwargs.update({'pk': self.pk})
        return self.resource.wrap_view('dispatch_detail')(request, **kwargs)


    