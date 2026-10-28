"""Hash Generator service.

Generates text hashes using various algorithms.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

import bcrypt
from argon2 import PasswordHasher as Argon2Hasher

_ARGON2 = Argon2Hasher()

_HEX_RE = re.compile(r"^[0-9a-f]+$")


def _data(text: str) -> bytes:
    return text.encode("utf-8")


def generate_md5(text: str) -> str:
    return hashlib.md5(_data(text)).hexdigest()


def generate_sha1(text: str) -> str:
    return hashlib.sha1(_data(text)).hexdigest()


def generate_sha256(text: str) -> str:
    return hashlib.sha256(_data(text)).hexdigest()


def generate_sha512(text: str) -> str:
    return hashlib.sha512(_data(text)).hexdigest()


def generate_bcrypt(text: str) -> str:
    return bcrypt.hashpw(_data(text), bcrypt.gensalt()).decode("utf-8")


def generate_argon2(text: str) -> str:
    return _ARGON2.hash(text)


@dataclass
class HashResult:
    md5: str
    sha1: str
    sha256: str
    sha512: str

    def format_message(self, text: str) -> str:
        lines = [
            f"🔐 <b>Hash Generator</b> — \"<code>{text[:64]}</code>\"\n",
            f"<b>MD5:</b>      <code>{self.md5}</code>",
            f"<b>SHA-1:</b>     <code>{self.sha1}</code>",
            f"<b>SHA-256:</b>   <code>{self.sha256}</code>",
            f"<b>SHA-512:</b>   <code>{self.sha512}</code>",
        ]
        return "\n".join(lines)


def generate_hashes(text: str) -> HashResult:
    """Compute the MD5, SHA-1, SHA-256 and SHA-512 hashes for the given text."""
    data = _data(text)
    return HashResult(
        md5=hashlib.md5(data).hexdigest(),
        sha1=hashlib.sha1(data).hexdigest(),
        sha256=hashlib.sha256(data).hexdigest(),
        sha512=hashlib.sha512(data).hexdigest(),
    )


def guess_hash_type(h: str) -> str | None:
    """Guess the type of the given hash value."""
    raw = h.strip()
    if raw.startswith("$2"):
        return "bcrypt"
    if raw.startswith("$argon2"):
        return "Argon2"
    if _HEX_RE.match(raw):
        n = len(raw)
        if n == 32:
            return "MD5"
        if n == 40:
            return "SHA-1"
        if n == 64:
            return "SHA-256"
        if n == 128:
            return "SHA-512"
    return None


@dataclass
class VerifyResult:
    is_match: bool
    algorithm: str | None


def verify_hash(plain_text: str, target_hash: str) -> VerifyResult:
    """Compute the hash of the given plain text and compare it with the target hash.

    Tries the MD5, SHA-1, SHA-256, SHA-512, bcrypt and argon2 algorithms.
    """
    raw_target = target_hash.strip()
    target = raw_target.lower()
    data = _data(plain_text)

    if raw_target.startswith("$2"):
        try:
            is_ok = bcrypt.checkpw(data, raw_target.encode("utf-8"))
            return VerifyResult(is_match=is_ok, algorithm="bcrypt")
        except Exception:
            return VerifyResult(is_match=False, algorithm=guess_hash_type(raw_target))

    if raw_target.startswith("$argon2"):
        try:
            _ARGON2.verify(raw_target, plain_text)
            return VerifyResult(is_match=True, algorithm="Argon2")
        except Exception:
            return VerifyResult(is_match=False, algorithm=guess_hash_type(raw_target))

    checks: list[tuple[str, str]] = [
        ("MD5", hashlib.md5(data).hexdigest()),
        ("SHA-1", hashlib.sha1(data).hexdigest()),
        ("SHA-256", hashlib.sha256(data).hexdigest()),
        ("SHA-512", hashlib.sha512(data).hexdigest()),
    ]

    for alg, computed in checks:
        if computed == target:
            return VerifyResult(is_match=True, algorithm=alg)

    return VerifyResult(is_match=False, algorithm=guess_hash_type(raw_target))
