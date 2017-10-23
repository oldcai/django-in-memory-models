from django.db.models import Field

from in_memory.fields import InMemoryFieldMixin
from in_memory.redis.models import RedisSorter


class RedisSortedIntegerField(InMemoryFieldMixin, Field):
    _class = RedisSorter
