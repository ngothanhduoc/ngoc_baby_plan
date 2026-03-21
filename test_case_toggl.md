# 🧪 TOGGL AUTOMATION - TEST CASE

## 📅 TEST CASE NGÀY HÔM NAY (21/03/2026)

---

## 🎯 TEST CASE MỤC TIÊU

**Mục tiêu:** Test full flow Toggl Automation cho một ngày làm việc

**Test bao gồm:**
1. **START Task 1** (sáng 7:00 VN)
2. **STOP Task 1** (sáng 11:17 VN)
3. **START Task 2** (trưa 12:03 VN, random)
4. **STOP Task 2** (chiều 15:00 VN, khi tổng = 8h)

**Kết quả mong muốn:**
- Toggl timer hoạt động OK
- Git commit mỗi lần START/STOP
- Telegram notification gửi OK
- Không push lên GitHub (chỉ commit)

---

## ⏰ LỊCH TRÌNH TEST CASE

| Thời gian VN | Thời gian UTC | Hành động | Command |
|-------------|---------------|----------|---------|
| **7:00 Sáng** | 0:00 UTC | START Task 1 | `python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-morning` |
| **11:17 Sáng** | 4:17 UTC | STOP Task 1 | `python3 /root/.openclaw/workspace/scripts/toggl_automation.py stop-morning` |
| **12:03 Trưa** | 5:03 UTC | START Task 2 | `python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-afternoon` |
| **15:00 Chiều** | 8:00 UTC | STOP Task 2 | `python3 /root/.openclaw/workspace/scripts/toggl_automation.py check-total` |

---

## 📝 CHECKLIST TEST CASE

### 1. START Task 1 (7:00 Sáng)

**Expected:**
- [ ] Toggl timer start được
- [ ] Timer description: "Làm việc - Sáng"
- [ ] Git commit message: "feat: START Task 1 - Sáng"
- [ ] Telegram notification gửi: "🌅 Đã bấm timer buổi sáng! 7:00 sáng"
- [ ] Không push lên GitHub

**Test command:**
```bash
python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-morning
```

**Verify:**
- Check Toggl website: Timer đang chạy?
- Check Git: `git log -1` (có commit START Task 1?)
- Check Telegram: Nhận được tin nhắn?

---

### 2. STOP Task 1 (11:17 Sáng)

**Expected:**
- [ ] Toggl timer stop được
- [ ] Duration: ~4h17p (15300s)
- [ ] Git commit message: "feat: STOP Task 1 - Sáng"
- [ ] Telegram notification gửi: "☕ Đã nghỉ trưa! Sáng làm việc xong."
- [ ] Không push lên GitHub

**Test command:**
```bash
python3 /root/.openclaw/workspace/scripts/toggl_automation.py stop-morning
```

**Verify:**
- Check Toggl website: Timer đã stop?
- Check Git: `git log -1` (có commit STOP Task 1?)
- Check Telegram: Nhận được tin nhắn?
- Check Toggl: Duration có đúng ~4h17p?

---

### 3. START Task 2 (12:03 Trưa, Random)

**Expected:**
- [ ] Toggl timer start được
- [ ] Timer description: "Làm việc - Chiều"
- [ ] Git commit message: "feat: START Task 2 - Chiều"
- [ ] Telegram notification gửi: "☀️ Đã bấm timer buổi chiều!"
- [ ] Không push lên GitHub

**Test command:**
```bash
python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-afternoon
```

**Verify:**
- Check Toggl website: Timer đang chạy?
- Check Git: `git log -1` (có commit START Task 2?)
- Check Telegram: Nhận được tin nhắn?
- Check Git: Commit message có "Random start 12:00-12:15"?

---

### 4. STOP Task 2 (15:00 Chiều, Tổng = 8h)

**Expected:**
- [ ] Toggl timer stop được
- [ ] Duration: ~3h57p (chiều)
- [ ] Total: ~7h59p52s (sáng + chiều)
- [ ] Git commit message: "feat: STOP Task 2 - Chiều"
- [ ] Telegram notification gửi: "🎉 Hoàn thành làm việc hôm nay!"
- [ ] Không push lên GitHub

**Test command:**
```bash
python3 /root/.openclaw/workspace/scripts/toggl_automation.py check-total
```

**Verify:**
- Check Toggl website: Timer đã stop?
- Check Git: `git log -1` (có commit STOP Task 2?)
- Check Telegram: Nhận được tin nhắn?
- Check Toggl: Tổng thời gian hôm nay có ~7h59p52s?

---

## 📊 KPI TEST CASE

| Step | Success Criteria |
|------|-----------------|
| START Task 1 | Timer start OK, Git commit OK, Telegram OK |
| STOP Task 1 | Timer stop OK, Duration ~4h17p, Git commit OK, Telegram OK |
| START Task 2 | Timer start OK, Git commit OK, Telegram OK |
| STOP Task 2 | Timer stop OK, Total ~7h59p52s, Git commit OK, Telegram OK |

---

## 🔍 VERIFY COMMANDS

### Check Git Logs
```bash
cd /root/.openclaw/workspace
git log --oneline -4
```

**Expected:**
```
feat: STOP Task 2 - Chiều
feat: START Task 2 - Chiều
feat: STOP Task 1 - Sáng
feat: START Task 1 - Sáng
```

### Check Git Status
```bash
cd /root/.openclaw/workspace
git status
```

**Expected:**
```
On branch master
nothing to commit, working tree clean
```

(Nếu có uncommitted files → OK, không push thì không sao)

### Check Toggl Website
1. Đăng nhập: https://track.toggl.com
2. Check Timer dashboard
3. Verify Time entries hôm nay:
   - Entry 1: "Làm việc - Sáng" (4h17p)
   - Entry 2: "Làm việc - Chiều" (3h57p)
   - Total: ~7h59p52s

### Check Telegram Messages
- Message 1: "🌅 Đã bấm timer buổi sáng! 7:00 sáng"
- Message 2: "☕ Đã nghỉ trưa! Sáng làm việc xong."
- Message 3: "☀️ Đã bấm timer buổi chiều!"
- Message 4: "🎉 Hoàn thành làm việc hôm nay!"

---

## 🚀 TEST CASE FLOW

### Step 1: START Task 1 (7:00 Sáng)
**Run:** `python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-morning`

**Verify:**
- [ ] Toggl website: Timer running?
- [ ] Git: Commit "START Task 1 - Sáng"?
- [ ] Telegram: Message received?

### Step 2: Wait ~4h17p
**Do công việc thực tế**

### Step 3: STOP Task 1 (11:17 Sáng)
**Run:** `python3 /root/.openclaw/workspace/scripts/toggl_automation.py stop-morning`

**Verify:**
- [ ] Toggl website: Timer stopped?
- [ ] Git: Commit "STOP Task 1 - Sáng"?
- [ ] Telegram: Message received?
- [ ] Toggl: Duration ~4h17p?

### Step 4: START Task 2 (12:03 Trưa)
**Run:** `python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-afternoon`

**Verify:**
- [ ] Toggl website: Timer running?
- [ ] Git: Commit "START Task 2 - Chiều"?
- [ ] Telegram: Message received?

### Step 5: Wait ~3h57p
**Do công việc thực tế**

### Step 6: STOP Task 2 (15:00 Chiều)
**Run:** `python3 /root/.openclaw/workspace/scripts/toggl_automation.py check-total`

**Verify:**
- [ ] Toggl website: Timer stopped?
- [ ] Git: Commit "STOP Task 2 - Chiều"?
- [ ] Telegram: Message received?
- [ ] Toggl: Total ~7h59p52s?

---

## ✅ TEST CASE SUCCESS CRITERIA

**Test case PASS khi:**
1. ✅ Tất cả 4 steps đều success
2. ✅ Toggl timer hoạt động đúng (start/stop)
3. ✅ Git commit OK cho mỗi step
4. ✅ Telegram notification OK cho mỗi step
5. ✅ Không push lên GitHub
6. ✅ Tổng thời gian: ~7h59p50s-7h59p55s

**Test case FAIL khi:**
1. ❌ Toggl API error (401, 500, v.v.)
2. ❌ Git commit error
3. ❌ Telegram notification error
4. ❌ Timer không start/stop được
5. ❌ Tổng thời gian vượt 8h

---

## 📝 TEST CASE NOTES

**Date:** 21/03/2026
**Tester:** Được Được
**Assistant:** KIKI
**Environment:**
- OS: Ubuntu 24.04
- Python: 3.12
- Git: 2.45.2
- Toggl API: v9 (Basic Auth)

---

## 🎯 TEST CASE RESULT

**Result:** PENDING

**Notes:**
- [ ] Test case chưa chạy
- [ ] Đợi user chạy test case
- [ ] Sau khi test → Cập nhật result

---

**Created by:** KIKI 🐶
**Date:** 2026-03-21 14:57 UTC (21:57 VN)
