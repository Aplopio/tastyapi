from tastypie.resources import Resource as TastypieResource,  ModelResource as TastypieModelResource
from serializers import RboxSerializer
from uris import ResourceURI, ResourceListURI
from tastypie.bundle import Bundle
from tastypie.authorization import DjangoAuthorization
import fields
    
class Resource(TastypieResource):

    def _handle_500_customrequest(self, request, exception):
        raise exception

    def throttle_check_customrequest(self, request):
        return

    def log_throttled_access_customrequest(self, request):
        return

       
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