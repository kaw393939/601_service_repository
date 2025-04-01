# Use an official Python runtime as a parent image
# Using python:3.11-slim provides a smaller base image than the full Python image
FROM python:3.11-slim

# Set the working directory in the container
# All subsequent commands (COPY, RUN, CMD) will be executed from this path
WORKDIR /app

# Copy the requirements file into the container at /app
# This is done before copying the rest of the code to leverage Docker's layer caching.
# If requirements.txt doesn't change, this layer won't be rebuilt, speeding up builds.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the pip cache, useful for keeping image size down.
# -r requirements.txt: Tells pip to install packages from the specified file.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents (build context) into the container at /app
# This includes our Python code (.py files), tests, etc.
# The .dockerignore file prevents unnecessary files from being copied.
COPY . .

# Make port 80 available to the world outside this container
# This informs Docker that the container listens on port 80, but doesn't actually publish it.
# Publishing is done in docker-compose.yml.
EXPOSE 80

# Define the command to run the application when the container launches
# Uses uvicorn, a fast ASGI server, recommended for FastAPI.
#   "main:app": Points to the 'app' instance in the 'main.py' file.
#   "--host", "0.0.0.0": Makes the server accessible from outside the container network.
#   "--port", "80": Tells uvicorn to listen on the port we exposed.
#   "--reload": Enables auto-reloading when code changes are detected (useful for development).
# Using the JSON array format is the preferred way to specify CMD instructions.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
