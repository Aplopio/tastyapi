from tastypie.fields import ApiField, CharField, FileField, IntegerField,\
                     FloatField, DecimalField, BooleanField, ListField, DictField,\
                     DateField, DateTimeField, RelatedField as TastypieRelatedField, ToOneField as TastypieToOneField,\
                     ForeignKey as TastypieForeignKey, OneToOneField, ToManyField as TastypieToManyField, ManyToManyField as TastypieManyToManyField,\
                     OneToManyField, TimeField

from uris import ResourceURI
from tastypie.exceptions import ApiFieldError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


class RelatedField(TastypieRelatedField):
    def __init__(self, *args, **kwargs):
        if not 'uri_cls_list' in kwargs:
            uri_cls_list = [basestring, ResourceURI]
            kwargs.update({'uri_cls_list': uri_cls_list})
        TastypieRelatedField.__init__(self, *args, **kwargs)        


class ToOneField(RelatedField, TastypieToOneField):
    def __init__(self, *args, **kwargs):
        RelatedField.__init__(self, *args, **kwargs)


class ForeignKey(ToOneField):
    pass


class ToManyField(RelatedField, TastypieToManyField):
    def __init__(self, *args, **kwargs):
        RelatedField.__init__(self, *args, **kwargs)


class SubResourceField(ToManyField):
    sub_resource_field=True
    
    def __init__(self, *args, **kwargs):
        if not 'related_name' in kwargs:
            raise TypeError('Please specify a related name')
        super(SubResourceField, self).__init__(*args, **kwargs)
        self.readonly = True
        
    def get_related_resource(self, related_instance):
        """
        Instaniates the related resource.
        """
        resource_obj = getattr(self, 'resource_obj')
        resource_pk = getattr(self, 'resource_pk')
        related_resource = self.to_class(api_name=self.api_name, parent_resource=resource_obj, parent_pk=resource_pk)
        

        # Fix the ``api_name`` if it's not present.
        if related_resource._meta.api_name is None:
            if self._resource and not self._resource._meta.api_name is None:
                related_resource._meta.api_name = self._resource._meta.api_name

        # Try to be efficient about DB queries.
        related_resource.instance = related_instance
        return related_resource
