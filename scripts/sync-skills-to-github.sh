#!/bin/bash
# 同步本地技能到 GitHub 仓库
# 用法: ./sync-skills-to-github.sh [技能名称]

REPO_DIR="/tmp/xiamark-skills"
SKILLS_SOURCE="/Users/markliu/clawd/skills"
GITHUB_REPO="https://github.com/GreatMark/xiamark-skills.git"

# 要同步的技能列表（可以手动添加）
SKILLS_TO_SYNC=(
    "claude-code-runner"
)

# 如果传入了技能名称，添加到列表
if [ -n "$1" ]; then
    SKILLS_TO_SYNC+=("$1")
fi

echo "🔄 开始同步技能到 GitHub..."

# 克隆或更新仓库
if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR" && git pull origin main
else
    git clone "$GITHUB_REPO" "$REPO_DIR"
fi

cd "$REPO_DIR"

# 确保 skills 目录存在
mkdir -p skills

# 同步技能
for skill in "${SKILLS_TO_SYNC[@]}"; do
    if [ -d "$SKILLS_SOURCE/$skill" ]; then
        echo "📦 同步技能: $skill"
        rm -rf "skills/$skill"
        cp -r "$SKILLS_SOURCE/$skill" "skills/"
    else
        echo "⚠️ 技能不存在: $skill"
    fi
done

# 更新 README 中的技能列表
echo "📝 更新 README..."
cat > README.md << 'EOF'
# 小mark的AI技能库

这是我和 AI 助手 greatmark 在日常对话中积累的技能集合。

## 🎯 技能列表

| 技能 | 描述 |
|------|------|
EOF

# 自动生成技能列表
for skill_dir in skills/*/; do
    skill_name=$(basename "$skill_dir")
    if [ -f "$skill_dir/SKILL.md" ]; then
        # 从 SKILL.md 提取描述
        desc=$(grep -A1 "^description:" "$skill_dir/SKILL.md" | head -1 | sed 's/description: //' | cut -c1-60)
        echo "| [$skill_name](./skills/$skill_name/) | $desc... |" >> README.md
    fi
done

cat >> README.md << 'EOF'

## 📦 使用方式

这些技能可以在 OpenClaw 中使用。把 `skills/` 目录放到你的 OpenClaw workspace 即可。

## 🔧 技能格式

每个技能是一个文件夹，包含：
- `SKILL.md` - 核心指令文件
- `scripts/` - 可选：可执行脚本
- `references/` - 可选：参考文档
- `assets/` - 可选：静态资源

---

*由 小mark 和 greatmark 共同维护* ✨
EOF

# 提交并推送
git add .
if git diff --cached --quiet; then
    echo "✅ 没有变更需要同步"
else
    git commit -m "sync: 更新技能库 $(date '+%Y-%m-%d %H:%M')"
    git push origin main
    echo "✅ 同步完成！"
fi
