#!/bin/bash
# Auto-commit và push lên GitHub
# Dùng khi kết thúc một session làm việc

echo "🚀 Auto-commit & Push - KIKI Automation"
echo "======================================"
echo ""

cd /root/.openclaw/workspace

# Load GitHub token từ .env
if [ -f .env ]; then
    source .env
else
    echo "⚠️  Không tìm thấy file .env!"
    exit 1
fi

# Check có GITHUB_TOKEN không
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN không được thiết lập trong .env!"
    echo "Thêm vào .env:"
    echo "GITHUB_TOKEN=your_github_token_here"
    exit 1
fi

# Check git status
echo "📊 Git status:"
git status
echo ""

# Add tất cả thay đổi
echo "📝 Adding changes..."
git add .

# Commit
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
git commit -m "chore: auto-commit session - $TIMESTAMP

- Update workspace files
- Update task tracking (if any)
- Update logs (if any)" || echo "Không có thay đổi để commit"
echo ""

# Push lên GitHub
echo "📤 Pushing lên GitHub..."
REPO_URL="https://ngothanhduoc:${GITHUB_TOKEN}@github.com/ngothanhduoc/ngoc_baby_plan.git"
git push $REPO_URL master

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Push thành công!"
    echo "🌐 Repo: https://github.com/ngothanhduoc/ngoc_baby_plan"
else
    echo ""
    echo "❌ Push thất bại!"
    echo "Kiểm tra:"
    echo "- GitHub Token có đúng?"
    echo "- Repo URL có đúng?"
fi
