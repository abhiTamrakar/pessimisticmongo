# PessimisticLockMongo
Pessimistic lock implementation for mongoengine, using  a very simple logic

`Inspired by mongolock and pessimistic locks concept.`

Read more about the implementation [here](https://medium.com/@abhishek.tamrakar/implementing-pessimistic-locks-in-mongodb-8f3fbe2ddfa9)

## usage
```
from mongoEngineLock import mongoEngineLock, MongoLockTimeout

lock = mongoEngineLock('<db..name>', poll=1, timeout=40, retries=15)

with lock(owner):
   try:
      <..do something here..>
   except Exception as e:
      raise e

# or use with conditional statements

if lock(owner):
   try:
      <..do something here..>
   except Exception as e:
      raise e
```
##### mongoEngineLock Parameters:
**client**: connection information for MongoEngine.

**poll**: interval to introduce a delay while retrying.

**retries**: number of retries before timeout.

##### Instance of the class takes exactly 1 parameter: 
**owner**: owner of the lock or collection name(in case there are more than one collections to be managed in a database).

## misc
* Try to use a smaller polling interval or interval based on time taken to execute the query, in case of bigger DB size.
* Worth to mention, timeout or retries should not supersede each other. 
* Use proper NTP servers to keep your machines in time sync.
