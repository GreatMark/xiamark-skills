#!/usr/bin/env python3
"""
Memory 2.0 - 对话历史压缩工具
使用 DeepSeek-OCR-2 将文本压缩为 Vision Tokens
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
MODEL_PATH = os.path.expanduser("~/.lmstudio/models/mlx-community/DeepSeek-OCR-2-bf16")
PYTHON = "/opt/homebrew/bin/python3.13"
TEMP_DIR = Path("/tmp/memory-compress")
TEMP_DIR.mkdir(exist_ok=True)


def text_to_image(text: str, output_path: Path, width: int = 1200, font_size: int = 14) -> bool:
    """将文本渲染为高密度 PNG 图片"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ 需要安装 Pillow: pip install Pillow")
        return False
    
    # 计算行数和高度
    lines = []
    max_chars_per_line = width // (font_size // 2)  # 估算每行字符数
    
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            lines.append('')
            continue
        # 自动换行
        while len(paragraph) > max_chars_per_line:
            lines.append(paragraph[:max_chars_per_line])
            paragraph = paragraph[max_chars_per_line:]
        lines.append(paragraph)
    
    # 计算图片高度
    line_height = font_size + 4
    height = max(100, len(lines) * line_height + 40)
    
    # 创建图片
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
    
    # 绘制文本
    y = 20
    for line in lines:
        draw.text((20, y), line, fill='black', font=font)
        y += line_height
    
    # 保存
    img.save(output_path, 'PNG', optimize=True)
    return True


def ocr_image(image_path: Path, prompt: str = "Extract all text from this image.") -> dict:
    """使用 DeepSeek-OCR 识别图片"""
    cmd = [
        PYTHON, "-m", "mlx_vlm.generate",
        "--model", MODEL_PATH,
        "--image", str(image_path),
        "--max-tokens", "500",
        "--prompt", prompt
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    output = result.stdout + result.stderr
    
    # 解析输出
    lines = output.split('\n')
    text_lines = []
    capture = False
    prompt_tokens = 0
    gen_tokens = 0
    
    for line in lines:
        if "Prompt:" in line and "tokens-per-sec" in line:
            parts = line.split()
            prompt_tokens = int(parts[1])
        elif "Generation:" in line and "tokens-per-sec" in line:
            parts = line.split()
            gen_tokens = int(parts[1])
        elif capture and line.strip() and "==========" not in line:
            text_lines.append(line)
        elif prompt in line:
            capture = True
    
    return {
        "text": '\n'.join(text_lines),
        "prompt_tokens": prompt_tokens,
        "generation_tokens": gen_tokens,
        "image_path": str(image_path)
    }


def compress_memory(text: str, mode: str = "base") -> dict:
    """
    压缩记忆文本
    
    Modes:
    - tiny: 极简摘要 (~64 vision tokens)
    - small: 简短摘要 (~100 vision tokens)
    - base: 标准压缩 (~256 vision tokens)
    - large: 详细保留 (~400 vision tokens)
    """
    
    prompts = {
        "tiny": "Extract only the most critical facts from this text in 2-3 bullet points.",
        "small": "Summarize the key information in 5 bullet points.",
        "base": "Extract and organize all important information from this text.",
        "large": "Preserve all meaningful details from this conversation history."
    }
    
    prompt = prompts.get(mode, prompts["base"])
    
    # 统计原始 tokens (粗略估计: 1 token ≈ 4 字符英文 / 1.5 字符中文)
    orig_tokens = len(text) // 2  # 简单估算
    
    # 渲染为图片
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = TEMP_DIR / f"memory_{timestamp}.png"
    
    print(f"📝 原始文本: {len(text)} 字符, ~{orig_tokens} tokens")
    print(f"🎨 渲染图片: {image_path}")
    
    if not text_to_image(text, image_path):
        return {"error": "Failed to render image"}
    
    # OCR 压缩
    print(f"🔍 OCR 压缩 (mode: {mode})...")
    result = ocr_image(image_path, prompt)
    
    # 计算压缩比
    compressed_tokens = result["generation_tokens"]
    compression_ratio = orig_tokens / max(compressed_tokens, 1)
    
    result["original_chars"] = len(text)
    result["original_tokens_est"] = orig_tokens
    result["compression_ratio"] = round(compression_ratio, 1)
    result["mode"] = mode
    
    print(f"✅ 压缩完成!")
    print(f"   原始: ~{orig_tokens} tokens")
    print(f"   压缩后: {compressed_tokens} tokens")
    print(f"   压缩比: {compression_ratio:.1f}x")
    
    return result


def demo():
    """演示压缩效果"""
    
    # 模拟对话历史
    sample_conversation = """
用户: 帮我配置一下 OpenClaw 的模型
助手: 好的，我来帮你配置。首先需要添加 provider...

用户: 添加 DeepSeek 的 API
助手: 已添加 DeepSeek provider，包含 deepseek-chat 和 deepseek-reasoner 两个模型。

用户: 再加上 NVIDIA 的模型
助手: 已配置 NVIDIA provider，包含 Kimi K2.5、Llama 3.3 70B、DeepSeek R1 Distill 等模型。

用户: Google AI Studio 也要
助手: 已添加 Google AI Studio，包含 Gemini 3 Pro、Gemini 2.5 Flash 等 8 个模型。

用户: 现在有多少模型了？
助手: 总共 42 个模型，涵盖 6 个 provider：
- Google AI Studio: 8 个
- OpenAI/Codex: 7 个  
- xAI: 8 个
- NVIDIA: 15 个
- DeepSeek: 2 个
- Antigravity: 2 个

用户: 太棒了！
助手: 你的模型库非常豪华，可以根据不同任务选择最合适的模型。
"""
    
    print("=" * 60)
    print("🧠 Memory 2.0 压缩演示")
    print("=" * 60)
    
    result = compress_memory(sample_conversation, mode="base")
    
    print("\n📋 压缩后的记忆:")
    print("-" * 40)
    print(result.get("text", ""))
    print("-" * 40)
    
    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 从文件读取
        input_file = sys.argv[1]
        mode = sys.argv[2] if len(sys.argv) > 2 else "base"
        
        with open(input_file, 'r') as f:
            text = f.read()
        
        result = compress_memory(text, mode)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 运行演示
        demo()
