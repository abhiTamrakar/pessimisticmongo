# PessimisticLockMongo
Pessimistic lock implementation for mongoengine, using  a very simple logic

`Inspired by mongolock and pessimistic locks concept.`

Read more about the implementation [here](https://medium.com/@abhishek.tamrakar/implementing-pessimistic-locks-in-mongodb-8f3fbe2ddfa9)

## Setting up the context
The real intention behind writing this utility isn't just Database locking. Locking is already handled in mongoDB, sufficient or not, but it locks the Database with exclusive write locks, thats when the problem begins.

With multiple collections and frequent requests coming in, it is on DB performance when a transaction is waitingon the lock on Database, when there is only one collection involved in the operation at the moment.

Hence, this utility, targets collection based locking mechanism, fully controoled in application for the DB.

## Usage
```
from mongoEngineLock import mongoEngineLock, MongoLockTimeout

lock = mongoEngineLock('<db..name>', poll=1, timeout=40, retries=15)

with lock(entity):
   try:
      <..do something here..>
   except Exception as e:
      raise e

# or use with conditional statements

if lock(entity):
   try:
      <..do something here..>
   except Exception as e:
      raise e
```
##### mongoEngineLock Parameters:
**client**: connection information for MongoEngine.

**poll**: interval to introduce a delay while retrying.

**timeout**: interval (seconds) to introduce timeout.

**retries**: number of retries before timeout.

##### Instance of the class takes exactly 1 parameter: 
**entity**: owner of the lock or collection name(in case there are more than one collections to be managed in a database).

## Misc
* Try to use a smaller polling interval or interval based on time taken to execute the query, in case of bigger DB size.
* Worth to mention, timeout or retries should not supersede each other. 
* Use proper NTP servers to keep your machines in time sync.
