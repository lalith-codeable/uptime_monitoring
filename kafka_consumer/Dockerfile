# Stage 1: Build stage
FROM python:3.13-slim AS builder

# Create and set working directory
WORKDIR /app

# Optimize Python behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip

# Copy the requirements file first (to leverage Docker caching)
COPY requirements.txt /app/

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.13-slim

# Create a non-root user and the /app directory
RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set the working directory to /app
WORKDIR /app

# Copy the rest of the application code into the container
COPY --chown=appuser:appuser . .

# Optimize Python runtime behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to the non-root user
USER appuser

# Optionally expose a port if your consumer exposes any endpoints (not needed for a background process)
# EXPOSE 8000

# Set the default command to run the consumer script
CMD ["python", "consumer.py"]
