#!/bin/bash
# Script nhanh để push lên GitHub repo ngoc_baby_plan
# Sử dụng khi bạn đã có GitHub Personal Access Token

echo "🚀 Git Clone & Push - NgocBaby Plan"
echo "=================================="
echo ""

# Cấu hình
REPO_URL="https://github.com/ngothanhduoc/ngoc_baby_plan.git"
WORKSPACE="/root/.openclaw/workspace"

cd $WORKSPACE

# Check git status
echo "📊 Git status:"
git status
echo ""

# Pull từ remote (nếu có content)
echo "📥 Pulling từ remote..."
git pull origin master 2>/dev/null || echo "Remote chưa có content, sẽ push lần đầu"
echo ""

# Commit changes
echo "📝 Commit changes..."
git add .
git commit -m "update: $(date '+%Y-%m-%d %H:%M')" || echo "Không có thay đổi để commit"
echo ""

# Lấy token từ environment hoặc nhập
if [ -z "$GITHUB_TOKEN" ]; then
    read -sp "Nhập GitHub Personal Access Token: " TOKEN
    echo ""
else
    TOKEN=$GITHUB_TOKEN
fi

# Push lên GitHub
echo "📤 Pushing lên GitHub..."
git push https://ngothanhduoc:${TOKEN}@github.com/ngothanhduoc/ngoc_baby_plan.git master

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
    exit 1
fi
