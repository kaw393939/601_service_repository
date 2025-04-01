# Basic FastAPI Development Setup with Docker Compose

This project provides a minimal FastAPI application configured for development using Docker Compose.

## Features

*   Basic FastAPI app (`main.py`)
*   Docker containerization (`Dockerfile`)
*   Development environment with live reload using `docker-compose.yml`
*   Volume sharing for immediate code updates in the container.

## Prerequisites

*   Docker
*   Docker Compose

## Running the Application

1.  **Build and run the container:**

    ```bash
    docker-compose up --build
    ```

2.  **Access the application:**

    Open your web browser and go to `http://localhost:8000`

3.  **Access the API docs:**

    Open your web browser and go to `http://localhost:8000/docs`

## Development

*   Any changes made to the code in your local `main.py` file will automatically trigger a reload of the Uvicorn server inside the container thanks to the volume mount and the `--reload` flag.
*   Stop the containers using `Ctrl+C` in the terminal where `docker-compose up` is running, or by running `docker-compose down` in another terminal in the project directory.

## Running Tests

Tests are written using `pytest` and interact with the application via the `TestClient`.

1.  **Ensure dependencies are installed:** The test dependencies (`pytest`, `httpx`) need to be available. If you're running tests *outside* the Docker container, install them in your local environment:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run tests from the project root directory:**

    ```bash
    pytest
    ```

    Pytest will automatically discover the `tests` directory and run the tests found within.
