# Local AI Stack

A complete local AI stack that runs AI models locally with Ollama, integrated with the LibreChat frontend.

## Components

- **Ollama**: Model runtime and API (OpenAI-compatible)
- **LibreChat**: Modern chat interface for interacting with AI models
- **OpenClaw**: AI assistant gateway for multi-channel messaging
- **Models**: Directory for storing GGUF model files

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd local-ai-stack
   ```

2. **Set up environment variables**

   Set up LibreChat environment:
   ```bash
   cp LibreChat/.env.example LibreChat/.env
   cp LibreChat/librechat.example.yaml LibreChat/librechat.yaml
   ```
   
   Edit `LibreChat/.env` and configure according to [LibreChat documentation](https://www.librechat.ai/docs/configuration/dotenv).
   
   The `librechat.yaml` file is pre-configured to connect to your local Ollama instance.

3. **Add your model files**

   Place your `.gguf` model files in the `models/` directory. Ollama stores its model data in `models/ollama/` so everything stays under `models/`.

   Generate Modelfiles for every `.gguf` in `models/` (also updates LibreChat defaults):
   ```bash
   bash ./generate-ollama-modelfiles.sh
   ```

   Start the stack. The `ollama-init` service will create models from `models/modelfiles/`:
   ```bash
   docker-compose up -d
   ```

   If the stack is already running, re-run the init step:
   ```bash
   docker-compose up -d ollama-init
   ```

   If you have the Ollama CLI installed on the host, you can also run:
   ```bash
   ollama create my-model -f ./models/modelfiles/my-model.Modelfile
   ```

   If you update Modelfiles later, re-create the model:
   ```bash
   ollama rm my-model
   ollama create my-model -f ./models/modelfiles/my-model.Modelfile
   ```

4. **Start the stack**
   ```bash
   docker-compose up -d
   ```

5. **Access the services**
   - LibreChat: http://localhost:3080
   - Ollama API: http://localhost:11434
   - OpenAI-compatible endpoint: http://localhost:11434/v1/chat/completions
   - OpenClaw Gateway: http://localhost:18789

## Configuration

### LibreChat Configuration

LibreChat requires two configuration files:
- `LibreChat/.env`: Environment variables (see [LibreChat documentation](https://www.librechat.ai/docs/configuration/dotenv))
- `LibreChat/librechat.yaml`: YAML configuration file for endpoints and settings

The `librechat.yaml` is pre-configured to connect to your local Ollama instance. LibreChat fetches available models directly from Ollama, so once you create a model it will show up in the UI.

See the [LibreChat YAML configuration documentation](https://www.librechat.ai/docs/configuration/librechat_yaml) for details on configuring endpoints.

### OpenClaw Configuration

OpenClaw is an AI assistant gateway. Set the gateway token via environment variable:
```bash
export OPENCLAW_GATEWAY_TOKEN=your-secure-token
```

Or add to a `.env` file in the repo root. The gateway runs on port 18789 by default.

To use the OpenClaw CLI interactively:
```bash
docker compose run --rm openclaw-cli
```

Configuration and state are stored in `openclaw-data/`. See the [OpenClaw documentation](openclaw/docs/) for more details.

## Directory Structure

```
local-ai-stack/
├── LibreChat/          # LibreChat frontend
├── openclaw/           # OpenClaw AI gateway (submodule)
├── openclaw-data/      # OpenClaw config and workspace
├── llama.cpp/          # llama.cpp library (submodule)
├── models/             # Model files directory (add your .gguf files here)
├── docker-compose.yml  # Master orchestration file
└── scripts/            # Helper scripts (ollama-init, etc.)
```

## API Usage

### OpenAI Compatible Endpoint (Ollama)

```bash
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-2-2b-it",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

## Notes

- Model files are stored in the `models/` directory and are excluded from git (they're large files)
- The stack uses Docker networking, so services can communicate using service names (e.g., `ollama`, `mongodb`)
