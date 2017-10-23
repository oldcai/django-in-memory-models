from django.db.models import Model, DEFERRED, FieldDoesNotExist
from django.db.models.base import ModelState
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.db.models.signals import pre_init, post_init


class InMemoryModel(Model):

    class Meta:
        abstract = True
        managed = False

    def __init__(self, *args, **kwargs):
        # Alias some things as locals to avoid repeat global lookups
        cls = self.__class__
        opts = self._meta
        _setattr = setattr
        _DEFERRED = DEFERRED

        pre_init.send(sender=cls, args=args, kwargs=kwargs)

        # Set up the storage for instance state
        self._state = ModelState()

        # There is a rather weird disparity here; if kwargs, it's set, then args
        # overrides it. It should be one or the other; don't duplicate the work
        # The reason for the kwargs check is that standard iterator passes in by
        # args, and instantiation for iteration is 33% faster.
        if len(args) > len(opts.concrete_fields):
            # Daft, but matches old exception sans the err msg.
            raise IndexError("Number of args exceeds number of fields")

        if not kwargs:
            fields_iter = iter(opts.concrete_fields)
            # The ordering of the zip calls matter - zip throws StopIteration
            # when an iter throws it. So if the first iter throws it, the second
            # is *not* consumed. We rely on this, so don't change the order
            # without changing the logic.
            for val, field in zip(args, fields_iter):
                if val is _DEFERRED:
                    continue
                _setattr(self, field.attname, val)
        else:
            # Slower, kwargs-ready version.
            fields_iter = iter(opts.fields)
            for val, field in zip(args, fields_iter):
                if val is _DEFERRED:
                    continue
                _setattr(self, field.attname, val)
                kwargs.pop(field.name, None)

        # Now we're left with the unprocessed fields that *must* come from
        # keywords, or default.

        for field in fields_iter:
            is_related_object = False
            # Virtual field
            if field.attname not in kwargs and field.column is None:
                continue
            if kwargs:
                if isinstance(field.remote_field, ForeignObjectRel):
                    try:
                        # Assume object instance was passed in.
                        rel_obj = kwargs.pop(field.name)
                        is_related_object = True
                    except KeyError:
                        try:
                            # Object instance wasn't passed in -- must be an ID.
                            val = kwargs.pop(field.attname)
                        except KeyError:
                            val = field.get_default()
                    else:
                        # Object instance was passed in. Special case: You can
                        # pass in "None" for related objects if it's allowed.
                        if rel_obj is None and field.null:
                            val = None
                else:
                    try:
                        val = kwargs.pop(field.attname)
                    except KeyError:
                        # This is done with an exception rather than the
                        # default argument on pop because we don't want
                        # get_default() to be evaluated, and then not used.
                        # Refs #12057.
                        val = field.get_default()
            else:
                val = field.get_default()

            if is_related_object:
                # If we are passed a related instance, set it using the
                # field.name instead of field.attname (e.g. "user" instead of
                # "user_id") so that the object gets properly cached (and type
                # checked) by the RelatedObjectDescriptor.
                if rel_obj is not _DEFERRED:
                    _setattr(self, field.name, rel_obj)
            else:
                if val is not _DEFERRED:
                    _setattr(self, field.attname, val)

        if kwargs:
            property_names = opts._property_names
            for prop in tuple(kwargs):
                try:
                    # Any remaining kwargs must correspond to properties or
                    # virtual fields.
                    if prop in property_names or opts.get_field(prop):
                        if kwargs[prop] is not _DEFERRED:
                            _setattr(self, prop, kwargs[prop])
                        del kwargs[prop]
                except (AttributeError, FieldDoesNotExist):
                    pass
            if kwargs:
                for key, value in kwargs.items():
                    if hasattr(self, key):
                        raise TypeError("'%s' is an invalid keyword argument for this function" % key)

                    setattr(self, key, value)
        super(Model, self).__init__()
        post_init.send(sender=cls, instance=self)


class Sorter(object):
    def __init__(self, name, key, related_class, default=None):
        self.name = name
        self.key = key
        self.default = default
        self.sorted_class = related_class
        super(Sorter, self).__init__()

    def __iadd__(self, other):
        if isinstance(other, (int, float)):
            self.increase(int(other))
        return self

    def __isub__(self, other):
        if isinstance(other, (int, float)):
            self.increase(-int(other))
        return self

    def __bool__(self):
        return bool(self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def top(self, count):
        top_ids = self.top_ids(count)
        sorted_class_key = getattr(self.sorted_class, 'key_field', 'user_id')
        return [self.sorted_class(**{sorted_class_key: top_id}) for top_id in top_ids]

    @property
    def rank(self):
        return self.get_rank()

    @property
    def value(self):
        result = self.get_value()
        if result is None:
            result = self.default
        return result

    def increase(self, value):
        raise NotImplementedError

    def set(self, value):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def get_rank(self):
        raise NotImplementedError

    def get_value(self):
        raise NotImplementedError

    def top_ids(self, count):
        raise NotImplementedError
