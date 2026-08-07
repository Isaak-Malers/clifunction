from __future__ import annotations

import re


def name_and_abbreviations(*, python_name: str) -> list[str]:
    """
    Given a string name for a python function or method or argument, returns a list with multiple possible matches.
    Examples:
        python_name='name_and_abbreviations'
        ['name_and_abbreviations', 'naa']

        python_name='myCamelFunc3'
        ['myCamelFunc3', 'mcf3']

        This function is then used in a bunch of places to map what a user might type on the command line
        to what function or argument they are most likely to want to specify in python.
    """
    if '_' in python_name:
        matches = re.findall(r'_[a-zA-Z0-9]', python_name)
        abbreviation = python_name[0] + "".join([char[1] for char in matches])
    else:
        matches = re.findall(r'[A-Z0-9]', python_name)
        # pylint: disable=unnecessary-comprehension
        abbreviation = python_name[0] + "".join([char for char in matches])

    # note:  these don't strictly need to be sorted, but it makes the test cases a lot more consistent/easier to
    # write
    return sorted(list({python_name, abbreviation.lower()}), key=lambda item: -len(item))
