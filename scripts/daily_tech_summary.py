#!/usr/bin/env python3
"""
Daily Tech Summary Script
Chạy lúc 9h UTC+7 mỗi sáng để gửi tóm tắt tin công nghệ tới user
"""

import subprocess
import json
from datetime import datetime

# Cấu hình
TELEGRAM_CHAT_ID = "320491154"
GITHUB_API_URL = "https://api.github.com/search/repositories"

def send_message(message):
    """Gửi tin nhắn qua OpenClaw CLI"""
    cmd = [
        "openclaw", "message", "send",
        "--channel", "telegram",
        "--target", TELEGRAM_CHAT_ID,
        "--message", message
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Lỗi gửi tin nhắn: {e}")
        print(f"STDERR: {e.stderr}")
        return False

def get_github_trending():
    """Lấy GitHub trending (dùng search API với sort=stars)"""
    import requests

    # Tìm repo có nhiều sao nhất trong 7 ngày
    try:
        response = requests.get(
            f"{GITHUB_API_URL}?q=created:>2024-03-01&sort=stars&order=desc&per_page=5",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        trending = []
        for repo in data.get('items', [])[:5]:
            trending.append({
                'name': repo['full_name'],
                'stars': repo['stargazers_count'],
                'description': repo['description'] or 'Không có mô tả',
                'url': repo['html_url']
            })

        return trending
    except Exception as e:
        print(f"Lỗi lấy GitHub trending: {e}")
        return []

def format_summary(github_trending):
    """Định dạng tóm tắt tin tức"""
    today = datetime.now().strftime("%d/%m/%Y")
    summary = f"🌅 *Tóm tắt công nghệ ngày {today}*\n\n"

    # GitHub Trending
    summary += "🔥 *GitHub Trending:*"
    for i, repo in enumerate(github_trending, 1):
        summary += f"\n{i}. **{repo['name']}** ⭐ {repo['stars']}\n"
        summary += f"   {repo['description']}\n"
        summary += f"   {repo['url']}\n"

    summary += "\n💡 Tips lập trình nhanh:"
    summary += "\n- Dùng 'git rebase --interactive' để clean commit history"
    summary += "\n- Thử 'console.table()' thay vì 'console.log()' cho mảng đối tượng"

    summary += "\n📚 Kiến thức nhỏ:"
    summary += "\n- *Big O Notation* đo độ phức tạp thuật toán theo thời gian và không gian"

    summary += f"\n\n🐶 Gửi bởi KIKI lúc 9:00 AM"

    return summary

def main():
    print(f"🐶 KIKI: Bắt đầu tóm tắt tin công nghệ...")

    # Lấy GitHub trending
    github_trending = get_github_trending()

    # Format tin
    summary = format_summary(github_trending)
    print(f"Tin nhắn: {summary}")

    # Gửi tin
    if send_message(summary):
        print("✅ Đã gửi tin nhắn thành công!")
    else:
        print("❌ Gửi tin nhắn thất bại!")

if __name__ == "__main__":
    main()
