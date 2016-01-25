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

    def do_reset(self, _):
        print(">> DB clear")

    def help_reset(self):
        print("Reset the sandbox")

    def do_new_world(self, _):
        if input("Wanna a brave new world? [Y/n]") in self.NO:
            print("OK, no World then")

        try:
            world = World()
        except:
            world = World(
                size=100001,
                energy=1000,
                reproducetibility=4,
                day=1
            )

        print("Please set the following parameters:")
        size = input("Size, this one dimension value [{}]".format(world.size))
        energy = input("Energy, this total energy available per day [{}]".format(world.energy))
        reproducetibility = input("Reproducetibility, this change of reproduction in every Zorb rendevouz [{}]".format(world.reproducetibility))
        day = input("Day, set the initial day[{}]".format(world.day))

        World(
            size=size or world.size,
            energy=energy or world.energy,
            reproducetibility=reproducetibility or world.reproducetibility,
            day=day or world.day
        )

    def help_new_world(self):
        print("Set new attributes for the sandbox")

    def do_add_zorbs(self, _):
        zorbs = input("How many new zorbs? [1..∞]") or 0

    def help_add_zorbs(self):
        print("Add new zorbs with properties")

    def do_play(self, days):
        if input("Are you sure you wanna play {} days? [Y/n]".format(days)) in self.YES:
            pass
        else:
            print(">> No")

    def help_play(self):
        print("Play X days")
