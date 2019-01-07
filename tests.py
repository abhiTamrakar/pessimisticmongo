import random
from mongoEngineLock import mongoEngineLock, MongoLockTimeout

def ConcurrencyTest(name, poll, timeout, retries, iterations):
    lock = mongoEngineLock('locktests', poll=poll, timeout=timeout, retries=retries)
    try:
       with lock(name):
          for i in range(iterations):
             print 'iteration #%d, user - %s' % (i, name)
             random_user = str(random.random())
             with lock(random_user):
                print 'get lock with random user - %s' % (random_user)
    except MongoLockTimeout as e:
       print 'Timedout!!! details are: %s'  % (e.message)

"""
 Test 1: test with higher polling interval and dynamic users.
"""
print 'Test 1: high polling interval.'
ConcurrencyTest(str(random.random()), 1, 10, 5, 4)

"""
 Test 2: test with short timeout and dynamic users.
"""

print '\n\nTest 2: short timeout.'
ConcurrencyTest(str(random.random()), 1, 3, 5, 8)

"""
 Test 3: test with short polling, optimal timeout and dynamic users.
"""

print '\n\nTest 1: short polling and optimal timeout'
ConcurrencyTest(str(random.random()), 0.1, 10, 5, 3)
