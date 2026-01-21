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
  printf 'FROM /models/%s\n' "$base" > "$modelfile"
  echo "Wrote ${modelfile}"
done

default_model="$(basename "${ggufs[0]}")"
default_model="${default_model%.gguf}"

update_default_model() {
  local file="$1"
  if [ ! -f "$file" ]; then
    return
  fi
  python - "$file" "$default_model" <<'PY'
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

echo "Done. Create a model with:"
echo "  docker compose up -d  # ollama-init will create models"
echo "  # or, if Ollama is already running:"
echo "  ollama create <name> -f ./models/modelfiles/<name>.Modelfile"
