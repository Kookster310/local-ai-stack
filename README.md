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
   - `MODEL_PATH`: Path to your model file (e.g., `/models/gemma-2-2b-it.q4_k_m.gguf`)
   - `OPENAI_API_KEYS`: Comma-separated list of API keys for OpenAI endpoint
   - `OLLAMA_API_KEYS`: Comma-separated list of API keys for Ollama endpoint

   Set up LibreChat environment:
   ```bash
   cp LibreChat/.env.example LibreChat/.env
   ```
   
   Edit `LibreChat/.env` and configure according to [LibreChat documentation](https://www.librechat.ai/docs/configuration/dotenv).
   
   Important: Configure LibreChat to use your local AI server by setting the OpenAI endpoint to `http://ai-server:8000/openai` in the LibreChat configuration.

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

See [LibreChat documentation](https://www.librechat.ai/docs/configuration/dotenv) for full configuration options.

To connect LibreChat to your local AI server, configure the OpenAI endpoint in LibreChat's settings to use:
- Base URL: `http://ai-server:8000/openai`
- API Key: Use one of the keys from `OPENAI_API_KEYS` in `server/.env`

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
