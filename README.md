## Introduce
For performance critical fields and models, and don't want to lose the convenience of getting them like attributes.

You can adding user page view by `user.statistics.visits += 1` and get the value by `user.statistics.visits.value
`
 
## Backends

- redis
- ssdb

## Install
`pip install django-in-memory-models`


## Example

```
from in_memory.ssdb.fields import IntegerField
#from in_memory.redis.fields import IntegerField


# InMemoryModel do not create tables when migrating.
# You can add fields to django.db.models.Model directly.
class IMAccountStatistics(InMemoryModel):
    user = InMemoryOneToOneKey(User, related_name='total_statics')
    total_subscription = IntegerField()

    @classmethod
    def get_by_user(cls, pk):
        instance = cls(user_id=pk)
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

## TODO

- Django system cache backend
