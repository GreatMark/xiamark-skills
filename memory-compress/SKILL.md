---
name: memory-compress
description: "Memory 2.0 压缩方案 - 使用 DeepSeek-OCR-2 将对话历史压缩为 Vision Tokens。将长文本渲染为图片，需要时用 OCR 恢复。适用于节省上下文 token、归档历史对话、实现双层记忆系统。"
metadata:
  clawdbot:
    emoji: "🧠"
    requires:
      bins: ["python3"]
      python: ["Pillow", "mlx-vlm"]
    tags: ["memory", "compression", "vision", "ocr", "local-model"]
license: MIT
---

# Memory 2.0 - Vision Token 压缩

使用 **DeepSeek-OCR-2** 将对话历史压缩为 Vision Tokens，实现高效的长期记忆存储。

## 为什么需要这个 Skill

- **节省 Token**: 长对话历史 (~3000 tokens) → 图片 (~256-400 vision tokens)
- **持久化存储**: 对话归档为 PNG 图片，永久保存
- **按需恢复**: 需要时用 OCR 提取原始内容
- **本地处理**: 隐私安全，不依赖云端

## 压缩模式

| 模式 | Vision Tokens | 准确度 | 压缩比 | 适用场景 |
|------|---------------|--------|--------|----------|
| Tiny | 64 | ⭐⭐ | ~50x | 极简摘要 |
| Small | 100 | ⭐⭐⭐ | ~30x | 快速回顾 |
| Base | 256 | ⭐⭐⭐⭐ | ~12x | 日常使用 |
| Large | 400 | ⭐⭐⭐⭐⭐ | ~8x | 重要对话 |

## 前置要求

1. **DeepSeek-OCR-2 模型**: 通过 LM Studio 下载
   - 搜索: `mlx-community/DeepSeek-OCR-2-bf16`
   - 路径: `~/.lmstudio/models/mlx-community/DeepSeek-OCR-2-bf16`

2. **Python 依赖**:
   ```bash
   pip install Pillow mlx-vlm
   ```

3. **Apple Silicon Mac**: 模型使用 MLX 优化

## 使用方法

### 归档对话

```python
from memory_compress import archive_conversation

result = archive_conversation(
    text="长对话内容...",
    label="session_20260201"
)
# 返回: {image_path, compression_ratio, ...}
```

### 恢复记忆

```python
from memory_compress import recall_memory

text = recall_memory("/path/to/memory.png")
# 返回: OCR 提取的文本
```

### 命令行

```bash
# 运行演示
python memory-compress.py

# 压缩文件
python memory-compress.py input.txt large
```

## 架构设计

```
┌─────────────────────────────────────────────┐
│  L1: Vision Memory (常驻上下文)              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │ Day 1   │  │ Day 2   │  │ Day 3   │      │
│  │ 256 tok │  │ 256 tok │  │ 256 tok │      │
│  └────┬────┘  └────┬────┘  └────┬────┘      │
│       │            │            │            │
│  ┌────▼────────────▼────────────▼────┐      │
│  │       DeepSeek-OCR 按需恢复        │      │
│  └────────────────────────────────────┘      │
│                                              │
│  L2: 原始文本 (存储在 memory/*.md)           │
└─────────────────────────────────────────────┘
```

## 性能指标

在 Apple M3 Ultra 上测试:
- OCR 速度: ~320 tokens/sec
- 内存占用: ~8.4 GB
- 中英文支持: ✅

## 注意事项

- DeepSeek-OCR-2 是 OCR 模型，不是 summarization 模型
- 对于摘要需求，建议 OCR 后再用 LLM 处理
- 图片渲染使用高密度排版以最大化信息密度
