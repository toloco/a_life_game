#!/usr/bin/env python
import sys

from .cli import CLI


def run():
    """
    Run life Cli
    """
    cli = CLI()

    # Commands as input
    if len(sys.argv) > 1:
        cmds = ' '.join(sys.argv[1:]).split(";")
        [cli.onecmd(c) for c in cmds]

    # interactive cli
    else:
        cli.cmdloop()
