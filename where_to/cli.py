import argparse
import datetime
import os
import sys
import tempfile

from .application import Application


def main(args=None):

    if sys.stdin:
        do_main(args)

    else:
        dir_name = os.path.join(tempfile.gettempdir(), "where-to")
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        console_outfile = os.path.join(dir_name, "output.txt")

        if os.path.exists(console_outfile):
            os.remove(console_outfile)

        sys.stderr = sys.stdout = open(console_outfile, "w")
        try:
            do_main(args)
        except Exception as e:
            print(e)
        finally:
            sys.stdout.flush()
            stats = os.stat(console_outfile)
            if stats.st_size > 0:
                os.system("notepad.exe " + console_outfile)


def do_main(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "which",
        metavar="which",
        default="upcoming",
        choices=["upcoming", "next", "now"],
        type=str,
        nargs="?",
        help="Which meetings to show.",
    )
    parser.add_argument(
        "--display-mode",
        metavar="mode",
        default="lock",
        choices=["list", "lock"],
        type=str,
        help="""How to show the meetings - paint on the lock screen or list to the console (which is
        only useful when a terminal is available, for example when invoked via the where-to-console
        executable).""",
    )
    parser.add_argument(
        "--background-color",
        metavar="color",
        type=str,
        help="""The background color to print messages on. Only useful in 'lock' mode. If both this
        option and --background-image are present, the background images will be overlaid on a field
        of this color before messages are printed.""",
    )

    parser.add_argument(
        "--background-image",
        metavar="FILE",
        type=str,
        help="The background to overlay messages on. Only useful in 'lock' mode.",
    )
    parser.add_argument("--now", type=datetime.datetime.fromisoformat, help=argparse.SUPPRESS)

    args = parser.parse_args(args)

    Application(args).run()


if __name__ == "__main__":
    main(sys.argv[1:])
