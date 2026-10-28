"""Nmap service: performs port + service (-sV) detection on a target.

By default -sT (TCP connect scan) + -Pn (skip host discovery/ping) are used;
neither of them requires a raw socket, so they also work on
containerized/sandboxed platforms such as Render. -Pn matters: even though
-sT does not need a raw socket, nmap's default host discovery phase (the
ICMP/ping it sends to check whether the target is "up") uses a raw socket
separately, and in environments where raw sockets are blocked this makes
nmap stop right at the start with "Couldn't open a raw socket" before it
ever reaches the port scan. -Pn skips this phase entirely and assumes the
target is up.

-O (OS detection) additionally requires raw socket access; many PaaS
providers (Render included) block it entirely at the platform level --
setcap or sudo do not help here, because the restriction is independent of
the container's user privileges. If you run on a server that allows raw
socket access (e.g. your own VPS), you can enable the -O flag with
`NMAP_OS_DETECTION=true`; if needed, you can also bring sudo into play with
`NMAP_USE_SUDO=true` (see README "Nmap Setup").

Before being passed to the subprocess, the target is strictly validated as
an IP address or hostname (see `_is_valid_target`). The command is always
run as an argv list (there is NO `shell=True`), so shell injection is not
possible even without validation; still, validation prevents the target from
being accidentally interpreted as an extra nmap flag.
"""
from __future__ import annotations

import ipaddress
import re

from app.config import settings
from app.utils.logger import get_logger
from app.utils.subprocess_tools import SubprocessError, run_subprocess

logger = get_logger(__name__)

_HOSTNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9\-.]{0,251}[A-Za-z0-9])?$")


class NmapError(Exception):
    pass


def _is_valid_target(target: str) -> bool:
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass
    return bool(_HOSTNAME_RE.match(target))


async def scan_target(target: str) -> str:
    """Run nmap against the target and return the raw output.

    Default command: `nmap -Pn -sT -sV <target>`. If `settings.nmap_os_detection`
    is True, `-O` is added as well (only meaningful in environments that
    allow raw socket access).
    """
    target = target.strip()

    if not target or not _is_valid_target(target):
        raise NmapError(
            "Invalid target. Enter only an IP address or a hostname "
            "(e.g. 8.8.8.8 or example.com)."
        )

    cmd = [settings.nmap_binary, "-Pn", "-sT", "-sV"]
    if settings.nmap_os_detection:
        cmd.append("-O")
    cmd.append(target)

    if settings.nmap_use_sudo:
        cmd = ["sudo", "-n", *cmd]

    try:
        return await run_subprocess(cmd, timeout=settings.nmap_timeout)
    except SubprocessError as exc:
        logger.error("Nmap execution error: %s", exc)
        raise NmapError(str(exc)) from exc
