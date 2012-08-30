from tastypie_resources import Resource as TastypieResource,  ModelResource as TastypieModelResource
from serializers import RboxSerializer
from responses import CustomResponseHandler
from uris import ResourceURI, ResourceListURI
from tastypie.bundle import Bundle
from tastypie.authorization import DjangoAuthorization
import fields
from django.conf.urls.defaults import url

    
class Resource(TastypieResource):
    def __init__(self, api_name=None):
        super(Resource, self).__init__(api_name=None)

    def _handle_500_customrequest(self, request, exception):
        raise exception

    def throttle_check_customrequest(self, request):
        return

    def log_throttled_access_customrequest(self, request):
        return
        
    def prepend_urls(self):
        urls = []

        for name, field in self.fields.items():
            if isinstance(field, fields.ToManyField):
                resource = r"^(?P<resource_name>{resource_name})/(?P<{related_name}>.+)/{related_resource}/$".format(
                    resource_name=self._meta.resource_name,
                    related_name=field.related_name,
                    related_resource=field.attribute,
                )
                resource = url(resource, field.to_class().wrap_view('get_list'), name="api_dispatch_detail")
                urls.append(resource)
        return urls

    def get_resource_uri_rbox(self, request=None, bundle_or_obj=None, obj_pk=None, **kwargs):            
        if obj_pk:
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
                    setattr(resource_uri, "%s" % field.to._meta.resource_name, ResourceListURI(resource=field.to(self._meta.api_name), parent_related_name=field.related_name, parent_obj_pk=obj_pk))                
        return resource_uri

    def get_via_uri_customrequest(self, uri, request):
        return self.obj_get(request=request, **{'pk': uri.pk})        

    class Meta:
        serializer = RboxSerializer()
        response_handler = CustomResponseHandler()
        authorization = DjangoAuthorization()
        always_return_data = True


class ModelResource(Resource, TastypieModelResource):
    pass