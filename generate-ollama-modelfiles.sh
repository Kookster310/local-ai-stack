#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
models_dir="${repo_dir}/models"
out_dir="${models_dir}/modelfiles"

mkdir -p "$out_dir"

shopt -s nullglob
ggufs=("$models_dir"/*.gguf)

if [ ${#ggufs[@]} -eq 0 ]; then
  echo "No .gguf files found in ${models_dir}"
  exit 0
fi

for gguf in "${ggufs[@]}"; do
  base="$(basename "$gguf")"
  name="${base%.gguf}"
  modelfile="${out_dir}/${name}.Modelfile"
  cat > "$modelfile" <<'EOF'
FROM /models/GGUF_PLACEHOLDER

PARAMETER stop "<|start|>"
PARAMETER stop "<|endoftext|>"
PARAMETER stop "<|eot_id|>"
PARAMETER stop "</s>"
PARAMETER num_ctx 32768

# Template with tool calling support (Llama 3.1 style)
TEMPLATE """{{- if or .System .Tools }}<|start_header_id|>system<|end_header_id|>
{{- if .System }}
{{ .System }}
{{- end }}
{{- if .Tools }}

You are a helpful assistant with tool calling capabilities. When you receive a tool call response, use the output to format an answer to the original user question.
{{- end }}<|eot_id|>
{{- end }}
{{- range $i, $_ := .Messages }}
{{- $last := eq (len (slice $.Messages $i)) 1 }}
{{- if eq .Role "user" }}<|start_header_id|>user<|end_header_id|>
{{- if and $.Tools $last }}

Given the following functions, please respond with a JSON for a function call with its proper arguments that best answers the given prompt.
Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}. Do not use variables.

{{ range $.Tools }}
{{- . }}
{{ end }}
Question: {{ .Content }}<|eot_id|>
{{- else }}

{{ .Content }}<|eot_id|>
{{- end }}{{ if $last }}<|start_header_id|>assistant<|end_header_id|>

{{ end }}
{{- else if eq .Role "assistant" }}<|start_header_id|>assistant<|end_header_id|>
{{- if .ToolCalls }}
{{ range .ToolCalls }}
{"name": "{{ .Function.Name }}", "parameters": {{ .Function.Arguments }}}{{ end }}
{{- else }}

{{ .Content }}
{{- end }}{{ if not $last }}<|eot_id|>{{ end }}
{{- else if eq .Role "tool" }}<|start_header_id|>ipython<|end_header_id|>

{{ .Content }}<|eot_id|>{{ if $last }}<|start_header_id|>assistant<|end_header_id|}

{{ end }}
{{- end }}
{{- end }}"""
EOF
  # Replace the placeholder with actual filename
  sed -i "s|GGUF_PLACEHOLDER|${base}|g" "$modelfile"
  echo "Wrote ${modelfile}"
done

default_model="$(basename "${ggufs[0]}")"
default_model="${default_model%.gguf}"

update_default_model() {
  local file="$1"
  if [ ! -f "$file" ]; then
    return
  fi
  python3 - "$file" "$default_model" <<'PY'
import re
import sys

path = sys.argv[1]
model = sys.argv[2]

with open(path, "r", encoding="utf-8") as handle:
    content = handle.read()

pattern = r'(-\s*name:\s*"Ollama".*?\n)(\s*models:\s*\n)(\s*default:\s*\[)[^\]]*(\]\s*)'
match = re.search(pattern, content, flags=re.DOTALL)
if not match:
    print(f"Skipped {path}: Ollama endpoint not found", file=sys.stderr)
    sys.exit(0)

replacement = match.group(1) + match.group(2) + match.group(3) + model + match.group(4)
content = content[: match.start()] + replacement + content[match.end() :]

with open(path, "w", encoding="utf-8") as handle:
    handle.write(content)
print(f"Updated default model in {path} to {model}")
PY
}

update_default_model "${repo_dir}/LibreChat/librechat.yaml"
update_default_model "${repo_dir}/LibreChat/librechat.example.yaml"

# Update OpenCode config
update_opencode_model() {
  local file="$1"
  if [ ! -f "$file" ]; then
    return
  fi
  python3 - "$file" "$default_model" <<'PY'
import json
import sys

path = sys.argv[1]
model = sys.argv[2]

with open(path, "r", encoding="utf-8") as handle:
    config = json.load(handle)

# Ensure provider.ollama.models structure exists
if "provider" not in config:
    config["provider"] = {}
if "ollama" not in config["provider"]:
    config["provider"]["ollama"] = {
        "npm": "@ai-sdk/openai-compatible",
        "name": "Ollama (local)",
        "options": {"baseURL": "http://ollama:11434/v1"},
        "models": {}
    }
if "models" not in config["provider"]["ollama"]:
    config["provider"]["ollama"]["models"] = {}

# Add/update the model entry
config["provider"]["ollama"]["models"][model] = {
    "name": model,
    "limit": {"context": 32768, "output": 8192}
}

with open(path, "w", encoding="utf-8") as handle:
    json.dump(config, handle, indent=2)
print(f"Updated OpenCode model in {path} to {model}")
PY
}

update_opencode_model "${repo_dir}/opencode/opencode.json"

echo "Done. Create a model with:"
echo "  docker compose up -d  # ollama-init will create models"
echo "  # if the stack is already running:"
echo "  docker compose up -d ollama-init"
echo "  # or, if Ollama is already running:"
echo "  ollama create <name> -f ./models/modelfiles/<name>.Modelfile"
echo "  # to apply Modelfile updates:"
echo "  ollama rm <name> && ollama create <name> -f ./models/modelfiles/<name>.Modelfile"
