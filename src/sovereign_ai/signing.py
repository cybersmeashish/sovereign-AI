"""Signing primitives. HMAC-SHA256 (stdlib) for labs/tests; Ed25519 when
`cryptography` is installed. Production deployments should anchor keys in
KMS / an HSM inside the approved boundary."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any, Protocol


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Signer(Protocol):
    key_id: str
    def sign(self, data: bytes) -> str: ...
    def verify(self, data: bytes, signature: str) -> bool: ...


class HMACSigner:
    def __init__(self, key: bytes, key_id: str = "hmac-default") -> None:
        self._key, self.key_id = key, key_id

    def sign(self, data: bytes) -> str:
        return base64.b64encode(hmac.new(self._key, data, hashlib.sha256).digest()).decode()

    def verify(self, data: bytes, signature: str) -> bool:
        return hmac.compare_digest(self.sign(data), signature)


class Ed25519Signer:
    def __init__(self, private_key=None, public_key=None, key_id: str = "ed25519-default") -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        if private_key is None and public_key is None:
            private_key = Ed25519PrivateKey.generate()
        self._priv = private_key
        self._pub = public_key or private_key.public_key()
        self.key_id = key_id

    def sign(self, data: bytes) -> str:
        if self._priv is None:
            raise RuntimeError("verification-only signer")
        return base64.b64encode(self._priv.sign(data)).decode()

    def verify(self, data: bytes, signature: str) -> bool:
        from cryptography.exceptions import InvalidSignature
        try:
            self._pub.verify(base64.b64decode(signature), data); return True
        except (InvalidSignature, ValueError):
            return False
