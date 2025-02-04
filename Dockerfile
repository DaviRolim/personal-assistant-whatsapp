# Use official Python image as a base
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Set environment variable to indicate Docker environment
ENV DOCKER_CONTAINER=1

# Install UV and other necessary dependencies
RUN pip install --no-cache-dir hatchling uv uvicorn fastapi openai pydantic[email] requests python-dotenv todoist-api-python google-auth google-api-python-client google-auth-oauthlib google-auth-httplib2 logging

# Copy dependency files
COPY pyproject.toml ./

# Create directory for tokens and set permissions
RUN mkdir -p /app/tokens && chmod 777 /app/tokens

# Copy the google-driver token
COPY drive_token.pickle /app/tokens/

# Install dependencies using UV
RUN uv sync

# Copy the application code
COPY app/ ./app

# Expose the port FastAPI runs on
EXPOSE 8000

# Set the entrypoint to use uvicorn to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
