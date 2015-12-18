import random
import Levenshtein

from enum import Enum

from scipy.stats import bernoulli


from .constants import (
    REDIS_ZORBS,
    REDIS_WORLD,
    DAY_REDUCE_ENERGY,
    DAY_REDUCE_LIFENESS,
    ENERGY_QUANTUM
)

from .zorb import Zorb, get_zorbs, get_random_zorb
from .inout import get_db
from .event import EventType, Event


class World(object):
    """Shared instance value
    """
    __instance = None
    genuine_properties = ("size", "energy", "reproducetibility", "day")

    def __new__(cls, **kwargs):
        if World.__instance is None:
            World.__instance = object.__new__(cls)
        return World.__instance

    def __init__(self, **kwargs):
        if kwargs:
            properties = ((k, v) for k, v in kwargs.items() if k in self.genuine_properties)
            for attribute, value in properties:
                setattr(self, attribute, value)
        else:
            db = get_db()
            for attribute, value in db.hgetall(REDIS_WORLD).items():
                attribute, value = attribute.decode("utf-8"), value.decode("utf-8")
                setattr(self, attribute, float(value))

    def __del__(self):
        # Update in Redis
        db = get_db()
        db.hmset(REDIS_WORLD, self.__dict__)

    @property
    def zorbs_no(self):
        db = get_db()
        return db.scard(REDIS_ZORBS)

    def next_day(self):
        self.day += 1


class Actions(Enum):
    """Actions
    """
    energy = 1
    zorb = 2
    none = 3
    attack = 4
    reproduce = 5
    run = 6


def zorb_day(world, zorb):

    def energy_zorb_or_none(world):
        """
            p_find_energy = max_energy_day / world_size
            p_find_zorb = no_zorbs / world_size
        """

        energy_found = bernoulli.rvs(
            (world.energy / world.size),
            size=1
        )
        if energy_found[0] == 1:
            return Actions.energy

        zorb_found = bernoulli.rvs(
            (world.zorbs_no / world.size),
            size=1
        )
        if zorb_found[0] == 1:
            return Actions.zorb

        return Actions.none

    def attack_reproduce_or_run(world, zorb_a, zorb_b):
        def can_attack(zorb_a, zorb_b):
            attack_defense_ratio = zorb_b.defense / zorb_a.attack
            speed_ratio = zorb_b.speed / zorb_a.speed

            return (attack_defense_ratio - random.expovariate(lambd=speed_ratio)) > 1

        def can_reproduce(world, zorb_a, zorb_b):
            """ 2 given zorbs can reproduce if diff is less than a given percentage
            """
            return Levenshtein.distance(zorb_a.dna, zorb_b.dna) < world.reproducetibility

        if can_reproduce(world, zorb_a, zorb_b):
            return Actions.reproduce
        elif can_attack(zorb_a, zorb_b):
            return Actions.attack
        else:
            return Actions.run

    action = energy_zorb_or_none(world)

    if action == Actions.energy:
        print("Energy found zid:`{}` total_energy :`{}`".format(zorb.zid, zorb.energy))

        # Create event
        event_data = zorb.__dict__
        event_data["feed"] = ENERGY_QUANTUM
        Event(event_type=EventType.Feed, data=event_data)

        zorb.energy += ENERGY_QUANTUM

    elif action == Actions.zorb:
        # Meet a zorb
        found_a_zorb = get_random_zorb()

        action = attack_reproduce_or_run(world, zorb, found_a_zorb)

        if action == Actions.attack:
            attack(world, zorb, found_a_zorb)

        elif action == Actions.reproduce:
            reproduce(world, zorb, found_a_zorb)

    # Finalize day
    zorb.lifeness -= DAY_REDUCE_LIFENESS
    zorb.energy -= zorb.consume / DAY_REDUCE_ENERGY
    if zorb.lifeness < 0 or zorb.energy < 0:
        zorb.alive = False


def attack(world, zorb_a, zorb_b):
    if round(zorb_a.attack, 2) == round(zorb_b.attack, 2):
        # Even attact (Fight)
        event_data = zorb_a.__dict__
        event_data = zorb_b.__dict__
        Event(event_type=EventType.Fight, data=event_data)

        # Both alive, both lose energy, but zorb_a lose 60% extra
        zorb_a.energy -= (zorb_a.consume * 1.6) / DAY_REDUCE_ENERGY
        zorb_b.energy -= zorb_b.consume / DAY_REDUCE_ENERGY

        # Both lose liveness
        zorb_a.lifeness -= DAY_REDUCE_LIFENESS
        zorb_b.lifeness -= DAY_REDUCE_LIFENESS
    elif zorb_a.attack > zorb_b.attack:
        # Stronger attact (Hunt)
        event_data = zorb_a.__dict__
        event_data = zorb_b.__dict__
        Event(event_type=EventType.Hunt, data=event_data)

        print("Zorb `{}` hunted zid:`{}` ".format(zorb_a.zid, zorb_a.zid))

        # zorb_a alive only, zorb_a recovers 80% of zorb_b energy, liveness slightly
        zorb_a.energy += zorb_b.energy * 0.6

        # zorb_b dead
        zorb_b.alive = False
        pass
    else:
        #  Weaker attact

        # zorb_a P alive (zorb_b.attack / zorb_a.defense)
        if (zorb_b.attack / zorb_a.defense) >= 1:
            zorb_a.alive = True
            # zorb_a, if alive, lose enery, lose liveness sensible
            zorb_a.energy -= (zorb_a.consume * 1.8) / DAY_REDUCE_ENERGY
            zorb_a.lifeness -= DAY_REDUCE_LIFENESS * 2

            event_data = zorb_a.__dict__
            event_data = zorb_b.__dict__
            Event(event_type=EventType.Fight, data=event_data)
        else:
            zorb_a.alive = False
            event_data = zorb_a.__dict__
            event_data = zorb_b.__dict__
            Event(event_type=EventType.Kill, data=event_data)

        # zorb_b alive, lose energy, liveness slightly
        zorb_b.lifeness -= DAY_REDUCE_LIFENESS
        zorb_a.energy -= (zorb_a.consume * 1.2) / DAY_REDUCE_ENERGY


def reproduce(world, zorb_a, zorb_b):
    """Share 50% energy of both parents
    Creates 3 sons with the avg of all attributes
    """

    event_data = zorb_a.__dict__
    event_data = zorb_b.__dict__
    Event(event_type=EventType.Reproduced, data=event_data)

    avgs = {
        k: (getattr(zorb_a, k) + getattr(zorb_b, k))/2
        for k in Zorb.INMUTABLE_ATTRIBUTES
    }
    zorb_a.energy, zorb_b.energy = zorb_a.energy * .5, zorb_b.energy * .5
    avgs["energy"] = (zorb_a.energy + zorb_b.energy) / 3
    [Zorb.birth(world, avgs) for _ in range(3)]


def play(world):
    """Play 1 day of this world
    """
    for zorb in get_zorbs():
        zorb_day(world, zorb)
