from django.db.models import Field

from in_memory.fields import InMemoryFieldMixin
from in_memory.ssdb.models import Sorter


class IntegerField(InMemoryFieldMixin, Field):
    _class = Sorter

