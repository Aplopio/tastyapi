from tastypie.fields import ApiField, CharField, FileField, IntegerField,\
                     FloatField, DecimalField, BooleanField, ListField, DictField,\
                     DateField, DateTimeField, RelatedField as TastypieRelatedField, ToOneField as TastypieToOneField,\
                     ForeignKey as TastypieForeignKey, OneToOneField, ToManyField as TastypieToManyField, ManyToManyField as TastypieManyToManyField,\
                     OneToManyField, TimeField
from tastypie.bundle import Bundle
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
    
    def __init__(self, *args, **kwargs):
        if not 'related_name' in kwargs:
            raise TypeError('Please specify a related name')
        super(SubResourceField, self).__init__(*args, **kwargs)
        self.readonly = True
        
    def get_related_resource(self, related_instance, bundle):
        """
        Instaniates the related resource.
        """
        resource_obj = getattr(self, 'resource_obj')
        resource_pk = bundle.obj.pk
        related_resource = self.to_class(api_name=self.api_name, parent_resource=resource_obj, parent_pk=resource_pk)
        

        # Fix the ``api_name`` if it's not present.
        if related_resource._meta.api_name is None:
            if self._resource and not self._resource._meta.api_name is None:
                related_resource._meta.api_name = self._resource._meta.api_name

        # Try to be efficient about DB queries.
        related_resource.instance = related_instance
        return related_resource

    def dehydrate(self, bundle):
        if not bundle.obj or not bundle.obj.pk:
            if not self.null:
                raise ApiFieldError("The model '%r' does not have a primary key and can not be used in a ToMany context." % bundle.obj)

            return []

        the_m2ms = None
        previous_obj = bundle.obj
        attr = self.attribute

        if isinstance(self.attribute, basestring):
            attrs = self.attribute.split('__')
            the_m2ms = bundle.obj

            for attr in attrs:
                previous_obj = the_m2ms
                try:
                    the_m2ms = getattr(the_m2ms, attr, None)
                except ObjectDoesNotExist:
                    the_m2ms = None

                if not the_m2ms:
                    break

        elif callable(self.attribute):
            the_m2ms = self.attribute(bundle)

        if not the_m2ms:
            if not self.null:
                raise ApiFieldError("The model '%r' has an empty attribute '%s' and doesn't allow a null value." % (previous_obj, attr))

            return []

        self.m2m_resources = []
        m2m_dehydrated = []

        # TODO: Also model-specific and leaky. Relies on there being a
        #       ``Manager`` there.
        for m2m in the_m2ms.all():
            m2m_resource = self.get_related_resource(m2m, bundle)
            m2m_bundle = Bundle(obj=m2m, request=bundle.request)
            self.m2m_resources.append(m2m_resource)
            m2m_dehydrated.append(self.dehydrate_related(m2m_bundle, m2m_resource))

        return m2m_dehydrated

