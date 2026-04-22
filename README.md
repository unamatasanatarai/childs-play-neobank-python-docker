# Child'sPay | Secure Financial Ledger

Child'sPay is a high-integrity, secure financial ledger application built to simulate core banking operations including authentication, account balance checking, and secure fund transfers. It demonstrates a robust, modern backend architecture alongside a clean, responsive frontend.

## 🚀 Key Features

* **Secure Authentication:** JWT-based user authentication and session management.
* **Financial Ledger Integrity:** Designed to ensure strict ACID compliance during transfers, maintaining accurate system-wide ledger balances without data race conditions.
* **Asynchronous Backend:** Built with FastAPI and Async SQLAlchemy for high performance and scalable concurrency.
* **RESTful API Design:** Clean and well-structured API endpoints for authentication and banking operations.
* **Responsive UI:** A lightweight, dependency-free vanilla JavaScript and HTML frontend styled with PicoCSS.
* **Containerized Deployment:** Fully Dockerized using `docker-compose` for seamless local setup and environment consistency.

## 🛠️ Technology Stack

**Backend:**
* [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework for APIs
* [PostgreSQL](https://www.postgresql.org/) - Robust relational database
* [SQLAlchemy (Asyncpg)](https://www.sqlalchemy.org/) - Asynchronous ORM for database interactions
* [Alembic](https://alembic.sqlalchemy.org/) - Database migration management
* [PyJWT](https://pyjwt.readthedocs.io/) - Secure token generation and validation
* [Pytest](https://docs.pytest.org/) - Testing framework

**Frontend:**
* HTML5 / CSS3 / Vanilla JavaScript
* [PicoCSS](https://picocss.com/) - Minimalist CSS framework

**Infrastructure:**
* [Docker & Docker Compose](https://www.docker.com/)

## 🏗️ Getting Started

### Prerequisites

Ensure you have Docker and Docker Compose installed on your local machine.

### Installation & Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/unamatasanatarai/childs-play-neobank-python-docker.git
   cd childs-play-neobank-python-docker
   ```

2. **Start the application:**
   The entire stack (API and Database) can be built, initialized, and seeded effortlessly using the provided Makefile setup routine:
   ```bash
   make setup
   ```
   
   *Alternative commands:*
   * `make up` - Starts the containers in the background.
   * `make stop` - Stops the running containers.
   * `make down` - Removes containers and networks.
   * `make logs` - Tails the API logs.

3. **Access the Application:**
   * **Web Interface:** Open `public/index.html` directly in your preferred web browser.
   * **API Documentation (Swagger UI):** Visit [http://localhost:8000/docs](http://localhost:8000/docs) to explore and interact with the backend API endpoints.

### Seed Data & Testing

The database is configured to automatically seed initial test data for demonstration purposes (e.g., 5 users, each with a starting balance of $100.00). 

**Demo Accounts:** 
* `user1@example.com` (Password: `password123`)
* `user2@example.com` (Password: `password123`)
* `user3@example.com` (Password: `password123`)
* `user4@example.com` (Password: `password123`)
* `user5@example.com` (Password: `password123`)

**Running Integrity Tests:**
To verify the ledger's integrity (ensuring the total system balance remains constant at 50,000 cents):
```bash
make test
```

## 📐 Architecture Overview

* **`app/auth/`**: Manages user models, JWT token creation, password hashing, and login endpoints.
* **`app/banking/`**: Contains the core business logic, defining accounts, executing transactions, and serving transfer endpoints.
* **`app/database.py`**: Configures the asynchronous PostgreSQL database engine and session lifecycle.
* **`public/`**: Hosts the client-side single-page application that consumes the REST API.
* **`tests/`**: Contains automated tests, particularly focusing on ledger consistency and transactional safety.

## 🔒 Security & Best Practices

* Passwords are securely hashed using `argon2` and never stored in plaintext.
* Protected API endpoints require Bearer JWT tokens for access.
* Database operations utilize transactions to prevent race conditions and ensure data anomalies do not occur during concurrent fund transfers.
