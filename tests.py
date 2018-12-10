import random
import time
from mongoEngineLock import mongoEngineLock, MongoLockTimeout

lock = mongoEngineLock('locktests', poll=2, retries=15)

def TimeoutTest(name):
    print 'Trying Timeout Test with value %s' % (name)
    with lock(name):
        try:
            for i in range(12):
                print 'i is %d for id %s' % (i, name)
                time.sleep(5)
        except Exception as e:
            raise e

def ConcurrencyTest(name):
    print 'Trying Concurrency Test with value %s' % (name)
    with lock(name):
        try:
            for i in range(8):
                print 'i is %d for id %s' % (i, name)
                time.sleep(5)
        except Exception as e:
            raise e

try:
    TimeoutTest(str(random.random()))
except MongoLockTimeout as e:
    print e.message

try:
    ConcurrencyTest(str(random.random()))
except MongoLockTimeout as e:
    print e.message
