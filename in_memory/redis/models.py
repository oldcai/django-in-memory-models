from django_redis import get_redis_connection

from in_memory.models import Sorter

redis = get_redis_connection()


class RedisSorter(Sorter):

    def increase(self, value):
        return redis.zincrby(self.name, self.key, value)

    def reset(self):
        redis.zrem(self.name, self.key)

    def get_rank(self):
        return redis.zrevrank(self.name, self.key)

    def get_value(self):
        return redis.zscore(self.name, self.key)

    def top_ids(self, count):
        return redis.zrevrange(self.name, 0, max(count, 0)) or []

    def set(self, value):
        current_value = self.value
        return redis.zincrby(self.name, self.key, value-current_value)
