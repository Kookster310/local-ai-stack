from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from llama_cpp import Llama
from dotenv import load_dotenv
import os
import time
import json
from pathlib import Path

# Load environment variables from .env file in the server directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# ------------------------
# Model
# ------------------------

MODEL_PATH = os.getenv("MODEL_PATH", "/models/default.gguf")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please set MODEL_PATH in .env file.")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=3,              # Use 3 cores (leave 1 for system/FastAPI)
    n_batch=512,              # Batch processing
    use_mlock=True,           # Lock in RAM (you have 8GB)
    use_mmap=True,            # Memory-map the file
    verbose=False,
    n_gpu_layers=0,           # Pi 5 doesn't have GPU acceleration for llama.cpp
)

# ------------------------
# API Keys
# ------------------------
# Load API keys from environment variables
# Multiple keys can be specified as comma-separated values in .env file
def parse_api_keys(env_var: str) -> set[str]:
    """Parse comma-separated API keys from environment variable"""
    keys_str = os.getenv(env_var, "")
    if not keys_str:
        return set()
    # Split by comma, strip whitespace, and filter out empty strings
    return {key.strip() for key in keys_str.split(",") if key.strip()}

OPENAI_API_KEYS = parse_api_keys("OPENAI_API_KEYS")
OLLAMA_API_KEYS = parse_api_keys("OLLAMA_API_KEYS")

# ------------------------
# Authorization
# ------------------------
def require_api_key(valid_keys: set[str]):
    def _auth(x_api_key: str = Header(...)):
        if x_api_key not in valid_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")
    return _auth

# ------------------------
# FastAPI App
# ------------------------
app = FastAPI(title="Local Chatbot API")

# ------------------------
# AI Routers
# ------------------------
openai_router = APIRouter(
    prefix="/openai",
    dependencies=[Depends(require_api_key(OPENAI_API_KEYS))]
)

ollama_router = APIRouter(
    prefix="/ollama",
    dependencies=[Depends(require_api_key(OLLAMA_API_KEYS))]
)

# ------------------------
# OpenAI-compatible models
# ------------------------
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[Message]
    max_tokens: int = 256
    temperature: float = 0.7
    stream: bool = False

def generate_stream(prompt, max_tokens, temperature):
    """Generator function for streaming responses"""
    for token in llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        stop=["<end_of_turn>", "<start_of_turn>"],
        echo=False,
        repeat_penalty=1.1,
        stream=True  # Enable streaming from llama.cpp
    ):
        chunk = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "gemma-2-2b-it",
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "content": token["choices"][0]["text"]
                    },
                    "finish_reason": None
                }
            ]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
    
    # Send final chunk
    final_chunk = {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "gemma-2-2b-it",
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }
        ]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"

@openai_router.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest):
    # DEBUG: Log the incoming request
    print("=" * 50)
    print("RECEIVED REQUEST:")
    print(f"Model: {req.model}")
    print(f"Messages: {req.messages}")
    print(f"Max tokens: {req.max_tokens}")
    print(f"Temperature: {req.temperature}")
    print(f"Stream: {req.stream}")
    print("=" * 50)
    
    # Build proper Gemma chat template
    prompt = ""
    for msg in req.messages:
        if msg.role == "user":
            prompt += f"<start_of_turn>user\n{msg.content}<end_of_turn>\n"
        elif msg.role == "assistant":
            prompt += f"<start_of_turn>model\n{msg.content}<end_of_turn>\n"
        elif msg.role == "system":
            prompt += f"<start_of_turn>system\n{msg.content}<end_of_turn>\n"
    
    prompt += "<start_of_turn>model\n"
    
    # Handle streaming vs non-streaming
    if req.stream:
        print("STREAMING MODE ENABLED")
        return StreamingResponse(
            generate_stream(prompt, req.max_tokens, req.temperature),
            media_type="text/event-stream"
        )
    else:
        # Non-streaming response (for title generation, etc.)
        result = llm(
            prompt,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            stop=["<end_of_turn>", "<start_of_turn>"],
            echo=False,
            repeat_penalty=1.1,
        )
        
        content = result["choices"][0]["text"].strip()
        
        print(f"RESPONSE: {content}")
        
        if not content:
            content = "I apologize, but I couldn't generate a response."
        
        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model or "gemma-2-2b-it",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop",
                    "logprobs": None
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": len(content.split()),
                "total_tokens": 10 + len(content.split())
            },
            "system_fingerprint": None
        }
        
        print(f"RETURNING: {response}")
        print("=" * 50)
        
        return response

# ------------------------
# Ollama-compatible API
# ------------------------
class OllamaGenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: bool = False
    options: dict | None = None

@ollama_router.post("/api/generate")
def ollama_generate(req: OllamaGenerateRequest):
    result = llm(
        req.prompt,
        max_tokens=256,
        temperature=0.7,
    )

    return {
        "model": req.model,
        "created_at": "now",
        "response": result["choices"][0]["text"],
        "done": True
    }

# ------------------------
# Include AI routers
# ------------------------
app.include_router(openai_router)
app.include_router(ollama_router)