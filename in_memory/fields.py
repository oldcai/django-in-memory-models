from django.db.models import ForeignKey
from django.db.models.fields.related import lazy_related_operation
from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor


class ReverseInMemoryOneToOneDescriptor(ReverseOneToOneDescriptor):
    """
    The descriptor that handles the object creation for an AutoOneToOneField.
    """

    def __get__(self, instance, instance_type=None):
        model = getattr(self.related, 'related_model', self.related.model)
        related_pk = instance._get_pk_val()
        try:
            rel_obj = getattr(instance, self.cache_name)
        except AttributeError:
            func_name = 'get_by_%s' % self.related.field.name
            func = getattr(model, func_name)
            rel_obj = func(related_pk)
            setattr(instance, self.cache_name, rel_obj)

        return rel_obj


class InMemoryOneToOneKey(ForeignKey):
    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), ReverseInMemoryOneToOneDescriptor(related))

    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        self.set_attributes_from_name(name)
        self.model = cls
        self.opts = cls._meta

        if not cls._meta.abstract:
            def resolve_related_class(model, related, field):
                field.remote_field.model = related
                field.do_related_class(related, model)

            lazy_related_operation(resolve_related_class, cls, self.remote_field.model, field=self)
        setattr(cls, self.name, self.forward_related_accessor_class(self))


def property_field(cls, name):
    def getter(self):
        key_field = getattr(self, 'key_field', 'user_id')
        key = getattr(self, key_field, '-')
        return cls(name, key)

    return property(getter, lambda s, x: x)


class InMemoryFieldMixin(object):
    def contribute_to_class(self, cls, name, *args, **kwargs):
        self.set_attributes_from_name(name)
        self.model = cls
        self.opts = cls._meta

        setattr(cls, self.name, property_field(self._class, name))
