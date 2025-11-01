# sofia/core/seguranca.py
import base64, hashlib, json
from pathlib import Path
from typing import Any, Union
from cryptography.fernet import Fernet

def _kdf_from_secret(secret: str) -> bytes:
    raw = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(raw)

def encrypt_json(obj: Any, secret: str) -> bytes:
    key = _kdf_from_secret(secret); f = Fernet(key)
    data = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return f.encrypt(data)

def decrypt_json(data: Union[bytes, bytearray], secret: str) -> Any:
    key = _kdf_from_secret(secret); f = Fernet(key)
    j = f.decrypt(data)
    return json.loads(j.decode("utf-8"))

def load_encrypted_json(path: Union[str, Path], secret: str) -> Any:
    path = Path(path); blob = path.read_bytes()
    return decrypt_json(blob, secret)
