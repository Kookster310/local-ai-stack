FROM node:22-bookworm-slim

# Install OpenCode globally
RUN npm i -g opencode-ai@latest

# Create non-root user for security
RUN useradd -m -s /bin/bash opencode

# Set up config directory (OpenCode uses ~/.config/opencode/)
RUN mkdir -p /home/opencode/.config/opencode && chown -R opencode:opencode /home/opencode

USER opencode
WORKDIR /workspace

# Default command - can be overridden
ENTRYPOINT ["opencode"]
