from tastypie.resources import Resource as TastypieResource,  ModelResource as TastypieModelResource
from serializers import RboxSerializer
from uris import ResourceURI, ResourceListURI
from tastypie.bundle import Bundle
from tastypie.authorization import DjangoAuthorization
import fields
from django.conf.urls.defaults import url, patterns, include
from django.core.urlresolvers import RegexURLResolver
from django.core.exceptions import ImproperlyConfigured
from tastypie.utils import trailing_slash
from django.http import Http404
class CustomRegexURLResolver(RegexURLResolver):    
    @property
    def url_patterns(self):
        url_patterns = patterns("", *self.urlconf_name)
        try:
            iter(url_patterns)
        except TypeError:
            raise ImproperlyConfigured("The included urlconf %s doesn't have any patterns in it" % self.urlconf_name)
        return url_patterns
    
class Resource(TastypieResource):

    def _handle_500_customrequest(self, request, exception):
        raise exception

    def throttle_check_customrequest(self, request):
        return

    def log_throttled_access_customrequest(self, request):
        return

    def view_to_handle_subresource(self, request, **kwargs):
        sub_resource_field_list = kwargs.pop('%s_sub_resource_field_list'%self._meta.resource_name)
        rest_of_url = kwargs.pop('%s_rest_of_url'%self._meta.resource_name)
        pk = kwargs.pop('pk')
        try:
            parent_obj = self.obj_get(request=request, **{'pk':pk})
        except Exception:
            return self._meta.response_router_obj[request].get_not_found_response()
        
        for field in sub_resource_field_list:
            sub_resource_cls = field.to
            sub_resource_obj = sub_resource_cls(api_name=self._meta.api_name, parent_resource=self, parent_pk=pk)
            sub_resource_obj._meta.queryset = getattr(parent_obj, '%s' % field.attribute).all()
            resolver = CustomRegexURLResolver(r'^', sub_resource_obj.urls)
            try:
                if rest_of_url[-1] != '/':
                    rest_of_url = "%s%s" %(rest_of_url, trailing_slash())
                callback, callback_args, callback_kwargs = resolver.resolve(rest_of_url)
                callback_kwargs.update({'%s_resource_name'%self._meta.resource_name: self._meta.resource_name, '%s_pk'%self._meta.resource_name: pk, 'api_name': self._meta.api_name})
                return callback(request, *callback_args, **callback_kwargs)
            except Http404:
                pass
        return self._meta.response_router_obj[request].get_not_found_response()
        
    def prepend_urls(self):
        sub_resource_field_list = []
        url_list = []
        for name, field in self.fields.items():
            if field.__class__ ==  fields.SubResourceField:
                sub_resource_field_list.append(field)
        if len(sub_resource_field_list) > 0:
            url_list += [
                url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w-]*)/(?P<%s_rest_of_url>.+)"%(self._meta.resource_name,
                                                                                       self._meta.resource_name),
                    self.wrap_view('view_to_handle_subresource'), {'%s_sub_resource_field_list'%(self._meta.resource_name): sub_resource_field_list})
            ]
        
        for name, field in self.fields.items():            
            if field.__class__ ==  fields.SubResourceField:
                include_urls = include(field.to(api_name=self._meta.api_name).urls)

                url_list += [url(r"^(?P<%s_resource_name>%s)/(?P<%s_pk>\w[\w-]*)/"%(self._meta.resource_name, self._meta.resource_name, self._meta.resource_name), include_urls)]
        return url_list        

    def get_resource_uri_rbox(self, request=None, bundle_or_obj=None, obj_pk=None, **kwargs):            
        if obj_pk:
            
            self.wrap_view('api_dispatch_detail')(request, **{'pk': obj_pk})
            resource_uri = ResourceURI(self, obj_pk)
            return self.assign_child_resource_managers_to_uri(resource_uri, obj_pk)

        if not bundle_or_obj:
            return ResourceListURI(self)
        else:
            if isinstance(bundle_or_obj, Bundle):
                obj = bundle_or_obj.obj
            else:
                obj = bundle_or_obj
            resource_uri = ResourceURI(self, obj.pk)
            return self.assign_child_resource_managers_to_uri(resource_uri, obj.pk)

    def assign_child_resource_managers_to_uri(self, resource_uri, obj_pk=None):
        for name, field in self.fields.items():
            if isinstance(field, fields.SubResourceField):
                if obj_pk:
                    ## do something here baby to stop abuse 
                    child_resource = field.to(self._meta.api_name)
                    child_resource._meta.queryset = child_resource._meta.queryset.filter(**{field.related_name: obj_pk})
                    setattr(resource_uri, "%s" % field.to._meta.resource_name, ResourceListURI(resource=child_resource))
        return resource_uri

    def get_via_uri_customrequest(self, uri, request):
        return self.obj_get(request=request, **{'pk': uri.pk})



    class Meta:
        serializer = RboxSerializer()
        authorization = DjangoAuthorization()
        always_return_data = True


class ModelResource(Resource, TastypieModelResource):
    pass