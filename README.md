<div align="center">
  <h1>💰 Child'sPay Neobank</h1>
  <p><em>A high-integrity, async financial ledger simulating core neobanking operations.</em></p>

  <!-- Badges -->
  <p>
    <a href="https://github.com/unamatasanatarai/childs-play-neobank-python-docker/issues"><img src="https://img.shields.io/github/issues/unamatasanatarai/childs-play-neobank-python-docker" alt="Issues"></a>
    <a href="https://github.com/unamatasanatarai/childs-play-neobank-python-docker/network/members"><img src="https://img.shields.io/github/forks/unamatasanatarai/childs-play-neobank-python-docker" alt="Forks"></a>
    <a href="https://github.com/unamatasanatarai/childs-play-neobank-python-docker/stargazers"><img src="https://img.shields.io/github/stars/unamatasanatarai/childs-play-neobank-python-docker" alt="Stars"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPL_v2.0-blue.svg" alt="License"></a>
    <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python 3.12">
    <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/PostgreSQL-16-336791.svg" alt="PostgreSQL">
  </p>
</div>

<hr />

## 📖 Overview

**Child'sPay** is an open-source, high-integrity financial ledger application. Designed to simulate core banking operations, it securely handles user authentication, real-time account balances, and concurrency-safe fund transfers. The project serves as an excellent reference implementation for building scalable, ACID-compliant fintech backends using modern Python.

Whether you're looking to integrate a robust microservice ledger, or learn about handling database race conditions with asynchronous SQL, Child'sPay provides a production-ready blueprint.

## ✨ Key Features

* 🔐 **Secure Authentication:** JWT-based stateless user authentication and session management. Passwords are computationally hashed using Argon2.
* 🛡️ **Financial Ledger Integrity:** Strict ACID compliance. Uses row-level locking (`SELECT ... FOR UPDATE`) to prevent double-spend anomalies and race conditions during concurrent fund transfers.
* ⚡ **High-Performance Async Backend:** Built from the ground up with **FastAPI** and **SQLAlchemy 2.0 (Asyncpg)** to handle thousands of concurrent transactions.
* 🧪 **Bulletproof Testing Suite:** Extensive end-to-end, integrity, and concurrency testing. All tests run safely against an ephemeral, auto-generated testing database.
* 📱 **Responsive UI Included:** Comes with a lightweight, dependency-free vanilla JavaScript frontend styled with PicoCSS.
* 🐳 **Fully Containerized:** Instantly reproducible environments using Docker and Docker Compose.

---

## 💻 Technology Stack

### Backend Engine
* **[FastAPI](https://fastapi.tiangolo.com/)**: Blazing fast web framework for APIs
* **[PostgreSQL 16](https://www.postgresql.org/)**: Robust, enterprise-grade relational database
* **[SQLAlchemy (Asyncpg)](https://www.sqlalchemy.org/)**: Asynchronous ORM handling connections
* **[Alembic](https://alembic.sqlalchemy.org/)**: Seamless database schema migrations
* **[PyJWT](https://pyjwt.readthedocs.io/) & [Argon2](https://argon2-cffi.readthedocs.io/)**: Industry-standard cryptographic security
* **[Pytest-Asyncio](https://pytest-asyncio.readthedocs.io/)**: Comprehensive asynchronous testing

### Frontend & Infrastructure
* **UI**: HTML5, CSS3, Vanilla JS, [PicoCSS](https://picocss.com/)
* **Ops**: Docker, Docker Compose, GNU Make

---

## 🚀 Getting Started

### Prerequisites
Before you begin, ensure you have the following installed on your machine:
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)
* `make` (Usually pre-installed on Linux/macOS)

### 1. Installation

Clone the repository and navigate into the project directory:
```bash
git clone https://github.com/unamatasanatarai/childs-play-neobank-python-docker.git
cd childs-play-neobank-python-docker
```

### 2. Launch the Application

Child'sPay comes with a comprehensive `Makefile` that handles building the containers, running database migrations, and injecting seed data. 

To fire everything up in one command, run:
```bash
make setup
```

*The API will be available at `http://localhost:8000`.*

### 3. Usage & Exploration

* **Web Application:** Open the `public/index.html` file in your preferred web browser to interact with the frontend.
* **Interactive API Docs:** Visit **[http://localhost:8000/docs](http://localhost:8000/docs)** to view the Swagger UI and test REST endpoints directly.

#### Demo Accounts
The `make setup` command automatically provisions 5 demo accounts. Each starts with a `$100.00` balance.
* **Emails:** `user1@example.com` through `user5@example.com`
* **Password:** `password123`

---

## 🛠️ Essential Commands

Manage the lifecycle of the application using `make`:

| Command | Description |
|---|---|
| `make up` | Starts the Docker containers in the background. |
| `make logs` | Tails the live output of the FastAPI backend logs. |
| `make test` | Rebuilds a temporary isolated database and runs the full Pytest suite (E2E & Concurrency). |
| `make stop` | Stops the running containers gracefully. |
| `make clean` | Tears down the containers and destroys the main database volume. |
| `make destroy` | **Nuke option:** Completely destroys all containers, volumes, cached layers, and local Python cache files. |

---

## 📄 License

This project is licensed under the GNU General Public License v2.0. See the [LICENSE](LICENSE) file for full details.

---
<div align="center">
  <p>Built with a 🧛.</p>
</div>
