import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.models import User
from app.banking.models import Account
from app.auth.schemas import UserCreate, UserPublic, UserLogin, Token
from app.auth.utils import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Check if user already exists
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # 2. Start an atomic transaction for User + Account creation
    try:
        # Create User object
        new_user = User(
            email=user_in.email, password_hash=hash_password(user_in.password)
        )
        db.add(new_user)
        await db.flush()  # Flush to get the new_user.id for the Account FK

        # Create associated Account (0 balance, demo account number)
        new_account = Account(
            user_id=new_user.id,
            balance=0,
            account_number=f"CHPAY-{uuid.uuid4().hex[:8].upper()}",
        )
        db.add(new_account)

        await db.commit()
        await db.refresh(new_user)
        return new_user

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete registration",
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    # 1. Fetch user by email
    query = select(User).where(User.email == credentials.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 2. Verify existence and password
    if not user or not verify_password(user.password_hash, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Generate JWT
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
