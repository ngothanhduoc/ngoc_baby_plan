# 🚀 HƯỚNG DẪN PUSH CONTENT LÊN GITHUB

## CÁCH 1: DÙNG SCRIPT (ĐƠN GIẢN NHẤT)

### Bước 1: Tạo GitHub Personal Access Token

1. Đăng nhập GitHub: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Token name: `ngocbaby-marketing`
4. Scopes: Chọn `repo` và `workflow`
5. Click "Generate token"
6. **Copy token ngay lập tức** (chỉ hiện 1 lần)

### Bước 2: Chạy script push

**A. Dùng script push_to_github.sh**

```bash
cd /root/.openclaw/workspace
bash scripts/push_to_github.sh
```

Khi được yêu cầu, paste GitHub token bạn vừa tạo.

**B. Dùng script git-clone-push.sh**

```bash
cd /root/.openclaw/workspace
bash scripts/git-clone-push.sh
```

Hoặc set token trước:

```bash
export GITHUB_TOKEN="your_token_here"
cd /root/.openclaw/workspace
bash scripts/git-clone-push.sh
```

---

## CÁCH 2: PUSH THỦ CÔNG

### Bước 1: Setup remote (chỉ lần đầu)

```bash
cd /root/.openclaw/workspace
git remote add origin https://github.com/ngothanhduoc/ngoc_baby_plan.git
```

### Bước 2: Push lên GitHub

**Với token:**

```bash
cd /root/.openclaw/workspace
git push https://ngothanhduoc:<YOUR_TOKEN>@github.com/ngothanhduoc/ngoc_baby_plan.git master
```

Thay `<YOUR_TOKEN>` bằng token bạn vừa tạo.

---

## CÁCH 3: DÙNG SSH (Nếu có SSH key)

### Bước 1: Thay đổi remote sang SSH

```bash
cd /root/.openclaw/workspace
git remote set-url origin git@github.com:ngothanhduoc/ngoc_baby_plan.git
```

### Bước 2: Push

```bash
git push -u origin master
```

---

## ✅ KIỂM TRA SAU KHI PUSH

Kiểm tra repo online:

https://github.com/ngothanhduoc/ngoc_baby_plan

Bạn sẽ thấy:
- README.md
- analysis/mom_baby_stores_analysis.md
- marketing/content_calendar_march_2026.md
- marketing/5_bat_dau_facebook_posts.md
- marketing/promo_plan_march_2026.md
- scripts/daily_tech_summary.py
- scripts/push_to_github.sh
- scripts/git-clone-push.sh

---

## 🔄 AUTO-COMMIT HÀNG TUẦN (OPTIONAL)

Nếu bạn muốn auto-commit hàng tuần:

### Tạo cron job

```bash
crontab -e
```

Thêm dòng:

```bash
0 2 * * 0 cd /root/.openclaw/workspace && /root/.openclaw/workspace/scripts/git-clone-push.sh >> /root/.openclaw/workspace/logs/git_push.log 2>&1
```

Lưu ý: Cần set `GITHUB_TOKEN` trong environment.

---

## 🤝 KHI CÓ THAY ĐỔI MỚI

Để push thay đổi mới:

```bash
cd /root/.openclaw/workspace
git add .
git commit -m "update: mô tả thay đổi"
git push origin master
```

Hoặc dùng script:

```bash
cd /root/.openclaw/workspace
bash scripts/git-clone-push.sh
```

---

## 🐶 TRỢ GIÚP TỪ KIKI

Nếu gặp vấn đề:
1. Kiểm tra token có đúng
2. Kiểm tra repo URL có đúng
3. Kiểm tra git status: `git status`

**Liên hệ KIKI** nếu cần trợ giúp! 🚀

---

**Lưu ý:**
- GitHub token chỉ hiện 1 lần, copy ngay lập tức
- Không chia sẻ token với ai
- Token có hạn sử dụng (tùy bạn chọn)
- Nếu token hết hạn, tạo token mới
