from django.db.models import ForeignKey, NOT_PROVIDED
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


def property_field(cls, name, related_class=None, default=None):
    def get_key(self):
        key_field = getattr(self, 'key_field', 'user_id')
        key = getattr(self, key_field, '-')
        return key

    def get_instance(self):
        key = get_key(self)
        kwargs = {}
        if related_class is not None:
            kwargs['related_class'] = related_class
        if default is not None:
            kwargs['default'] = default
        return cls(name, key, **kwargs)

    def getter(self):
        return get_instance(self)

    def setter(self, value):
        if isinstance(value, cls):
            return value
        instance = get_instance(self)
        return instance.set(value)

    return property(getter, setter)


class InMemoryFieldMixin(object):
    def contribute_to_class(self, cls, name, *args, **kwargs):
        self.set_attributes_from_name(name)
        self.model = cls
        self.opts = cls._meta

        class_key = getattr(cls, 'class_key', None)
        field_keys = []
        if class_key is None:
            field_keys.append(cls._meta.db_table)
        elif class_key:
            field_keys.append(class_key)
        field_keys.append(self.name)

        field_key = '_'.join(field_keys)

        if NOT_PROVIDED == self.default:
            default = None
        else:
            default = self.default

        setattr(cls, self.name, property_field(self._class, field_key, related_class=cls, default=default))
