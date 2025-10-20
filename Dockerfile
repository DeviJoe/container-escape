FROM python:3.11-slim

# Install system dependencies needed for container escape demos
RUN apt-get update && apt-get install -y \
    kmod \
    util-linux \
    procps \
    net-tools \
    iproute2 \
    libcap2-bin \
    gcc \
    make \
    linux-headers-generic \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create a non-root user (but we'll still have dangerous capabilities)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Add some environment variables for demonstration
ENV CONTAINER_ESCAPE_DEMO=true
ENV DANGEROUS_CAPABILITY=CAP_SYS_MODULE

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Start the vulnerable application
CMD ["python", "app.py"]
