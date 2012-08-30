from tastypie.api import Api
from django.core.exceptions import ImproperlyConfigured
from uris import ResourceListURI


class RboxApi(Api):
    def __init__(self, api_name="v1"):
        self._rbox_registry = {}
        super(RboxApi, self).__init__(api_name="v1")

    def handle_add_resource(self, resource):    
        resource_name = getattr(resource._meta, 'resource_name', None)

        if resource_name is None:
            raise ImproperlyConfigured("Resource %r must define a 'resource_name'." % resource)

        self._rbox_registry[resource_name] = resource
        
        setattr(self, resource_name, ResourceListURI(resource))
        
    def register(self, resource, register_to_tastypie=True, canonical=True):
        """
        Registers an instance of ``Resource`` to the Api

        Optionally registers to tastypie if the argument
        ``register_to_tastypie``  is ``True``.
        """
        if register_to_tastypie:
            super(RboxApi, self).register(resource, canonical=True)

        self.handle_add_resource(resource)

    def handle_del_resource(self, resource_name):
        if resource_name in self._rbox_registry:
            del (self._rbox_registry[resource_name])

        resource_manager = getattr(self, resource_name)
        del resource_manager

    def unregister(self, resource_name, only_from_tastypie=False):        
        """
        If present, unregisters a resource from the API.
        """
        
        if not only_from_tastypie:
            self.handle_del_resource(resource_name)
            
        super(RboxApi, self).unregister(resource_name)
