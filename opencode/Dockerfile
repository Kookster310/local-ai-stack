FROM node:22-bookworm-slim

# Install OpenCode globally
RUN npm i -g opencode-ai@latest

# Create non-root user for security
RUN useradd -m -s /bin/bash opencode

# Set up config directory
RUN mkdir -p /home/opencode/.opencode && chown -R opencode:opencode /home/opencode

USER opencode
WORKDIR /workspace

# Default command - can be overridden
ENTRYPOINT ["opencode"]
