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
from in_memory.ssdb.fields import SSDBSortedIntegerField as IntegerField
# from in_memory.redis.fields import RedisSortedIntegerField as IntegerField


# InMemoryModel do not create tables when migrating.
# You can add fields to django.db.models.Model directly.
class AccountStatistics(InMemoryModel):
    user = InMemoryOneToOneKey(User, related_name='statistics')
    total_subscription = IntegerField(default=0)

    @classmethod
    def get_by_user(cls, pk):
        instance = cls(user_id=pk)
        return instance
        
    def __str__(self):
        return '<Account Statistics: %s>' % self.user

s = User.objects.first().statistics
s.total_subscription.reset()
print(s.total_subscription.value)
s.total_subscription += 1
print(s.total_subscription.value)
s.total_subscription = 200
print(s.total_subscription.value)
top_users = s.total_subscription.top(1)
print(top_users)
top_user = top_users[0]
print(top_user)
print(top_user.user)
print(top_user.total_subscription.value)
```

Output

```
0
1
200
[<AccountStatistics: <Account Statistics: oldcai>>]
<Account Statistics: oldcai>
oldcai
200
```

## TODO

- Django system cache backend
