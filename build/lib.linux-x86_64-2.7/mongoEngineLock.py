"""
  Implementation of pessimistic lock using mongoengine.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
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
        
        self.poll = poll
        self.timeout = timeout
        self.retries = retries
        connect(self.client)

        self.step = 1
        self.start_time = datetime.utcnow()

    @contextlib.contextmanager
    def __call__(self, owner):

        if not self.lock(owner):
           data = self.getLockinfo(owner)
           data = json_util.loads(data)
           status = data[0]
           raise MongoLockTimeout(
              u'timedout, lock owned by {owner}, please try again after sometime.'.format(
                 owner=status['owner']
              )
           )
        try:
           yield
        finally:
           self.release(owner) 

    def lock(self, owner):
        request_time = datetime.utcnow()
        while True:
           try:
              if not self.isLocked(owner):
                 data = Locks(
                    ts=request_time,
                    owner=owner,
                    locked=True
                 )
                 data.save()
                 return True
              else:
                 raise MongoCollectionLocked

           except MongoCollectionLocked:
              pass

           finally: 
              if self.step == self.retries or datetime.utcnow() >= self.start_time + timedelta(seconds=self.timeout):
                 return False

              self.step+=1
              time.sleep(self.poll)

    def isLocked(self, owner):
        status = Locks.objects(owner__exact=owner).count()
        return True if status == 1 else False

    def getLockinfo(self, owner):

        return Locks.objects(owner__exact=owner).to_json()

    def release(self, owner):
        status = Locks.objects(owner__exact=owner).delete()

        return True if status == 1 else False
