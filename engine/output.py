"""Writing the JSON files the website reads (docs/data/*.json).

If the environment variable ``SITE_PASSPHRASE`` is set (GitHub secret), every file is
encrypted with AES-256-GCM (key = PBKDF2-SHA256 of the passphrase). The website asks for
the passphrase once and decrypts in the browser (WebCrypto). Without the variable the
files are plain JSON.

Encrypted envelope::

    {"enc": "aes-256-gcm/pbkdf2-sha256", "iter": 200000,
     "salt": "<base64>", "iv": "<base64>", "data": "<base64 ciphertext+tag>"}
"""
from __future__ import annotations

import base64
import json
import math
import os
from pathlib import Path

from .config import SITE_DATA

PBKDF2_ITER = 200_000


def _clean_floats(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, 6)
    if isinstance(obj, dict):
        return {str(k): _clean_floats(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean_floats(v) for v in obj]
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if hasattr(obj, "item"):  # numpy scalar
        return _clean_floats(obj.item())
    return obj


def encrypt_payload(plaintext: bytes, passphrase: str) -> dict:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=PBKDF2_ITER).derive(passphrase.encode())
    ct = AESGCM(key).encrypt(iv, plaintext, None)
    b64 = lambda b: base64.b64encode(b).decode()
    return {"enc": "aes-256-gcm/pbkdf2-sha256", "iter": PBKDF2_ITER, "salt": b64(salt), "iv": b64(iv), "data": b64(ct)}


def decrypt_payload(env: dict, passphrase: str) -> bytes:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    d = base64.b64decode
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=d(env["salt"]), iterations=env["iter"]).derive(passphrase.encode())
    return AESGCM(key).decrypt(d(env["iv"]), d(env["data"]), None)


def write_site_json(name: str, obj, directory: Path = SITE_DATA) -> Path:
    """Write ``docs/data/<name>.json`` (encrypted when SITE_PASSPHRASE is set)."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (name if name.endswith(".json") else f"{name}.json")
    payload = json.dumps(_clean_floats(obj), ensure_ascii=False, separators=(",", ":"))
    passphrase = os.environ.get("SITE_PASSPHRASE", "")
    if passphrase:
        payload = json.dumps(encrypt_payload(payload.encode("utf-8"), passphrase))
    path.write_text(payload + "\n", encoding="utf-8")
    return path


def read_site_json(name: str, directory: Path = SITE_DATA):
    path = directory / (name if name.endswith(".json") else f"{name}.json")
    if not path.exists():
        return None
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, dict) and "enc" in obj:
        pw = os.environ.get("SITE_PASSPHRASE", "")
        if not pw:
            return None
        obj = json.loads(decrypt_payload(obj, pw))
    return obj
