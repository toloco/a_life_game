import uuid
import random

from .inout import get_db
from .event import Event, EventType
from .constants import (
    ZORB_INITIAL_LIFENESS,
    REDIS_ZORBS,
    REDIS_ZORBS_PROCESSED,
    REDIS_ZORBS_PROCESSING,
    REDIS_ZORB_PREFIX
)


class Zorb(object):

    INMUTABLE_ATTRIBUTES = ("defense", "attack", "speed")

    def __init__(self, **kwargs):
        for attribute, value in kwargs.items():
            setattr(self, attribute, value)

    def __del__(self):
        if not hasattr(self, "zid"):
            return None
        key = self.zid_key()
        db = get_db()

        if self.alive:
            # Update in Redis
            db.hmset(key, self.__dict__)
        else:
            print("Dead zid:`{}` born :`{}`".format(self.zid, self.born))

            # Create event
            Event(event_type=EventType.Dead, data=self.__dict__)

            # Remove from Redis
            db.delete(key)
            db.srem(REDIS_ZORBS, key)
            db.srem(REDIS_ZORBS_PROCESSED, key)
            db.srem(REDIS_ZORBS_PROCESSING, key)

    @property
    def weight(self):
        # Weight (based upon defense x attack)
        return self.defense + self.attack

    @property
    def consume(self):
        # Consume (Energy consume based upon speed x weight)
        return self.speed * self.weight

    @property
    def dna(self):
        try:
            return self._dna
        except AttributeError:
            self._dna = "".join((
                bin(int(self.defense)),
                bin(int(self.attack)),
                bin(int(self.speed)),
            ))
            return self._dna

    @classmethod
    def birth(cls, world, kwargs):
        kwargs["lifeness"] = ZORB_INITIAL_LIFENESS
        kwargs["zid"] = str(uuid.uuid1())
        kwargs["alive"] = True
        kwargs["born"] = world.day

        for k in cls.INMUTABLE_ATTRIBUTES:
            kwargs[k] = kwargs[k] + random.gauss(0, .1)

        obj = cls(**kwargs)

        # Create in Redis
        obj.dehidratate()

        # Event register
        Event(event_type=EventType.Born, data=obj.__dict__)

        return obj

    @classmethod
    def hidratate(cls, key):
        db = get_db()
        kwargs = {}

        for key, value in db.hgetall(key).items():
            key, value = key.decode("utf-8"), value.decode("utf-8")
            if key == "alive":
                value = True
            elif key in ("defense", "attack", "speed", "energy", "lifeness"):
                value = float(value)
            kwargs[key] = value

        return cls(**kwargs)

    def zid_key(self):
        return "{}{}".format(REDIS_ZORB_PREFIX, self.zid)

    def dehidratate(self):
        db = get_db()
        key = self.zid_key()
        # Add zorb data
        db.hmset(key, self.__dict__)
        # Set zorb into set living zorbs
        db.sadd(REDIS_ZORBS, key)


def get_zorbs():
    def restart_queue(db):
        # Iteration ended
        if (db.scard(REDIS_ZORBS_PROCESSING) == 0 and
                db.scard(REDIS_ZORBS_PROCESSED) == 0):
            # Copy main set into processing set
            db.sunionstore(REDIS_ZORBS_PROCESSING, REDIS_ZORBS)
            db.sunionstore(REDIS_ZORBS_PROCESSED, REDIS_ZORBS)

        # Processing error, restore from processed
        elif (db.scard(REDIS_ZORBS_PROCESSING) == 0 and
                db.scard(REDIS_ZORBS_PROCESSED) > 0):
            db.sunionstore(REDIS_ZORBS_PROCESSING, REDIS_ZORBS_PROCESSED)

    db = get_db()

    # Restart queue if needed
    restart_queue(db)

    while True:
        zorb = db.spop(REDIS_ZORBS_PROCESSING)
        if not zorb:
            raise StopIteration()
        zorb = Zorb.hidratate(zorb.decode('utf-8'))
        yield zorb
        db.srem(REDIS_ZORBS_PROCESSED, zorb.zid)


def get_random_zorb():
    db = get_db()
    zorb = db.srandmember(REDIS_ZORBS)
    return Zorb.hidratate(zorb.decode('utf-8'))
