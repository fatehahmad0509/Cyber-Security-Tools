"""Base64 encode/decode service."""
from __future__ import annotations

import base64


def encode_bytes(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def decode_bytes(text: str) -> bytes:
    return base64.b64decode(text.encode("utf-8"))
