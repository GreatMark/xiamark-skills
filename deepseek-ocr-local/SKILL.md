---
name: deepseek-ocr-local
description: "本地运行 DeepSeek-OCR-2 进行图片文字识别。通过 LM Studio 下载模型，使用 mlx-vlm 调用。适用于 OCR、文档识别、截图提取、隐私敏感场景。"
metadata:
  clawdbot:
    emoji: "👁️"
    requires:
      bins: ["python3"]
      python: ["mlx-vlm"]
    tags: ["ocr", "vision", "local-model", "mlx", "deepseek"]
license: MIT
---

# DeepSeek-OCR-2 本地调用指南

在 Apple Silicon Mac 上本地运行 DeepSeek-OCR-2 进行图片文字识别。

## 为什么用本地 OCR

- **隐私安全**: 数据不出本机
- **无限调用**: 不受 API 限制
- **低延迟**: 本地推理，~320 tokens/sec
- **离线可用**: 不需要网络

## 前置要求

### 1. 安装 LM Studio

```bash
brew install --cask lm-studio
```

或从 https://lmstudio.ai 下载

### 2. 下载模型

1. 打开 LM Studio
2. 搜索: `mlx-community/DeepSeek-OCR-2-bf16`
3. 点击下载 (~6.3GB)

模型路径: `~/.lmstudio/models/mlx-community/DeepSeek-OCR-2-bf16`

### 3. 启用 CLI

1. LM Studio → Developer 标签
2. 点击 "Enable CLI" 或 "Install CLI"

验证:
```bash
~/.lmstudio/bin/lms --version
~/.lmstudio/bin/lms ls  # 查看已下载模型
```

### 4. 安装 mlx-vlm

```bash
pip install mlx-vlm
```

## 使用方法

### 命令行调用

```bash
python -m mlx_vlm.generate \
  --model ~/.lmstudio/models/mlx-community/DeepSeek-OCR-2-bf16 \
  --image /path/to/image.png \
  --max-tokens 500 \
  --prompt "Read and extract all text from this image."
```

### Python 代码

```python
import subprocess
import os

def ocr_image(image_path: str, max_tokens: int = 500) -> str:
    """使用 DeepSeek-OCR 识别图片文字"""
    
    model_path = os.path.expanduser(
        "~/.lmstudio/models/mlx-community/DeepSeek-OCR-2-bf16"
    )
    
    cmd = [
        "python", "-m", "mlx_vlm.generate",
        "--model", model_path,
        "--image", image_path,
        "--max-tokens", str(max_tokens),
        "--prompt", "Read and output all text in this image exactly:"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    # 解析输出
    output = result.stdout + result.stderr
    lines = output.split('\n')
    text_lines = []
    capture = False
    
    for line in lines:
        if "exactly:" in line:
            capture = True
            continue
        if capture:
            if "==========" in line or "Prompt:" in line:
                break
            if line.strip():
                text_lines.append(line)
    
    return '\n'.join(text_lines)


# 使用示例
text = ocr_image("/path/to/screenshot.png")
print(text)
```

### Clawdbot 中调用

我可以直接帮你识别图片：

1. 发送图片给我
2. 我会用 DeepSeek-OCR 识别
3. 返回提取的文字

## Prompt 技巧

| 场景 | Prompt |
|------|--------|
| 精确提取 | `Read and output all text exactly as written:` |
| 表格识别 | `Extract the table data in markdown format:` |
| 代码识别 | `Extract the code from this screenshot:` |
| 中英混合 | `识别图片中的所有文字:` |
| 摘要模式 | `Summarize the key information from this image:` |

## 性能指标

在 Apple M3 Ultra 上测试:

| 指标 | 数值 |
|------|------|
| 推理速度 | ~320 tokens/sec |
| 内存占用 | ~8.4 GB |
| 模型大小 | 6.3 GB |
| 首次加载 | ~5 秒 |

## 常见问题

### Q: LM Studio 报 "Model type not supported"

A: LM Studio 不支持直接加载 DeepSeek-OCR-2，需要用 `mlx-vlm` 命令行调用。

### Q: 中文识别不准确

A: DeepSeek-OCR-2 对小字体中文识别有局限，建议：
- 使用较大字体的图片
- 提高图片分辨率
- 英文/代码效果更好

### Q: 如何批量处理

```bash
for img in *.png; do
  echo "=== $img ==="
  python -m mlx_vlm.generate \
    --model ~/.lmstudio/models/mlx-community/DeepSeek-OCR-2-bf16 \
    --image "$img" \
    --max-tokens 300 \
    --prompt "Extract text:"
done
```

## 与 LM Studio 集成

虽然 LM Studio 不能直接运行这个模型，但可以：

1. **用 LM Studio 管理下载** - 方便的 GUI 下载和更新
2. **用 mlx-vlm 运行** - 命令行调用

```bash
# 检查模型状态
~/.lmstudio/bin/lms ls | grep -i deepseek

# 调用 OCR
python -m mlx_vlm.generate --model ~/.lmstudio/models/mlx-community/DeepSeek-OCR-2-bf16 ...
```

## 相关资源

- [DeepSeek-OCR-2 HuggingFace](https://huggingface.co/mlx-community/DeepSeek-OCR-2-bf16)
- [mlx-vlm GitHub](https://github.com/ml-explore/mlx-vlm)
- [LM Studio](https://lmstudio.ai)
