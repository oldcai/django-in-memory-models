### Example

```
from in_memory.ssdb.fields import IntegerField
from in_memory.ssdb.fields import Sorter
#from in_memory.redis.fields import IntegerField
#from in_memory.redis.fields import Sorter


class IMAccountStatistics(InMemoryModel):
    user = InMemoryOneToOneKey(User, related_name='total_statics')
    total_subscription = IntegerField()

    @classmethod
    def get_by_user(cls, pk):
        instance = cls(user_id=pk, user_foreign_id=pk)
        return instance

s = User.objects.first().total_statics
print(s)
print(s.user)
print(s.total_subscription.value)
s.total_subscription += 1
print(s.total_subscription.value)
```

Output

```
IMAccountStatistics object
oldcai
0
1
```