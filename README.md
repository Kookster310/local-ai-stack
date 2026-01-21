# Local AI Stack

A complete local AI stack that runs AI models locally with OpenAI and Ollama compatible API endpoints, integrated with LibreChat frontend.

## Components

- **AI Server**: FastAPI server providing OpenAI and Ollama compatible endpoints using llama.cpp
- **LibreChat**: Modern chat interface for interacting with AI models
- **Models**: Directory for storing GGUF model files

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd local-ai-stack
   ```

2. **Set up environment variables**
   
   Copy the example environment file for the AI server:
   ```bash
   cp server/.env.example server/.env
   ```
   
   Edit `server/.env` and configure:
   - `MODEL_PATH`: Path to your model file (e.g., `/models/gemma-3-12b-it-Q4_K_M.gguf`)
   - `OPENAI_API_KEYS`: API key for OpenAI endpoint (use the same key in `librechat.yaml` apiKey field)
   - `OLLAMA_API_KEYS`: API key for Ollama endpoint (optional)
   
   **Important**: The API key in `server/.env` must match the `apiKey` in `librechat.yaml` (default: `local-ai-key`)

   Set up LibreChat environment:
   ```bash
   cp LibreChat/.env.example LibreChat/.env
   cp LibreChat/librechat.example.yaml LibreChat/librechat.yaml
   ```
   
   Edit `LibreChat/.env` and configure according to [LibreChat documentation](https://www.librechat.ai/docs/configuration/dotenv).
   
   The `librechat.yaml` file is pre-configured to connect to your local AI server. Model selection is hidden in the UI since only one model runs at a time.

3. **Add your model files**
   
   Place your `.gguf` model files in the `models/` directory. Update `MODEL_PATH` in `server/.env` to point to your model file.

4. **Start the stack**
   ```bash
   docker-compose up -d
   ```

5. **Access the services**
   - LibreChat: http://localhost:3080
   - AI Server API: http://localhost:8000
   - OpenAI endpoint: http://localhost:8000/openai/v1/chat/completions
   - Ollama endpoint: http://localhost:8000/ollama/api/generate

## Configuration

### AI Server Configuration (`server/.env`)

- `MODEL_PATH`: Path to the model file (use `/models/` prefix in Docker)
- `OPENAI_API_KEYS`: Comma-separated API keys for OpenAI endpoint authentication
- `OLLAMA_API_KEYS`: Comma-separated API keys for Ollama endpoint authentication

### LibreChat Configuration

LibreChat requires two configuration files:
- `LibreChat/.env`: Environment variables (see [LibreChat documentation](https://www.librechat.ai/docs/configuration/dotenv))
- `LibreChat/librechat.yaml`: YAML configuration file for endpoints and settings

The `librechat.yaml` is pre-configured to connect to your local AI server. The AI server accepts any model name in requests and uses whatever model is loaded (specified in `server/.env`).

See the [LibreChat YAML configuration documentation](https://www.librechat.ai/docs/configuration/librechat_yaml) for details on configuring endpoints.

## Directory Structure

```
local-ai-stack/
├── server/              # AI server code
│   ├── server.py       # FastAPI server
│   ├── Dockerfile      # Docker image for AI server
│   └── .env.example    # Example environment file
├── LibreChat/          # LibreChat frontend
├── llama.cpp/          # llama.cpp library (submodule)
├── models/             # Model files directory (add your .gguf files here)
├── docker-compose.yml  # Master orchestration file
└── requirements.txt    # Python dependencies
```

## API Usage

### OpenAI Compatible Endpoint

```bash
curl -X POST http://localhost:8000/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "model": "gemma-2-2b-it",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

### Ollama Compatible Endpoint

```bash
curl -X POST http://localhost:8000/ollama/api/generate \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -d '{
    "model": "gemma-2-2b-it",
    "prompt": "Hello!"
  }'
```

## Notes

- Model files are stored in the `models/` directory and are excluded from git (they're large files)
- The stack uses Docker networking, so services can communicate using service names (e.g., `ai-server`, `mongodb`)
