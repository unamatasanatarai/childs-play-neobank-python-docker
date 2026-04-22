from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import uuid

from app.database import get_db
from app.config import settings
from app.auth.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Use JWT_SECRET (matching your config.py)
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        # Convert to UUID object to ensure DB compatibility
        user_id = uuid.UUID(user_id_str)

    except (JWTError, ValueError):
        raise credentials_exception

    # Eagerly load the account relationship to prevent MissingGreenlet error
    result = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.account))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user
