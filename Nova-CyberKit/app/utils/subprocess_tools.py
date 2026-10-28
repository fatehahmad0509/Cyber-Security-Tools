"""Shared helper for running external CLI tools (nmap, phoneinfoga, ...).

Important security note: commands are always run as a list (argv) and
`shell=True` is NOT used. This way, user input such as targets/numbers is
never interpreted directly by the shell, and command injection is not
possible. Even so, each service should separately validate its own input
(IP/host, phone number) before passing it to the subprocess.
"""
from __future__ import annotations

import asyncio
import re

_ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    """Strip terminal color/control codes (ANSI escapes) from the text."""
    return _ANSI_RE.sub("", text)


class SubprocessError(Exception):
    pass


async def run_subprocess(cmd: list[str], *, timeout: float) -> str:
    """Run the given command as a subprocess and return its combined
    (stdout+stderr) output as text with ANSI codes stripped.

    `cmd` is an argv list (the first element is the executable name).
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except FileNotFoundError as exc:
        raise SubprocessError(
            f"Command '{cmd[0]}' not found. Make sure it is installed on the server "
            "and available in PATH (see README)."
        ) from exc
    except PermissionError as exc:
        raise SubprocessError(
            f"Could not run '{cmd[0]}' (permission denied)."
        ) from exc

    try:
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError as exc:
        try:
            proc.kill()
        except Exception:
            pass
        raise SubprocessError(
            f"Operation timed out after {timeout:.0f} seconds."
        ) from exc

    return strip_ansi(stdout.decode(errors="ignore"))
