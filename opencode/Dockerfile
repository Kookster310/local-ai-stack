FROM node:22-bookworm-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    openssh-client \
    git \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install OpenCode globally
RUN npm i -g opencode-ai@latest

# Create non-root user for security
RUN useradd -m -s /bin/bash opencode

# Set up config directory (OpenCode uses ~/.config/opencode/)
RUN mkdir -p /home/opencode/.config/opencode && chown -R opencode:opencode /home/opencode

# Create workspace directories
RUN mkdir -p /workspace/skills \
    /workspace/credentials \
    /workspace/logs \
    /workspace/cron \
    /workspace/scripts \
    && chown -R opencode:opencode /workspace

# Copy configuration files
COPY --chown=opencode:opencode opencode.json /home/opencode/.config/opencode/opencode.json
COPY --chown=opencode:opencode hosts.yaml /workspace/hosts.yaml
COPY --chown=opencode:opencode SOUL.md /workspace/SOUL.md
COPY --chown=opencode:opencode skills/ /workspace/skills/

USER opencode
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
