import hashlib
from typing import Union


def hash_sha256(data: Union[str, bytes], encoding: str = "utf-8") -> str:
    if isinstance(data, str):
        data = data.encode(encoding)
    if not isinstance(data, bytes):
        raise TypeError("Data must be of type str or bytes")
    hash = hashlib.sha256()
    hash.update(data)
    return hash.hexdigest()


def hash_sha256_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        hash = hashlib.file_digest(f, "sha256")
    return hash.hexdigest()
