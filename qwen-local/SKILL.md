---
name: qwen-local
description: Run Qwen3 Coder Next locally on Apple Silicon via MLX. Use this for private code generation, large refactoring tasks, or when offline.
---

# Qwen Local Runner

Runs the local `Qwen3-Coder-Next-bf16` model using `mlx-lm`.

## Tools

### `ask_qwen_local`

Ask the local Qwen model a question or give it a coding task.

- **prompt**: The prompt/question for the model.
- **max_tokens**: Maximum number of tokens to generate (default: 2048).

```javascript
// Run the python script in the virtual environment
await cli.exec({
  command: `source ~/.openclaw/venv-mlx/bin/activate && python3 qwen_runner.py "${prompt.replace(/"/g, '\\"')}" --max-tokens ${max_tokens || 2048}`,
  cwd: __dirname
});
```
