#!/usr/bin/env python3
import sys
import subprocess
import argparse
from mlx_lm import load, generate

# Configuration
MODEL_PATH = "/Users/markliu/.lmstudio/models/mlx-community/Qwen3-Coder-Next-bf16"

def run_local_model(prompt, max_tokens=2048, temp=0.7):
    """Run the local MLX model with the given prompt."""
    
    # Check if model exists
    import os
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model path not found: {MODEL_PATH}")
        sys.exit(1)

    print(f"Loading model from {MODEL_PATH}...", file=sys.stderr)
    
    # Load model (this might take a few seconds, MLX uses lazy loading so it's fast-ish)
    model, tokenizer = load(MODEL_PATH)
    
    print("Generating...", file=sys.stderr)
    
    # Generate
    response = generate(
        model, 
        tokenizer, 
        prompt=prompt, 
        max_tokens=max_tokens, 
        temp=temp,
        verbose=False 
    )
    
    print(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run local Qwen3 Coder via MLX")
    parser.add_argument("prompt", help="The prompt to send to the model")
    parser.add_argument("--max-tokens", type=int, default=2048, help="Max tokens to generate")
    
    args = parser.parse_args()
    
    run_local_model(args.prompt, args.max_tokens)
