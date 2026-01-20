#!/usr/bin/env python3
from llama_cpp import Llama
import time

models = [
    "gemma-2-2b-it.q4_k_m.gguf",
    "gemma-2-2b-it.q8_0.gguf"
]

prompt = "Hello world! Write a short paragraph about AI."

for m in models:
    print(f"\nTesting model: {m}")
    start = time.time()
    llm = Llama(model_path=f"/home/kookster/models/{m}")
    output = llm(prompt, max_tokens=50)
    end = time.time()
    print("Output:", output)
    print(f"Time taken: {end - start:.2f} sec")
