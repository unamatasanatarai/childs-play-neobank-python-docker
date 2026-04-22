import uuid
from datetime import datetime
from sqlalchemy import String, BigInteger, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,  # Reinforces 1:1 at the DB level
        nullable=False,
    )

    # balance is BIGINT to store minor units (e.g., cents)
    balance: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    account_number: Mapped[str] = mapped_column(String(34), unique=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="account")

    # DB-Level Constraints (The "Fail-Safe")
    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_balance_non_negative"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    sender_account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id"), nullable=False
    )
    recipient_account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id"), nullable=False
    )

    # amount in minor units
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="SUCCESS")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Ensure no zero or negative transfers
    __table_args__ = (CheckConstraint("amount > 0", name="check_positive_transfer"),)
