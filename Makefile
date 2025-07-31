 # Claude - Nöbetçi Eczane Sistemi
# Docker container for the pharmacy display system

FROM ubuntu:22.04

# Metadata
LABEL maintainer="Claude Project Team <info@claude.com>"
LABEL version="2.0.0"
LABEL description="Modern nöbetçi eczane gösterge sistemi"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV QT_X11_NO_MITSHM=1
ENV DISPLAY=:0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    # PyQt5 dependencies
    python3-pyqt5 \
    python3-pyqt5.qtmultimedia \
    pyqt5-dev-tools \
    # System libraries
    libgl1-mesa-glx \
    libglib2.0-0 \
    libfontconfig1 \
    libx11-xcb1 \
    libxcb-glx0 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    # Audio/Video codecs
    libavcodec-extra \
    libavformat58 \
    libavutil56 \
    libswscale5 \
    # X11 and display
    xvfb \
    x11-utils \
    x11-xserver-utils \
    # Network tools
    wget \
    curl \
    # Cleanup in same layer
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -m -s /bin/bash eczane && \
    usermod -aG video eczane

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=eczane:eczane . .

# Create necessary directories
RUN mkdir -p /app/ads /app/logs /app/cache && \
    chown -R eczane:eczane /app

# Create startup script
RUN cat > /app/start.sh << 'EOF'
#!/bin/bash
set -e

# Function to handle graceful shutdown
cleanup() {
    echo "Shutting down Claude..."
    pkill -f python3 || true
    pkill -f Xvfb || true
    exit 0
}

trap cleanup SIGTERM SIGINT

# Check if running in headless mode
if [ "${HEADLESS:-false}" = "true" ]; then
    echo "Starting Xvfb for headless mode..."
    Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
    export DISPLAY=:99
    sleep 2
fi

# Validate configuration
echo "Validating configuration..."
python3 -c "from config import Config; errors = Config.validate_config(); print('Config OK' if not errors else f'Config errors: {errors}')"

# Start the application
echo "Starting Claude..."
cd /app
python3 main.py

# Keep the script running
wait
EOF

RUN chmod +x /app/start.sh

# Switch to application user
USER eczane

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Expose port for potential web interface
EXPOSE 8080

# Volume mounts
VOLUME ["/app/ads", "/app/logs", "/app/cache"]

# Default command
CMD ["/app/start.sh"]
