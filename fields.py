from tastypie.fields import ApiField, CharField, FileField, IntegerField,\
                     FloatField, DecimalField, BooleanField, ListField, DictField,\
                     DateField, DateTimeField, RelatedField as TastypieRelatedField, ToOneField as TastypieToOneField,\
                     ForeignKey as TastypieForeignKey, OneToOneField, ToManyField as TastypieToManyField, ManyToManyField as TastypieManyToManyField,\
                     OneToManyField, TimeField, SubResourceField as TastypieSubResourceField
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


class SubResourceField(ToManyField, TastypieSubResourceField):    
    def __init__(self, *args, **kwargs):
        if not 'related_name' in kwargs:
            raise TypeError('Please specify a related name')
        super(SubResourceField, self).__init__(*args, **kwargs)
        self.readonly = True
        
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

        m2m_dehydrated = {}

        # TODO: Also model-specific and leaky. Relies on there being a
        #       ``Manager`` there.
        m2m_resource = self.get_related_resource(bundle)
        m2m_dehydrated.update({'resource_uri': m2m_resource.get_resource_uri()})
        m2m_dehydrated.update({'count': the_m2ms.all().count()})
        return m2m_dehydrated