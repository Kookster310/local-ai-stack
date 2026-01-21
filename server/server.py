from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from llama_cpp import Llama
from dotenv import load_dotenv
import os
import time
import json
import sys
from pathlib import Path

# Force unbuffered output for Docker logs
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Load environment variables from .env file in common locations
env_candidates = [
    Path("/app/.env"),  # Docker mounted path (highest priority)
    Path(__file__).parent / ".env",
    Path.cwd() / ".env",
]
env_loaded = False
for candidate in env_candidates:
    if candidate.exists():
        print(f"DEBUG: Loading .env from: {candidate}", flush=True)
        load_dotenv(dotenv_path=candidate, override=True)  # override=True ensures new values override old ones
        env_loaded = True
        break

if not env_loaded:
    print("DEBUG: No .env file found, using system environment variables", flush=True)
    load_dotenv(override=True)  # Load from system environment

# ------------------------
# Model
# ------------------------

def resolve_model_path(raw_path: str) -> str:
    path = Path(raw_path)
    if path.is_absolute():
        return str(path)

    candidates = [
        Path("/models") / path,
        Path("/app") / path,
        path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(Path("/models") / path)

# Get MODEL_PATH from environment
raw_model_path = os.getenv("MODEL_PATH", "default.gguf")
print(f"DEBUG: Raw MODEL_PATH from environment: {raw_model_path}", flush=True)
model_env_vars = [(k, v) for k, v in os.environ.items() if 'MODEL' in k]
print(f"DEBUG: All MODEL_PATH related env vars: {model_env_vars}", flush=True)

MODEL_PATH = resolve_model_path(raw_model_path)
print(f"DEBUG: Resolved MODEL_PATH: {MODEL_PATH}", flush=True)
print(f"DEBUG: MODEL_PATH exists: {os.path.exists(MODEL_PATH)}", flush=True)

if not os.path.exists(MODEL_PATH):
    error_msg = f"Model file not found at {MODEL_PATH}. Please set MODEL_PATH in .env file."
    print(f"ERROR: {error_msg}", flush=True)
    raise FileNotFoundError(error_msg)

# Print model file info for verification
model_stat = os.stat(MODEL_PATH)
print(f"DEBUG: Model file size: {model_stat.st_size / (1024*1024):.2f} MB", flush=True)
print(f"DEBUG: Model file modified: {time.ctime(model_stat.st_mtime)}", flush=True)
print(f"DEBUG: Model file path: {MODEL_PATH}", flush=True)

CHAT_FORMAT = os.getenv("CHAT_FORMAT", "chatml")
print(f"DEBUG: CHAT_FORMAT: {CHAT_FORMAT}", flush=True)

print(f"DEBUG: Loading model from: {MODEL_PATH}", flush=True)
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=8192,
    n_threads=12,              # Use 12 cores
    n_batch=512,              # Batch processing
    use_mlock=True,           # Lock in RAM
    use_mmap=True,            # Memory-map the file
    verbose=False,
    n_gpu_layers=0,           # Pi 5 doesn't have GPU acceleration for llama.cpp
    chat_format=CHAT_FORMAT,
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

@app.on_event("startup")
async def startup_event():
    """Log model information on startup"""
    print("=" * 60, flush=True)
    print("AI SERVER STARTUP", flush=True)
    print("=" * 60, flush=True)
    print(f"Model Path: {MODEL_PATH}", flush=True)
    print(f"Model Exists: {os.path.exists(MODEL_PATH)}", flush=True)
    if os.path.exists(MODEL_PATH):
        model_stat = os.stat(MODEL_PATH)
        print(f"Model Size: {model_stat.st_size / (1024*1024):.2f} MB", flush=True)
        print(f"Model Modified: {time.ctime(model_stat.st_mtime)}", flush=True)
    print(f"Chat Format: {CHAT_FORMAT}", flush=True)
    try:
        print(f"Context Size: {llm.n_ctx()}", flush=True)
    except:
        pass
    print("=" * 60, flush=True)

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
    max_tokens: int = 2048  # Increased default for longer responses
    temperature: float = 0.7
    stream: bool = False

HIDE_THOUGHTS = os.getenv("HIDE_THOUGHTS", "true").lower() in {"1", "true", "yes", "on"}

STOP_TOKENS = [
    "<end_of_turn>",
    "<start_of_turn>",
    "<|end|>",
    "<|start|>",
    "<|eot_id|>",
]

THINK_TAG_START = "<think>"
THINK_TAG_END = "</think>"
THOUGHT_PREFIXES = [
    "We need to",
    "We should",
    "We must",
    "The user",
    "Let's",
    "I will",
]

def strip_thoughts_after_answer(text: str) -> str:
    """Cut off reasoning if it appears after an answer."""
    for prefix in THOUGHT_PREFIXES:
        idx = text.find(prefix)
        if idx != -1:
            return text[:idx].rstrip()
    return text

def strip_thought_tags(text: str, in_think: bool) -> tuple[str, bool]:
    """Remove <think>...</think> blocks from text while streaming."""
    output = ""
    remaining = text
    while remaining:
        if in_think:
            end_idx = remaining.find(THINK_TAG_END)
            if end_idx == -1:
                return output, True
            remaining = remaining[end_idx + len(THINK_TAG_END):]
            in_think = False
            continue
        start_idx = remaining.find(THINK_TAG_START)
        if start_idx == -1:
            output += remaining
            break
        output += remaining[:start_idx]
        remaining = remaining[start_idx + len(THINK_TAG_START):]
        in_think = True
    return output, in_think

def truncate_thought_lines(text: str) -> str:
    """Remove trailing chain-of-thought style lines."""
    lines = text.splitlines()
    kept = []
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(prefix) for prefix in THOUGHT_PREFIXES):
            break
        kept.append(line)
    if kept:
        return "\n".join(kept).strip()
    return text.strip()

def sanitize_output(text: str) -> str:
    cleaned = text
    for token in STOP_TOKENS:
        if token in cleaned:
            cleaned = cleaned.split(token, 1)[0]
    cleaned = cleaned.replace(THINK_TAG_START, "").replace(THINK_TAG_END, "")
    cleaned = truncate_thought_lines(cleaned)
    cleaned = strip_thoughts_after_answer(cleaned)
    return cleaned.strip()

def iter_stream_chunks(raw_text: str, buffer: str) -> tuple[str, str, bool]:
    buffer += raw_text

    for token in STOP_TOKENS:
        index = buffer.find(token)
        if index != -1:
            return buffer[:index], "", True

    safe_len = len(buffer)
    for token in STOP_TOKENS:
        for i in range(1, len(token)):
            if buffer.endswith(token[:i]):
                safe_len = min(safe_len, len(buffer) - i)
                break

    return buffer[:safe_len], buffer[safe_len:], False

def generate_stream(messages, max_tokens, temperature):
    """Generator function for streaming responses"""
    stream_id = f"chatcmpl-{int(time.time())}"
    finish_reason = None
    model_name = "local-ai"  # Model name doesn't matter, we use whatever is loaded
    in_think = False
    buffered = ""
    stop_stream = False
    
    try:
        for token in llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=STOP_TOKENS,
            stream=True,
        ):
            # Check if stream is finished
            if token.get("choices") and len(token["choices"]) > 0:
                choice = token["choices"][0]
                delta = choice.get("delta", {})
                finish_reason = choice.get("finish_reason")
                
                # Get content from delta
                content = delta.get("content", "")
                if content:
                    # If content begins to show reasoning, stop immediately
                    if any(prefix in content for prefix in THOUGHT_PREFIXES):
                        finish_reason = "stop"
                        stop_stream = True
                        break
                    # Strip <think>...</think> blocks while streaming
                    content, in_think = strip_thought_tags(content, in_think)
                    if not content:
                        continue
                    buffered += content

                    # If we detect chain-of-thought style prefixes, truncate and stop
                    for prefix in THOUGHT_PREFIXES:
                        marker = f"\n{prefix}"
                        if buffered.startswith(prefix) or marker in buffered:
                            cutoff = buffered.find(marker)
                            if cutoff == -1:
                                cutoff = 0
                            chunk_text = buffered[:cutoff].rstrip()
                            if chunk_text:
                                chunk = {
                                    "id": stream_id,
                                    "object": "chat.completion.chunk",
                                    "created": int(time.time()),
                                    "model": "local-ai",
                                    "choices": [
                                        {
                                            "index": 0,
                                            "delta": {"content": chunk_text},
                                            "finish_reason": None,
                                        }
                                    ],
                                }
                                yield f"data: {json.dumps(chunk)}\n\n"
                            finish_reason = "stop"
                            stop_stream = True
                            break
                    if stop_stream:
                        break

                    # Check for stop tokens in content
                    chunk_text = buffered
                    for stop_token in STOP_TOKENS:
                        if stop_token in chunk_text:
                            # Split at stop token and send everything before it
                            chunk_text = chunk_text.split(stop_token)[0]
                            finish_reason = "stop"
                            break
                    
                    # Send chunk if we have content
                    if chunk_text:
                        chunk = {
                            "id": stream_id,
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": "local-ai",
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {
                                        "content": chunk_text
                                    },
                                    "finish_reason": None
                                }
                            ]
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
                        buffered = ""
                
                # If finish_reason is set, break
                if finish_reason or stop_stream:
                    break
    
    except Exception as e:
        print(f"Error in streaming: {e}")
        finish_reason = "stop"
    
    # Send final chunk
    final_chunk = {
        "id": stream_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "local-ai",
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": finish_reason or "stop"
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
    
    messages = [{"role": msg.role, "content": msg.content} for msg in req.messages]
    if HIDE_THOUGHTS:
        # Prepend a system instruction to avoid chain-of-thought in outputs
        messages = [
            {
                "role": "system",
                "content": "Respond with the final answer only. Do not include reasoning or analysis.",
            }
        ] + messages
    
    # Handle streaming vs non-streaming
    # Note: Model name in request is ignored - we use whatever model is loaded
    if req.stream:
        print("STREAMING MODE ENABLED")
        return StreamingResponse(
            generate_stream(messages, req.max_tokens, req.temperature),
            media_type="text/event-stream"
        )
    else:
        # Non-streaming response (for title generation, etc.)
        result = llm.create_chat_completion(
            messages=messages,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            stop=STOP_TOKENS,
        )

        # Get content and handle finish_reason
        choice = result["choices"][0]
        content = sanitize_output(choice["message"]["content"])
        
        # Check if response was cut off due to max_tokens
        finish_reason = choice.get("finish_reason")
        if finish_reason == "length":
            print(f"WARNING: Response was truncated due to max_tokens limit ({req.max_tokens})")
            # Optionally append a note, but don't modify content as it might break things
        
        print(f"RESPONSE: {content}")
        
        if not content:
            content = "I apologize, but I couldn't generate a response."
        
        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model or "local-ai",
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
