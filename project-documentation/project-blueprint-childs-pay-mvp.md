# **Child’sPay – MVP Product Specification**

**Version:** 1.0
**Status:** Approved for Development
**Owner:** UnamataSanatarai

---

## 🎯 1. Executive Overview

**Child’sPay** is a closed-loop fintech demonstration platform designed to simulate **high-integrity peer-to-peer money transfers** within a controlled environment.

The MVP prioritizes:
* **Atomic data integrity (ACID compliance)**
* **Transfer safety and concurrency correctness**
* **Simplicity for demo usability**

**Strategic Goal:** Deliver a *“zero-error”* transactional system that behaves with the reliability of a tier-1 banking ledger while remaining lightweight and demo-friendly.

---

## 🧩 2. Product Scope

### ✅ In Scope (MVP)
* Internal user-to-user transfers (closed ecosystem)
* Real-time balance tracking
* Immutable transaction logging
* Secure authentication and authorization
* Deterministic concurrency handling

### ❌ Out of Scope (Post-MVP)
* External integrations (Stripe, Plaid, banks)
* Multi-currency support
* Fraud detection / AML systems
* Transaction reversals or admin overrides

---

## 🔐 3. Identity & Access Management

### Core Requirements
* Secure user registration and login
* Password hashing via **Argon2id**
* Token-based authentication (JWT or Secure Session)

### User Model
* Unique email per user
* Automatic account creation upon registration

### User Discovery
* **Endpoint:** `GET /users`
* **Privacy & Performance Rule:** This endpoint must only return `id` and `email` (or `display_name`). No sensitive metadata or balance information is to be exposed in discovery.

---

## 💰 4. Wallet & Ledger System

### Account Model
* One account per user (1:1 relationship)
* **Non-negative balance** enforced at the database level via unsigned constraints or check constraints.
* **Precision Standard:** All financial values are stored as **BIGINT** representing the smallest minor unit (e.g., cents). This eliminates floating-point rounding errors.

### Capabilities
* Real-time balance visibility
* Paginated transaction history (Incoming/Outgoing)

---

## 💸 5. Atomic Transfer Engine (Core of MVP)

### Execution Flow (Strict)
The system uses a pessimistic locking strategy to eliminate race conditions and double-spending.

1.  **Lock Rows:** Execute `SELECT ... FOR UPDATE` on the sender’s account row to block concurrent modifications.
2.  **Validate:** Ensure `balance >= amount`.
3.  **Debit:** Subtract `amount` from sender.
4.  **Credit:** Add `amount` to recipient.
5.  **Log:** Insert immutable record into `Transactions` table.
6.  **Commit:** Finalize the database transaction.

### Guarantees
* **No double-spending:** Concurrent requests for the same sender are serialized.
* **No partial updates:** The transaction fails entirely if any step fails.
* **Integrity:** `sender_balance + recipient_balance` remains constant throughout the operation.

---

## 🏗️ 6. Technical Architecture

| Layer | Responsibility |
| :--- | :--- |
| **Frontend** | UI, form handling, API consumption (Vanilla JS) |
| **Backend** | Auth, business logic, Atomic Transfer Engine |
| **Database** | PostgreSQL / MySQL (Enforcing ACID and Locking) |

---

## 🗄️ 7. Data Model

### Users
* `id`: UUID
* `email`: String (Unique)
* `password_hash`: String (Argon2id)
* `created_at`: Timestamp

### Accounts
* `id`: UUID
* `user_id`: UUID (FK)
* `balance`: **BIGINT** (Minor units, default 0, check balance >= 0)
* `account_number`: IBAN / String

### Transactions
* `id`: UUID
* `from_account_id`: UUID (FK)
* `to_account_id`: UUID (FK)
* `amount`: **BIGINT** (Minor units)
* `status`: Enum (SUCCESS, FAILED)
* `created_at`: Timestamp (Immutable)

---

## 🚦 8. API Specification

### Auth
* `POST /api/v1/auth/register`
* `POST /api/v1/auth/login`

### Banking
* `GET /api/v1/users`: Returns `[{id, email}, ...]`
* `GET /api/v1/account/balance`: Returns current balance in minor units.
* `GET /api/v1/account/transactions`: Returns history.
* `POST /api/v1/transfer`

**Transfer Payload:**
```json
{
  "recipient_id": "UUID",
  "amount": 5000 // Representing $50.00
}
```

---

## ⚠️ 9. Edge Cases & Validation Rules

* **Self-Transfer:** Blocked at the logic layer.
* **Non-Positive Amounts:** Reject if `amount <= 0`.
* **Concurrency:** Handled via `SELECT ... FOR UPDATE`.
* **Integrity:** Database-level check constraint on `balance` to prevent negative values.

---

## ✅ 10. Definition of Done

* Transfer engine passes concurrency/race-condition stress tests.
* All financial math uses integer-based minor units (**BIGINT**).
* User discovery is limited to non-sensitive identifiers.
* Registration successfully triggers atomic Account creation.