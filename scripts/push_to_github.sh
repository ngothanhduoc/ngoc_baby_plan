#!/bin/bash
# Script để push content lên GitHub repo ngoc_baby_plan
# Cần GitHub Personal Access Token để chạy

echo "🚀 Push content lên GitHub..."

cd /root/.openclaw/workspace

# Kiểm tra remote
if ! git remote | grep -q "origin"; then
    echo "Setting up remote..."
    git remote add origin https://github.com/ngothanhduoc/ngoc_baby_plan.git
fi

# Lấy thông tin token
echo "--------------------------------------------------"
echo "Cần GitHub Personal Access Token để push:"
echo "1. Đi đến: https://github.com/settings/tokens"
echo "2. Tạo token mới, chọn 'repo' và 'workflow'"
echo "3. Copy token"
echo "--------------------------------------------------"
read -sp "Nhập GitHub PAT (sẽ không hiển thị): " TOKEN
echo ""

# Push lên GitHub
echo "Pushing to GitHub..."
git push https://ngothanhduoc:${TOKEN}@github.com/ngothanhduoc/ngoc_baby_plan.git master

if [ $? -eq 0 ]; then
    echo "✅ Push thành công!"
    echo "Repo: https://github.com/ngothanhduoc/ngoc_baby_plan"
else
    echo "❌ Push thất bại! Kiểm tra token."
fi
