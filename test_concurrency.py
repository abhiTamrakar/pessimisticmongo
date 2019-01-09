import random, time
from mongoEngineLock import mongoEngineLock, MongoLockTimeout
import pytest

def get_connection(poll, timeout, retries):
    # start the db connections
    return mongoEngineLock('locktests', poll=poll, timeout=timeout, retries=retries)

def test_lock():
    """
    Test if the lock is gained and released immediately after the operation is finished.
    """
    lock = get_connection(1, 5, 5)
    collection = str(random.random())
    with lock(collection):
        assert lock.isLocked(collection) == True

    assert lock.isLocked(collection) == False

def test_timeout():
    """
    Test is the timeout exception is raised with proper message.
    """
    lock = get_connection(1, 5, 15)
    collection = str(random.random())
    with pytest.raises(MongoLockTimeout) as excinfo:
        with lock(collection):
            for i in range(15):
                with lock(collection):
                    assert lock.isLocked(collection) == False

    assert 'timedout' in str(excinfo.value)
