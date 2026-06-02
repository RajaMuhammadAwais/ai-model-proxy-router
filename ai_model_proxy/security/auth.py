import os
import hmac
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    raw_keys = os.getenv("PROXY_API_KEYS") or os.getenv("PROXY_MASTER_KEY")
    allowed_keys = [key.strip() for key in (raw_keys or "").split(",") if key.strip()]
    if api_key_header and any(hmac.compare_digest(api_key_header, key) for key in allowed_keys):
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )

def encrypt_key(key: str) -> str:
    # Placeholder for encryption logic (e.g., using cryptography library)
    return f"encrypted_{key}"

def decrypt_key(encrypted_key: str) -> str:
    # Placeholder for decryption logic
    return encrypted_key.replace("encrypted_", "")
