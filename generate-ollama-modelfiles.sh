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

echo "Done. Create a model with:"
echo "  docker compose up -d  # ollama-init will create models"
echo "  # or, if Ollama is already running:"
echo "  ollama create <name> -f ./models/modelfiles/<name>.Modelfile"
