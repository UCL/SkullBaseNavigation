# coding=utf-8

"""Command line processing"""


import argparse
from skullbasenavigation import __version__
from skullbasenavigation.ui.skullbasenavigation_demo import run_demo


def main(args=None):
    """Entry point for Skull Base Navigation application"""

    parser = argparse.ArgumentParser(description='Skull Base Navigation')

    parser.add_argument("-t", "--text",
                        required=False,
                        default="This is Skull Base Navigation",
                        type=str,
                        help="Text to display")

    parser.add_argument("--console", required=False,
                        action='store_true',
                        help="If set, Skull Base Navigation "
                             "will not bring up a graphical user interface")

    version_string = __version__
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='Skull Base Navigation version ' + friendly_version_string)

    args = parser.parse_args(args)

    run_demo(args.console, args.text)
