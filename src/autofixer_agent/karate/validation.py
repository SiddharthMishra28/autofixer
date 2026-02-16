from __future__ import annotations

import shlex
import subprocess
from pathlib import Path


ALLOWED_BRANCHES = {"main", "master", "release"}


def run_validation_command(command: str, cwd: str, timeout_s: int = 300) -> dict:
    completed = subprocess.run(
        shlex.split(command),
        cwd=Path(cwd),
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
