from django_redis import get_redis_connection


redis = get_redis_connection()


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
        return redis.zincrby(self.name, self.key, value)

    def reset(self):
        redis.zrem(self.name, self.key)

    @property
    def rank(self):
        return redis.zrevrank(self.name, self.key)

    @property
    def value(self):
        return redis.zscore(self.name, self.key)

    def top(self, count):
        return redis.zrevrange(self.name, 0, max(count - 1, 0)) or []
