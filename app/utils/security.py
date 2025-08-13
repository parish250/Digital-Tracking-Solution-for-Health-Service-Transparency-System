from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

# Use env vars in production
JWT_SECRET = "CHANGE_ME_SUPER_SECRET"       # e.g., os.getenv("JWT_SECRET")
JWT_ALG    = "HS256"
JWT_EXP_MIN = 60 * 24  # 24h

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(
    subject: str,
    claims: Optional[Dict[str, Any]] = None,
    expires_minutes: int = JWT_EXP_MIN
) -> str:
    to_encode = {"sub": subject, "iat": datetime.now(timezone.utc)}
    if claims:
        to_encode.update(claims)
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError as e:
        raise ValueError("Invalid token") from e
