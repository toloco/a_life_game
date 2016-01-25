import uuid
from enum import Enum, unique

from .inout import get_db
from .constants import (
    REDIS_EVENTS,
    REDIS_EVENTS_TYPE,
    REDIS_EVENTS_PREFIX
)


@unique
class EventType(Enum):
    Born = 1
    Reproduced = 2
    Dead = 3
    Hunt = 4
    Kill = 5
    Fight = 6
    Feed = 7

    def __str__(self):
        return self.name


class Event(object):

    def __init__(self, event_type, data):
        self.id = str(uuid.uuid1())
        self.type = event_type
        self.data = data

        # Avoid circular import
        from .world import World
        try:
            self.data["day"] = World().day
        except:
            self.data["day"] = 1

    def __del__(self):
        db = get_db()
        key = REDIS_EVENTS_PREFIX.format(
            type=self.type,
            id=self.id
        )

        db.hmset(key, self.data)
        db.sadd(REDIS_EVENTS, key)
        db.sadd(REDIS_EVENTS_TYPE.format(self.type), key)
