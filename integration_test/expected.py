"""
Expected literal output for integration_test/fixtures/dummy_cli.py, captured once by actually
running it and inspecting the raw output -- not hand-transcribed. Shared across multiple test
files so the man page text lives in exactly one place.
"""

DUMMY_CLI_MAN_PAGE = (
    "dummy_cli.py\n"
    "\tgreet -- Greets someone by name.\n"
    "\t\tname | default:world | type:<class 'str'>\n"
    "\tadd -- Adds two required integers together.\n"
    "\t\tfirst | default:N/A | type:<class 'int'>\n"
    "\t\tsecond | default:N/A | type:<class 'int'>\n"
    "\tscale -- Multiplies value by factor.\n"
    "\t\tvalue | default:N/A | type:<class 'float'>\n"
    "\t\tfactor | default:2.0 | type:<class 'float'>\n"
    "\ttoggle -- Prints whether the flag is enabled.\n"
    "\t\tenabled | default:False | type:<class 'bool'>\n"
    "\tambiguous_one -- First half of an intentional abbreviation collision (both abbreviate to 'ao').\n"
    "\t\tnote | default:one | type:<class 'str'>\n"
    "\tanother_option -- Second half of an intentional abbreviation collision (both abbreviate to 'ao').\n"
    "\t\tnote | default:two | type:<class 'str'>\n"
)
