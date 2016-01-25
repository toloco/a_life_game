import cmd

from termcolor import colored

from .world import World


class CLI(cmd.Cmd):
    """
        - Run x number of days
        - Add new zorbs
        - Setup a new world / reset
        - Export ??

    """
    prompt = '👉  '
    intro = colored("""
   __ _  __               __   _____           _
  / /(_)/ _| ___    ___  / _| / _  / ___  _ __| |__
 / / | | |_ / _ \  / _ \| |_  \// / / _ \| '__| '_ \ ø
/ /__| |  _|  __/ | (_) |  _|  / //\ (_) | |  | |_) |
\____/_|_|  \___|  \___/|_|   /____/\___/|_|  |_.__/
    """, "green")
    ruler = colored('~~', 'red')

    YES = set(('yes', 'y', 'ye', ''))
    NO = set(('no', 'n'))

    @staticmethod
    def get_float_attribute(msg, error="Please use an int"):
        def to_float_or_none(number):
            try:
                return float(number)
            except:
                return None

        for _ in range(10):
            number = to_float_or_none(input(msg))
            if not number:
                print(error)
            else:
                return number
        else:
            raise Exception("I said float, float!!")

    @staticmethod
    def get_int_attribute(msg, error="Please use an int"):
        def to_int_or_none(number):
            try:
                return int(number)
            except:
                return None

        for _ in range(10):
            number = to_int_or_none(input(msg))
            if not number:
                print(error)
            else:
                return number
        else:
            raise Exception("I said int, int!!")

    def do_reset(self, _):
        print(">> DB clear")

    def help_reset(self):
        print("Reset the sandbox")

    def do_new_world(self, _):
        try:
            world = World()
        except:
            world = World(
                size=100000,
                energy=1000,
                reproducetibility=4,
                day=1
            )

        if input("Wanna a brave new world? [Y/n]") in self.NO:
            print("OK, no World then")

        size = input("> Size, this one dimension value [{}]".format(world.size))
        energy = input("> Energy, this total energy available per day [{}]".format(world.energy))
        reproducetibility = input("> Reproducetibility, this change of reproduction in every Zorb rendevouz [{}]".format(world.reproducetibility))
        day = input("> Day, set the initial day[{}]".format(world.day))

        World(
            size=size or world.size,
            energy=energy or world.energy,
            reproducetibility=reproducetibility or world.reproducetibility,
            day=day or world.day
        )

    def help_new_world(self):
        print("Set new attributes for the sandbox")

    def do_add_zorbs(self, _):
        try:
            world = World()
        except:
            print("World is not setup, my master, please \"new_world\" first")

        zorbs = self.get_int_attribute(msg="How many new zorbs? [1..∞]")
        print(zorbs)

        defense = self.get_float_attribute(
            msg="Set defense: ",
            error="Please use a positive float"
        )
        print(defense)

        speed = self.get_float_attribute(
            msg="Set speed: ",
            error="Please use a positive float"
        )

        attack = self.get_float_attribute(
            msg="Set attack: ",
            error="Please use a positive float"
        )

        d = dict(
            defense=10,
            speed=10,
            attack=10
        )

        [Zorb.birth(world, d) for i in range(zorbs)]

    def help_add_zorbs(self):
        print("Add new zorbs with properties")

    def do_play(self, days):
        if input("Are you sure you wanna play {} days? [Y/n]".format(days)) in self.YES:
            pass
        else:
            print(">> No")

    def help_play(self):
        print("Play X days")
