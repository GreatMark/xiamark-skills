#!/usr/bin/env python3
"""
DeepSeek-OCR-2 本地调用工具
"""

import subprocess
import os
import sys
from pathlib import Path

MODEL_PATH = os.path.expanduser(
    "~/.lmstudio/models/mlx-community/DeepSeek-OCR-2-bf16"
)
PYTHON = "/opt/homebrew/bin/python3.13"


def ocr_image(image_path: str, max_tokens: int = 500, prompt: str = None) -> dict:
    """
    使用 DeepSeek-OCR 识别图片文字
    
    Args:
        image_path: 图片路径
        max_tokens: 最大输出 tokens
        prompt: 自定义 prompt
    
    Returns:
        dict: {text, tokens, speed, success}
    """
    
    if not Path(image_path).exists():
        return {"success": False, "error": f"图片不存在: {image_path}"}
    
    if not Path(MODEL_PATH).exists():
        return {"success": False, "error": "模型未下载，请在 LM Studio 中下载 mlx-community/DeepSeek-OCR-2-bf16"}
    
    default_prompt = "Read and output all text in this image exactly as written:"
    prompt = prompt or default_prompt
    
    cmd = [
        PYTHON, "-m", "mlx_vlm.generate",
        "--model", MODEL_PATH,
        "--image", image_path,
        "--max-tokens", str(max_tokens),
        "--prompt", prompt
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        output = result.stdout + result.stderr
        
        # 解析输出
        lines = output.split('\n')
        text_lines = []
        capture = False
        gen_tokens = 0
        speed = 0.0
        
        for line in lines:
            # 开始捕获文本
            if prompt.split(':')[0] in line:
                capture = True
                continue
            if capture:
                if "==========" in line or "Prompt:" in line:
                    break
                text_lines.append(line)
            # 提取统计信息
            if "Generation:" in line and "tokens-per-sec" in line:
                parts = line.split()
                gen_tokens = int(parts[1])
                speed = float(parts[3])
        
        return {
            "success": True,
            "text": '\n'.join(text_lines).strip(),
            "tokens": gen_tokens,
            "speed": speed,
            "image": image_path
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "OCR 超时"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """命令行入口"""
    
    if len(sys.argv) < 2:
        print("用法: python ocr.py <image_path> [max_tokens] [prompt]")
        print("")
        print("示例:")
        print("  python ocr.py screenshot.png")
        print("  python ocr.py doc.png 800")
        print("  python ocr.py code.png 500 'Extract the code:'")
        sys.exit(1)
    
    image_path = sys.argv[1]
    max_tokens = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    prompt = sys.argv[3] if len(sys.argv) > 3 else None
    
    print(f"🔍 识别: {image_path}")
    result = ocr_image(image_path, max_tokens, prompt)
    
    if result["success"]:
        print(f"✅ 完成 ({result['tokens']} tokens, {result['speed']:.1f} t/s)")
        print("-" * 50)
        print(result["text"])
        print("-" * 50)
    else:
        print(f"❌ 失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
