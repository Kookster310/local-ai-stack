#!/usr/bin/env sh
set -eu

modelfiles_dir="/models/modelfiles"

if [ ! -d "$modelfiles_dir" ]; then
  echo "No modelfiles directory at ${modelfiles_dir}; nothing to create."
  exit 0
fi

echo "Waiting for Ollama API..."
until ollama list >/dev/null 2>&1; do
  sleep 1
done

for file in "$modelfiles_dir"/*.Modelfile; do
  if [ ! -e "$file" ]; then
    echo "No Modelfiles found in ${modelfiles_dir}; nothing to create."
    exit 0
  fi

  name="$(basename "$file" .Modelfile)"

  if ollama show "$name" >/dev/null 2>&1; then
    echo "Model ${name} already exists; skipping."
    continue
  fi

  echo "Creating model ${name} from ${file}"
  ollama create "$name" -f "$file"
done
