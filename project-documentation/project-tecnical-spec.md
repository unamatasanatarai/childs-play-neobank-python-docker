## 🏗️ 1. Technical Stack

To ensure performance, type safety, and ACID compliance, the following stack is mandated:

* **Language:** Python 3.12+
* **Framework:** **FastAPI** (Chosen for high-performance async support and native OpenAPI documentation).
* **Database:** **PostgreSQL** (Required for robust row-level locking and atomic transactions).
* **ORM:** **SQLAlchemy 2.0 (Async)** (For precise control over `SELECT ... FOR UPDATE` statements).
* **Security:** `argon2-cffi` for password hashing and `PyJWT` for session management.
* **Validation:** `Pydantic v2` for strict schema enforcement.

---

## 🗄️ 2. Database Schema (DDL)

The schema enforces data integrity through check constraints and foreign keys. All monetary values are stored as `BIGINT` representing the smallest minor unit (e.g., 1000 = $10.00).

```sql
-- Initial Schema Migration
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE accounts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    balance BIGINT NOT NULL DEFAULT 0 CHECK (balance >= 0),
    account_number VARCHAR(34) UNIQUE NOT NULL,
    version INT DEFAULT 1 -- For optimistic locking support if needed
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    sender_account_id UUID REFERENCES accounts(id),
    recipient_account_id UUID REFERENCES accounts(id),
    amount BIGINT NOT NULL CHECK (amount > 0),
    status VARCHAR(20) NOT NULL, -- 'SUCCESS', 'FAILED'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 💸 3. The Transfer Engine (Logic Flow)

The Python implementation must handle database transactions strictly to prevent race conditions. The core logic utilizes a **Pessimistic Locking** strategy.

### **Concurrency Handling Protocol**
To avoid deadlocks, the system must lock account rows in a consistent order (e.g., always lock the account with the smaller UUID first).

1.  **Open Transaction:** Start an `async with session.begin():` block.
2.  **Lock Rows:** 
```python
# Lock sender and recipient rows to prevent concurrent balance changes
# ids should be pre-sorted: ids = sorted([sender_id, recipient_id])
stmt = select(Account).where(Account.id.in_(ids)).with_for_update()
result = await session.execute(stmt)
```
3.  **Validate:** Check if the sender has sufficient funds.
4.  **Execute Update:** * `sender.balance -= amount`
    * `recipient.balance += amount`
5.  **Audit Log:** Create the `Transaction` record.
6.  **Commit:** Automatically happens when the context manager exits successfully.

---

## 🚦 4. API Specification

### **Authentication**
* `POST /auth/register`: Hashes password using Argon2id; creates a User and an associated Account record in a single transaction.
* `POST /auth/login`: Validates credentials and returns a JWT.

### **Banking Operations**
* `GET /users`: Returns `List[UserPublicSchema]` (limited to `id` and `email`).
* `GET /account/balance`: Returns the integer balance and a human-readable decimal string.
* `POST /transfer`: Accepts `recipient_id` and `amount` (as an integer).

---

## 🛡️ 5. Precision & Math
Floating-point math is strictly forbidden for financial calculations.
* **Input:** Users enter `10.50`.
* **Processing:** Backend receives `1050`.
* **Storage:** Database stores `1050`.
* **Formula for Integrity Check:** $$\sum \text{Accounts}_{initial} = \sum \text{Accounts}_{current}$$
    *(Total money in the closed loop must remain constant.)*

---

## 📅 6. Development Roadmap

### **Sprint 1: The Core (API & DB)**
* Initialize FastAPI project with Docker-compose (App + Postgres).
* Setup SQLAlchemy models and Alembic migrations.
* Implement Argon2id security utilities.

### **Sprint 2: Ledger & Transactions**
* Build the `POST /transfer` endpoint with `FOR UPDATE` locking.
* Implement global exception handlers for `InsufficientFunds` and `DatabaseError`.
* Write integration tests for the transfer engine.

### **Sprint 3: Discovery & History**
* Implement `GET /users` discovery with pagination.
* Build transaction history view with filtering (Sent vs. Received).

### **Sprint 4: Demo Frontend**
* Develop a Vanilla JS dashboard to interact with the Python API.
* Implement real-time balance updates.

---

## 🧪 7. Success Criteria for QA
1.  **Double-Spend Prevention:** Attempting to send \$100 twice when the balance is only \$100 must result in exactly one successful transaction.
2.  **Atomicity:** If the database crashes during step 4 of the transfer, the sender's balance must not be debited.
3.  **Zero Drift:** After 1,000 random transfers, the total sum of all balances must be identical to the starting sum.