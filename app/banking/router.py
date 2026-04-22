from app.banking.service import execute_transfer
from app.banking.schemas import TransferRequest
from app.banking.models import Account
from app.auth.models import User
from app.auth.service import get_current_user
from app.database import get_db

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.get("/users")
async def list_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.id != current_user.id)
    result = await db.execute(query)
    users = result.scalars().all()
    return [{"id": str(u.id), "email": u.email} for u in users]


@router.get("/accounts")
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Account)
        .options(joinedload(Account.user))
        .where(Account.user_id != current_user.id)
    )

    result = await db.execute(query)
    accounts = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "display_name": f"{a.user.email} / {a.account_number}",
        }
        for a in accounts
    ]


@router.post("/transfer")
async def transfer_funds(
    payload: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await execute_transfer(
        db, current_user.id, payload.recipient_id, payload.amount
    )


@router.get("/account/balance")
async def get_balance(current_user: User = Depends(get_current_user)):
    return {
        "account_number": current_user.account.account_number,
        "balance": current_user.account.balance,
    }
