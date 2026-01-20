from llama_cpp import Llama

llm = Llama(model_path="/home/kookster/llama.cpp/models/gemma-2-2b-it-q4_k_m.gguf")
output = llm("Hello world!", max_tokens=20)
print(output)
