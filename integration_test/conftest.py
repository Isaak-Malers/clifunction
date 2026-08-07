"""
System-level ("black box") test harness for clifunction.

Everything in test/ calls Targets/DefaultArgumentParser methods directly, in-process. This
suite deliberately does the opposite: it execs a real `python <fixture>.py <args...>`
subprocess for every case and asserts on stdout, stderr, and the exit code -- exactly what an
end user (or an agent driving a CLI) actually sees. Nothing here imports CliFunction or
clifunction directly.

The library is made importable via PYTHONPATH pointing at the repo root, rather than by placing
fixture scripts next to the library source the way Example.py sits next to CliFunction.py.
Python only ever puts a *script's own* directory on sys.path, never the invoking cwd, so
PYTHONPATH is what actually decouples "where the library lives" from "where the user's script
lives" -- which is exactly what varies between a pip-installed library and this repo's checked
-out source. It's also what keeps this harness unchanged no matter what the library's internal
module/package layout looks like, on this branch or any other.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def run_tool():
    """
    Returns a callable: run_tool("fixture_name.py", "arg1", "arg2", ...) -> CompletedProcess.

    Runs the named fixture script from integration_test/fixtures/ as a real subprocess, the
    same way a user would run `python my_tool.py arg1 arg2`.
    """
    def _run(fixture_name: str, *args: str) -> subprocess.CompletedProcess:
        script = FIXTURES_DIR / fixture_name
        assert script.is_file(), f"no such fixture: {script}"

        env = dict(os.environ)
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = str(REPO_ROOT) + (os.pathsep + existing if existing else "")

        # Deliberately a relative path, run with cwd=FIXTURES_DIR: sys.argv[0] inside the
        # fixture then reads exactly "dummy_cli.py" (what os.path.basename(sys.argv[0]) already
        # normalizes for the man page header, but *not* what the raw args list embedded in
        # "No Matches found for args: [...]" uses) -- matching a real `python dummy_cli.py ...`
        # invocation instead of leaking this harness's absolute path into expected output.
        return subprocess.run(
            [sys.executable, fixture_name, *args],
            capture_output=True,
            text=True,
            cwd=FIXTURES_DIR,
            env=env,
            timeout=10,
            check=False,
        )
    return _run
