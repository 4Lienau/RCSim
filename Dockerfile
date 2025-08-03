# Advanced Rubik's Cube Simulator - Production Docker Image
# Multi-stage build for optimized production image

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=latest

# Add metadata
LABEL maintainer="Rubik's Cube Simulator Team <dev@rcsim.org>"
LABEL org.opencontainers.image.title="Advanced Rubik's Cube Simulator"
LABEL org.opencontainers.image.description="Realistic 3D Rubik's Cube simulator with authentic solving algorithms"
LABEL org.opencontainers.image.url="https://github.com/your-username/rcsim"
LABEL org.opencontainers.image.source="https://github.com/your-username/rcsim"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.licenses="MIT"

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    cmake \
    pkg-config \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libegl1-mesa-dev \
    libgles2-mesa-dev \
    libx11-dev \
    libxext-dev \
    libxrandr-dev \
    libxcursor-dev \
    libxinerama-dev \
    libxi-dev \
    libxss-dev \
    libglib2.0-dev \
    libgtk-3-dev \
    libasound2-dev \
    libpulse-dev \
    libjack-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better cache layering
COPY requirements.txt .
COPY pyproject.toml .
COPY README.md .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir build && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY assets/ ./assets/ 2>/dev/null || true

# Build the package
RUN python -m build --wheel && \
    pip install --no-cache-dir dist/*.whl

# Production stage
FROM python:3.11-slim as production

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglu1-mesa \
    libegl1-mesa \
    libgles2-mesa \
    libx11-6 \
    libxext6 \
    libxrandr2 \
    libxcursor1 \
    libxinerama1 \
    libxi6 \
    libxss1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libpulse0 \
    xvfb \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r rcsim && useradd -r -g rcsim -s /bin/bash rcsim

# Set work directory
WORKDIR /app

# Copy built wheel from builder stage
COPY --from=builder /app/dist/*.whl /tmp/

# Install the application
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm /tmp/*.whl

# Copy assets if they exist
COPY --from=builder /app/assets/ ./assets/ 2>/dev/null || true

# Create directories and set permissions
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R rcsim:rcsim /app

# Switch to non-root user
USER rcsim

# Set environment variables
ENV RCSIM_DATA_DIR=/app/data
ENV RCSIM_LOG_DIR=/app/logs
ENV RCSIM_CONFIG_DIR=/app/config
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port for web interface (if implemented)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import rcsim; print('OK')" || exit 1

# Default command (headless mode)
CMD ["python", "-m", "rcsim", "--headless", "--web-interface"]

# Alternative commands for different modes:
# GUI mode: docker run rcsim python -m rcsim
# Benchmark: docker run rcsim python -m rcsim --benchmark
# Solver only: docker run rcsim python -m rcsim --solve-only