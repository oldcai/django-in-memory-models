from in_memory.ssdb.utils import ssdb_client


class Sorter(object):
    def __init__(self, name, key):
        self.name = name
        self.key = key
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

    def increase(self, value):
        return ssdb_client.zincr(self.name, self.key, value)

    def reset(self):
        ssdb_client.zdel(self.name, self.key)

    @property
    def rank(self):
        return ssdb_client.zrank(self.name, self.key)

    @property
    def value(self):
        return ssdb_client.zget(self.name, self.key)

    def top(self, count):
        return ssdb_client.zrrange(self.name, 0, max(count-1, 0)) or []


