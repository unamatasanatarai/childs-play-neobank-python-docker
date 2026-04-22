from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.banking.models import Account, Transaction
from fastapi import HTTPException, status


async def execute_transfer(
    db: AsyncSession, sender_user_id: UUID, recipient_id: UUID, amount: int
):
    # 1. Get Account IDs and sort them to prevent deadlocks
    # We fetch the sender's account first
    sender_stmt = select(Account).where(Account.user_id == sender_user_id)
    sender_res = await db.execute(sender_stmt)
    sender_acc = sender_res.scalar_one_or_none()

    if not sender_acc:
        raise HTTPException(status_code=404, detail="Sender account not found")

    # 2. Prevent self-transfers
    if sender_acc.id == recipient_id:
        raise HTTPException(status_code=422, detail="Cannot transfer to self")

    # Sort IDs for locking order
    lock_ids = sorted([sender_acc.id, recipient_id])

    # 3. Start Atomic Transaction block
    try:
        # 4. Lock rows using FOR UPDATE
        # This blocks other transactions from touching these two accounts
        stmt = (
            select(Account)
            .where(Account.id.in_(lock_ids))
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        result = await db.execute(stmt)
        accounts = {acc.id: acc for acc in result.scalars().all()}

        if recipient_id not in accounts:
            raise HTTPException(status_code=404, detail="Recipient not found")

        sender = accounts[sender_acc.id]
        recipient = accounts[recipient_id]

        # 5. Business Logic Validation
        if sender.balance < amount:
            raise HTTPException(status_code=402, detail="Insufficient funds")

        # 6. Perform Updates
        sender.balance -= amount
        recipient.balance += amount

        # 7. Create Immutable Audit Log
        new_tx = Transaction(
            sender_account_id=sender.id,
            recipient_account_id=recipient.id,
            amount=amount,
            status="SUCCESS",
        )
        db.add(new_tx)

        # Commit happens automatically if this is called within a session.begin() block
        # or manually here:
        await db.commit()
        return new_tx

    except Exception as e:
        await db.rollback()
        raise e
