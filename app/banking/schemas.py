from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class TransferRequest(BaseModel):
    recipient_id: UUID
    # Amount is in minor units (cents).
    # We use Field(gt=0) to ensure transfers are always positive.
    amount: int = Field(
        ..., gt=0, description="Amount in minor units (e.g., 1000 for $10.00)"
    )

    @field_validator("amount")
    @classmethod
    def must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Transfer amount must be greater than zero")
        return v


class TransferResponse(BaseModel):
    transaction_id: UUID
    sender_id: UUID
    recipient_id: UUID
    amount: int
    new_balance: int
    status: str = "success"


class AccountBalanceResponse(BaseModel):
    account_number: str
    balance: int
