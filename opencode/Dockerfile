FROM node:22-bookworm-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    openssh-client \
    git \
    gosu \
    cron \
    sudo \
    # Network tools
    curl \
    wget \
    rsync \
    netcat-openbsd \
    iputils-ping \
    dnsutils \
    ca-certificates \
    # Data processing
    jq \
    gzip \
    tar \
    zip \
    unzip \
    xz-utils \
    # Text/file utilities
    vim-tiny \
    less \
    tree \
    file \
    # System utilities
    procps \
    htop \
    # Media tools
    ffmpeg \
    imagemagick \
    # Build tools (for compiling if needed)
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install OpenCode globally
RUN npm i -g opencode-ai@latest

# Create non-root user with sudo access for installing packages
RUN useradd -m -s /bin/bash opencode && \
    echo "opencode ALL=(ALL) NOPASSWD: /usr/bin/apt-get, /usr/bin/apt, /usr/bin/pip, /usr/bin/pip3" >> /etc/sudoers.d/opencode

# Set up config directories
RUN mkdir -p /home/opencode/.config/opencode \
    /home/opencode/.config/moltbook \
    && chown -R opencode:opencode /home/opencode

# Create workspace directories
RUN mkdir -p /workspace/skills \
    /workspace/credentials \
    /workspace/logs \
    /workspace/scripts \
    && chown -R opencode:opencode /workspace

# Copy configuration files
COPY --chown=opencode:opencode opencode.json /home/opencode/.config/opencode/opencode.json
COPY --chown=opencode:opencode AGENTS.md /workspace/AGENTS.md
COPY --chown=opencode:opencode hosts.yaml.example /workspace/hosts.yaml
COPY --chown=opencode:opencode SOUL.md.example /workspace/SOUL.md
COPY --chown=opencode:opencode skills/ /workspace/skills/

# Copy scripts
COPY --chown=opencode:opencode scripts/ /workspace/scripts/

# Make scripts executable
RUN chmod +x /workspace/scripts/*.sh

# Stay as root for entrypoint (it drops to opencode user)
WORKDIR /workspace

# Install Python dependencies for skills
RUN python3 -m venv /home/opencode/venv && \
    /home/opencode/venv/bin/pip install --no-cache-dir \
    paramiko \
    pyyaml \
    requests \
    google-auth \
    google-auth-oauthlib \
    google-api-python-client

# Add venv to PATH
ENV PATH="/home/opencode/venv/bin:$PATH"

# Default command - can be overridden
ENTRYPOINT ["opencode"]
