"""
Implement pessimistic lock using mongoengine.

"""
import time
from bson import json_util
from datetime import datetime, timedelta
from mongoengine import *
import contextlib

class MongoLockTimeout(Exception):
   pass

class MongoCollectionLocked(Exception):
   pass

class Locks(Document):
    ts = DateTimeField(default=datetime.utcnow(), required=True, unique=True)
    locked = BooleanField(default=False, required=True)
    owner = StringField(required=True)
    meta = {
       'collection': 'locks.lock',
       'indexes': [
           {
               'fields': ['ts'],
               'expireAfterSeconds': 60
           },
           {
               'fields': ['owner'],
               'unique': False
           }
       ]
    }

class mongoEngineLock(object):
    def __init__(self, client=None, poll=0.1, timeout=60, retries=5):
        if client:
           self.client = client
           print 'client=%s' % (self.client)
        
        self.poll = poll
        self.timeout = timeout
        self.retries = retries
        connect(self.client)

    @contextlib.contextmanager
    def __call__(self, owner):
        if not self.lock(owner):
           data = self._get_lockinfo()
           data = json_util.loads(data)
           status = data[0]
           raise MongoLockTimeout(
              u'timedout, lock owned by {owner}, since {ts}. Please try after sometime.'.format(
                 owner=status['owner'], ts=status['ts']
              )
           )
        try:
           yield
        finally:
           self.release() 

    def lock(self, owner):
        _retry_step = 1
        _now = datetime.utcnow()
        while True:
           try:
              if not self.isLocked():
                 data = Locks(
                    ts=_now,
                    owner=owner,
                    locked=True
                 )
                 data.save()

                 return True
              else:
                 raise MongoCollectionLocked

           except MongoCollectionLocked:
              print ('rt:%d, rts: %d, now: %s', _retry_step, self.retries, _now)
              if _retry_step == self.retries or datetime.utcnow() >= _now + timedelta(seconds=self.timeout):
                 return False

              _retry_step+=1
              time.sleep(self.poll)

    def isLocked(self):
        status = Locks.objects(locked__exact=True).count()

        return True if status == 1 else False

    def _get_lockinfo(self):

        return Locks.objects(locked__exact=True).to_json()

    def release(self):
        status = Locks.objects(locked__exact=True).delete()

        return True if status == 1 else False
