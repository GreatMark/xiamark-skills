#!/usr/bin/env python3
"""
Memory 2.0 - 双层压缩方案
1. 对话历史 → 渲染 PNG
2. DeepSeek-OCR → 提取文字 (作为 Vision Tokens)
3. 可选: 用 LLM 生成摘要

核心价值: 长对话历史存储为图片，需要时用 OCR 读取
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

MODEL_PATH = os.path.expanduser("~/.lmstudio/models/mlx-community/DeepSeek-OCR-2-bf16")
PYTHON = "/opt/homebrew/bin/python3.13"
MEMORY_DIR = Path(os.path.expanduser("~/clawd/memory/vision"))
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def render_text_to_image(text: str, output_path: Path, 
                          width: int = 1200, font_size: int = 14) -> dict:
    """将文本渲染为高密度 PNG"""
    
    # 加载字体
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
    except:
        font = ImageFont.load_default()
    
    # 计算布局
    lines = []
    max_chars = width // (font_size // 2 + 2)
    
    for para in text.split('\n'):
        while len(para) > max_chars:
            lines.append(para[:max_chars])
            para = para[max_chars:]
        lines.append(para)
    
    line_height = font_size + 6
    height = len(lines) * line_height + 40
    
    # 渲染
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    y = 20
    for line in lines:
        draw.text((20, y), line, fill='black', font=font)
        y += line_height
    
    img.save(output_path, 'PNG', optimize=True)
    
    return {
        "path": str(output_path),
        "width": width,
        "height": height,
        "lines": len(lines),
        "chars": len(text)
    }


def ocr_extract(image_path: str) -> str:
    """用 DeepSeek-OCR 提取图片中的文字"""
    
    cmd = [
        PYTHON, "-m", "mlx_vlm.generate",
        "--model", MODEL_PATH,
        "--image", image_path,
        "--max-tokens", "1000",
        "--prompt", "Read and output all the text in this image exactly as written:"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    output = result.stdout + result.stderr
    
    # 提取文字
    lines = output.split('\n')
    text_lines = []
    capture = False
    
    for line in lines:
        if "exactly as written:" in line:
            capture = True
            continue
        if capture:
            if "==========" in line or "Prompt:" in line:
                break
            if line.strip():
                text_lines.append(line)
    
    return '\n'.join(text_lines)


def archive_conversation(text: str, label: str = None) -> dict:
    """
    归档对话到 Vision Memory
    
    返回:
    - image_path: 图片路径
    - token_estimate: 原始 token 估算
    - vision_tokens: 作为图片只需 ~256 vision tokens
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = label or timestamp
    image_path = MEMORY_DIR / f"{label}.png"
    
    # 渲染
    info = render_text_to_image(text, image_path)
    
    # 估算 tokens
    orig_tokens = len(text) // 2  # 粗略估算
    vision_tokens = 256  # Gemini/Claude 处理图片约用 256-400 tokens
    
    return {
        "label": label,
        "image_path": str(image_path),
        "original_chars": len(text),
        "original_tokens_est": orig_tokens,
        "vision_tokens": vision_tokens,
        "compression_ratio": round(orig_tokens / vision_tokens, 1),
        "recoverable": True  # 可以用 OCR 恢复原文
    }


def recall_memory(image_path: str) -> str:
    """从 Vision Memory 恢复对话"""
    return ocr_extract(image_path)


# ===== 演示 =====
if __name__ == "__main__":
    
    # 模拟长对话
    conversation = """
=== 对话记录 2026-02-01 ===

用户: 帮我配置 OpenClaw 的模型
助手: 好的，我来帮你配置多个 AI 模型 provider。

用户: 加上 NVIDIA 的模型
助手: 已配置 NVIDIA provider，包含:
- Kimi K2.5 (Moonshot)
- Llama 3.3 70B (Meta)
- DeepSeek R1 Distill 70B
- Llama 3.1 405B
- Phi-4 Multimodal

用户: DeepSeek 官方 API 也要
助手: 已添加 DeepSeek provider:
- deepseek-chat (V3)
- deepseek-reasoner (R1)

用户: Google AI Studio
助手: 配置完成，8 个 Gemini 模型:
- Gemini 3 Pro/Flash Preview
- Gemini 2.5 Pro/Flash
- Gemini 2.0 Flash/Lite

用户: 总共多少模型？
助手: 42 个云端模型 + 本地 DeepSeek-OCR-2

=== 关键配置 ===
主力: Claude Opus 4.5
Fallback: Gemini → GPT-5.2 → Kimi K2.5
本地: DeepSeek-OCR-2 (Memory 压缩)

=== 待办 ===
- Memory 2.0 压缩方案
- AI 客服延迟测试
"""
    
    print("=" * 60)
    print("🧠 Memory 2.0 - Vision Archive Demo")
    print("=" * 60)
    
    # 归档
    print("\n📦 归档对话...")
    result = archive_conversation(conversation, "session_20260201")
    
    print(f"   原始: ~{result['original_tokens_est']} tokens")
    print(f"   Vision: ~{result['vision_tokens']} tokens")
    print(f"   压缩比: {result['compression_ratio']}x")
    print(f"   图片: {result['image_path']}")
    
    # 恢复
    print("\n🔍 从 Vision Memory 恢复...")
    recovered = recall_memory(result['image_path'])
    print(f"   恢复了 {len(recovered)} 字符")
    print("\n📖 恢复的内容 (前 500 字符):")
    print("-" * 40)
    print(recovered[:500])
    print("-" * 40)
