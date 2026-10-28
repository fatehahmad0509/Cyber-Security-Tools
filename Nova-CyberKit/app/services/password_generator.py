"""Random password generator service.

Uses the `secrets` module from the Python standard library to produce
cryptographically secure random passwords.
"""
from __future__ import annotations

import secrets
import string

DEFAULT_LENGTH = 16
MIN_LENGTH = 4
MAX_LENGTH = 128


def _pick_char(pool: str) -> str:
    return secrets.choice(pool)


def generate_password(
    length: int = DEFAULT_LENGTH,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    """Generate a cryptographically secure random password.

    Args:
        length: Password length (default 16).
        use_uppercase: Include uppercase letters?
        use_lowercase: Include lowercase letters?
        use_digits: Include digits?
        use_symbols: Include symbols?

    Returns:
        The generated password.

    Raises:
        ValueError: Invalid length or character sets.
    """
    if length < MIN_LENGTH:
        raise ValueError(f"Password must be at least {MIN_LENGTH} characters.")
    if length > MAX_LENGTH:
        raise ValueError(f"Password can be at most {MAX_LENGTH} characters.")

    pools: list[str] = []
    if use_lowercase:
        pools.append(string.ascii_lowercase)
    if use_uppercase:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append(string.punctuation)

    if not pools:
        raise ValueError("At least one character set must be selected.")

    all_chars = "".join(pools)

    password_chars: list[str] = []

    for pool in pools:
        password_chars.append(_pick_char(pool))

    remaining = length - len(password_chars)
    password_chars.extend(secrets.choice(all_chars) for _ in range(remaining))

    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


def format_password_message(password: str, length: int) -> str:
    escaped = password.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f"🔑 <b>Random Password</b> ({length} characters)\n\n"
        f"<code>{escaped}</code>\n\n"
        f"⚠️ This password is shown only once. "
        f"Please copy it to a safe place."
    )
