"""Agento Docker configuration."""

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m agent && \
    usermod -aG docker agent
USER agent

# Mount volumes for persistence
VOLUME ["/app/memory", "/app/projects"]

ENTRYPOINT ["agento"]
CMD ["--help"]
