from django.db.models import Field

from in_memory.fields import InMemoryFieldMixin
from in_memory.ssdb.models import SSDBSorter


class SSDBSortedIntegerField(InMemoryFieldMixin, Field):
    _class = SSDBSorter

