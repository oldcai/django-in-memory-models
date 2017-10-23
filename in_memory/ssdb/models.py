from in_memory.models import Sorter
from in_memory.ssdb.utils import ssdb_client


class SSDBSorter(Sorter):

    def increase(self, value):
        return ssdb_client.zincr(self.name, self.key, value)

    def set(self, value):
        return ssdb_client.zset(self.name, self.key, value)

    def reset(self):
        ssdb_client.zdel(self.name, self.key)

    def get_rank(self):
        return ssdb_client.zrank(self.name, self.key)

    def get_value(self):
        return ssdb_client.zget(self.name, self.key)

    def top_ids(self, count):
        result = ssdb_client.zrrange(self.name, 0, max(count, 0)) or []
        result = [result[i] for i in range(0, len(result), 2)]
        return result


