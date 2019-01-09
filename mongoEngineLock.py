"""
  Implementation of pessimistic lock using mongoengine.

  Copyright 2018 ('Abhishek Tamrakar')

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
from mongoengine import fields as fld, connect
from mongoengine.document import Document
from mongoengine.queryset.visitor import Q
import contextlib


class MongoLockTimeout(Exception):
    pass


class MongoCollectionLocked(Exception):
    pass


class Locks(Document):
    ts = fld.DateTimeField(default=datetime.utcnow(), required=True, unique=True)
    locked = fld.BooleanField(default=False, required=True)
    entity = fld.StringField(required=True)
    meta = {
        'collection': 'locks.lock',
        'indexes': [
            {
                'fields': ['ts'],
                'expireAfterSeconds': 60
            },
            {
                'fields': ['entity'],
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
    def __call__(self, entity):

        if not self.lock(entity):
            data = self.getLockinfo(entity)
            data = json_util.loads(data)
            status = data[0]
            raise MongoLockTimeout(
                u'timedout, lock owned by {entity}, please try again after sometime.'.format(
                    entity=status['entity']
                )
            )
        try:
            yield
        finally:
            self.release(entity)

    def lock(self, entity):
        request_time = datetime.utcnow()
        while True:
            try:
                if not self.isLocked(entity):
                    data = Locks(
                        ts=request_time,
                        entity=entity,
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

                self.step += 1
                time.sleep(self.poll)

    def isLocked(self, entity):
        status = Locks.objects(Q(locked__exact=True) & Q(entity__exact=entity)).count()
        return True if status == 1 else False

    def getLockinfo(self, entity):

        return Locks.objects(entity__exact=entity).to_json()

    def release(self, entity):
        status = Locks.objects(entity__exact=entity).delete()

        return True if status == 1 else False
