# IS601 Demo: FastAPI, SQLAlchemy, Service-Repository Pattern, and Docker

This project serves as a demonstration for IS601, illustrating the integration of several key technologies and design patterns common in modern web application development. It features a simple User Management System built with FastAPI, interacting with a PostgreSQL database via SQLAlchemy, and structured using the Service-Repository pattern. The entire application stack is containerized using Docker and Docker Compose for ease of setup and deployment.

## Core Concepts Demonstrated

1.  **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
    *   **Key Features Used:** Type Hinting for automatic data validation and documentation (Swagger UI/ReDoc), Dependency Injection, Asynchronous Support.
    *   **File:** [`main.py`](main.py)

2.  **SQLAlchemy**: A powerful and Pythonic SQL toolkit and Object Relational Mapper (ORM). It allows developers to interact with relational databases using Python objects instead of writing raw SQL.
    *   **Key Features Used:** Declarative Base for defining models, Session management for database transactions, Core API for database connection setup.
    *   **Files:** [`models.py`](models.py), [`database.py`](database.py), [`repositories.py`](repositories.py)

3.  **Service-Repository Pattern**: A design pattern used to separate concerns in an application's architecture.
    *   **Repository Layer**: Encapsulates the logic required to access data sources. It mediates between the domain and data mapping layers using a collection-like interface for accessing domain objects. Its primary goal is to abstract away the details of data storage (e.g., specific database queries).
        *   **File:** [`repositories.py`](repositories.py)
    *   **Service Layer**: Sits between the API/presentation layer and the repository layer. It encapsulates the application's business logic, orchestrating calls to repositories and other services to fulfill use cases. It keeps the API layer thin and focused on handling HTTP requests/responses.
        *   **File:** [`services.py`](services.py)
    *   **Benefits:** Improved maintainability, testability (layers can be tested independently), and separation of concerns.

4.  **Docker & Docker Compose**: Tools for containerizing applications and managing multi-container applications, respectively.
    *   **Dockerfile**: A text document that contains instructions for assembling a Docker image. It specifies the base image, dependencies, application code, and commands needed to run the application.
        *   **File:** [`Dockerfile`](Dockerfile)
    *   **Docker Compose**: A tool for defining and running multi-container Docker applications. It uses a YAML file (`docker-compose.yml`) to configure the application's services (e.g., web application, database, admin tool).
        *   **File:** [`docker-compose.yml`](docker-compose.yml)
    *   **Benefits:** Consistent development/testing/production environments, simplified dependency management, easy scaling and deployment.

5.  **Dependency Injection (FastAPI)**: FastAPI uses function parameter type hints to automatically provide dependencies (like database sessions or service instances) to API route functions. This promotes decoupling and makes testing easier.
    *   **Example:** The `get_db` dependency in [`main.py`](main.py) provides a database session to the route handlers.

6.  **Database Seeding (`seed.py`)**: A script using the `Faker` library to populate the database with realistic dummy data for development and testing purposes.
    *   **File:** [`seed.py`](seed.py)

7.  **Testing (`pytest`)**: Using `pytest` along with `httpx` (for API testing) and SQLAlchemy's session management for testing different layers of the application (API endpoints, repositories).
    *   **Directory:** [`tests/`](tests/)

8.  **Password Hashing (`passlib`)**: Using `passlib` with `bcrypt` to securely hash user passwords before storing them in the database.
    *   **File:** [`security.py`](security.py)

9.  **GitHub Actions (CI)**: Automated workflow to run tests using a PostgreSQL service container whenever code is pushed or a pull request is made.
    *   **File:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

## Project Structure

```
.                     # Project Root
├── .github/          # GitHub specific files
│   └── workflows/    # GitHub Actions workflows
│       └── ci.yml    # Continuous Integration workflow
├── tests/            # Automated tests
│   ├── __init__.py
│   ├── conftest.py   # Pytest configuration and fixtures
│   ├── test_main.py  # API endpoint tests
│   └── test_repositories.py # Repository layer tests
├── .gitignore        # Files/directories ignored by Git
├── database.py       # SQLAlchemy setup (engine, session)
├── Dockerfile        # Instructions to build the FastAPI app image
├── docker-compose.yml # Docker Compose configuration for services (app, db, pgadmin)
├── main.py           # FastAPI application entry point and API routes
├── models.py         # SQLAlchemy ORM models (database table definitions)
├── README.md         # This file
├── repositories.py   # Data access logic (Repository pattern)
├── requirements.txt  # Python dependencies
├── security.py       # Password hashing and verification utilities
├── seed.py           # Database seeding script
└── services.py       # Business logic (Service pattern)
```

## Getting Started with Docker

Docker and Docker Compose are required to run this project locally in a containerized environment that mirrors a typical deployment setup.

**Prerequisites:**
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.

**Key Docker Compose Commands:**

1.  **Build and Start Services:**
    *   Builds the images (if they don't exist or `Dockerfile` changed) and starts all services defined in `docker-compose.yml` (`web`, `db`, `pgadmin`) in the background (`-d`).
    ```bash
    docker compose up --build -d
    ```
    *   `--build`: Forces Docker to rebuild the image for the `web` service based on the `Dockerfile`.
    *   `-d`: Runs the containers in detached mode (in the background).

2.  **View Logs:**
    *   Shows the logs from all running services.
    ```bash
    docker compose logs
    ```
    *   To follow the logs in real-time:
    ```bash
    docker compose logs -f
    ```
    *   To view logs for a specific service (e.g., `web`):
    ```bash
    docker compose logs web
    ```

3.  **Run Commands Inside a Service Container:**
    *   Executes a command inside a running container. This is essential for running migrations, tests, or accessing a shell within the container.
    *   **Example: Run Pytest:**
        ```bash
        docker compose exec web python -m pytest
        ```
    *   **Example: Run Database Seeder:**
        ```bash
        docker compose exec web python seed.py
        ```
    *   **Example: Access a Bash Shell in the `web` container:**
        ```bash
        docker compose exec web /bin/bash
        ```
        (Type `exit` to leave the shell)

4.  **Stop Services:**
    *   Stops the running containers defined in `docker-compose.yml` but does *not* remove them.
    ```bash
    docker compose stop
    ```

5.  **Stop and Remove Services:**
    *   Stops *and* removes the containers, networks, and potentially volumes created by `docker compose up`.
    ```bash
    docker compose down
    ```
    *   To also remove volumes (like the database data): **Use with caution!**
    ```bash
    docker compose down -v
    ```

6.  **List Running Services:**
    *   Shows the containers managed by Docker Compose in the current project directory.
    ```bash
    docker compose ps
    ```

**Accessing Services:**

*   **FastAPI Application:** [http://localhost:8000](http://localhost:8000)
*   **FastAPI Auto-docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **pgAdmin (Database Admin Tool):** [http://localhost:5050](http://localhost:5050)
    *   Login with the credentials defined in `docker-compose.yml` (e.g., `pgadmin4@pgadmin.org` / `admin`).
    *   You'll need to add a server connection within pgAdmin:
        *   **Host name/address:** `db` (This is the service name from `docker-compose.yml`)
        *   **Port:** `5432`
        *   **Maintenance database:** `mydatabase`
        *   **Username:** `user`
        *   **Password:** `password`
        (These values come from the `environment` section of the `db` service in `docker-compose.yml`)

## Running Tests

Tests are run using `pytest` inside the `web` container:

```bash
docker compose exec web python -m pytest
```

This ensures tests run against the PostgreSQL database service managed by Docker Compose.
