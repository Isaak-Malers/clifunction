"""
Provides the simplest possible wrapper for exposing python functions to be run on a command line!
Annotate python functions with the [@cli_function] decorator, and annotate the function fully with the builtin python tools.
The library will generate a man page for your file, and provide helpful error messages when arguments are not formatted correctly.
"""
from __future__ import annotations

import json
import sys

from .exceptions import CliFunctionException
from .parsing import DefaultArgumentParser
from .targets import Targets

__all__ = [
    "cli_function",
    "cli",
    "CliFunctionException",
    "Targets",
    "DefaultArgumentParser",
]

targets = Targets()

# Exit codes, distinguished so a caller (human or agent) can branch on failure *kind* without
# parsing stdout text.  0 is success (implicit -- plain return / no SystemExit raised).
EXIT_NO_ARGS = 1
EXIT_NO_MATCH = 2
EXIT_AMBIGUOUS_MATCH = 3


def cli_function(target_to_add):
    """
    Decorates a function, and at import time registers that function with the CLI tool.
    This allows the cli function to know what functions are available and should be exposed.
    """
    targets.add_target(target_to_add)
    return target_to_add


def cli(args: list[str] | None = None):
    """
    Runs the CLI tool for the current file
    """
    if args is None:
        args = sys.argv

    if len(args) < 2:
        print(targets.man())
        raise SystemExit(EXIT_NO_ARGS)

    # Reserved, not routed through the normal target-matching machinery: "--schema" can never
    # collide with a real target name/abbreviation, since name_and_abbreviations never produces
    # anything starting with "--".
    if args[1] == "--schema":
        print(json.dumps(targets.schema(), indent=2))
        return

    if not targets.execute(args=args):
        print(targets.man())
        # execute() already ran the same match-collection internally; re-deriving the count
        # here (rather than changing execute()'s bool return contract) only happens on the
        # failure path, so the common (successful) path pays nothing extra for it.
        match_count = len(targets.collect_method_kwargs(args=args))
        raise SystemExit(EXIT_NO_MATCH if match_count == 0 else EXIT_AMBIGUOUS_MATCH)
