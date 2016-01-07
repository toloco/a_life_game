import cmd


class CLI(cmd.Cmd):
    """
        - Run x number of days
        - Add new zorbs
        - Setup a new world / reset
        - Export ??

    """
    prompt = '👉 '
    intro = "Life of zorbs"
    ruler = "~~"

    YES = set(('yes', 'y', 'ye', ''))
    NO = set(('no', 'n'))

    def do_reset(self, _):
        print(">> DB clear")

    def help_reset(self):
        print("Reset the sandbox")

    def do_new_world(self, _):
        if input("Wanna a brave new world? [Y/n]") in self.YES:
            print("Please set the following parameters:")
            size = input("Size, this one dimension value [{}]".format(0))
            energy = input("Energy, this total energy available per day [{}]".format(0))
            reproducetibility = input("Reproducetibility, this change of reproduction in every Zorb rendevouz [{}]".format(0))
            day = input("Day, set the initial day if you want to my lord [{}]".format(1)) or "1"
        else:
            pass

    def help_new_world(self):
        print("Set new attributes for the sandbox")
