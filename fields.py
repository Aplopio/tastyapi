from tastypie.fields import ApiField, CharField, FileField, IntegerField,\
                     FloatField, DecimalField, BooleanField, ListField, DictField,\
                     DateField, DateTimeField, RelatedField as TastypieRelatedField, ToOneField as TastypieToOneField,\
                     ForeignKey as TastypieForeignKey, OneToOneField, ToManyField as TastypieToManyField, ManyToManyField as TastypieManyToManyField,\
                     OneToManyField, TimeField

from uris import ResourceURI


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
        
        