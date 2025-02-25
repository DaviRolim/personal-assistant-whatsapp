# Use official Python image as a base
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Copy preferences.json file
COPY preferences.json ./

# Install UV and install dependencies
RUN pip install uv && \
    uv pip install --system .

# Copy the application code
COPY app/ ./app

# Expose the port FastAPI runs on
EXPOSE 80

# Set the entrypoint to use uvicorn to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
