# 🧪 TOGGL AUTOMATION - TEST CASE (NEW LOGIC)

## 📅 TEST CASE NGÀY HÔM NAY (21/03/2026)

---

## 🎯 TEST CASE MỚI (NO CHECK LOOP)

**Mục tiêu:** Test flow Toggl Automation với calculate ngay stop time (không check liên tục)

**Test bao gồm:**
1. **START Task 1** (sáng 7:00 VN) → Calculate stop → Schedule with `at`
2. **STOP Task 1** (sáng 11:17 VN) → Triggered by `at`
3. **START Task 2** (trưa 12:03 VN, random) → Calculate stop → Schedule with `at`
4. **STOP Task 2** (chiều 15:47 VN) → Triggered by `at` (calculate dựa trên Task 1)

**Kết quả mong muốn:**
- Start → Calculate ngay stop time → Schedule với `at` → Done
- Stop trigger đúng giờ calculate
- Không cần check liên tục
- Git commit mỗi lần START/STOP
- Telegram notification mỗi lần START/STOP

---

## 🆕 LOGIC MỚI (NO CHECK LOOP)

### Task 1 (Sáng):
1. **Start:** 7:00 VN (0:00 UTC)
2. **Calculate ngay stop:**
   - Random duration: 4h15p-4h20p (15300-15600s)
   - VD: 4h17p32s (15352s)
   - Stop time = 7:00 + 4h17p32s = **11:17:32 VN** (4:17:32 UTC)
3. **Schedule stop với `at`:** Chạy đúng 4:17:32 UTC
4. **Khi stop trigger:**
   - Stop timer Toggl
   - Git commit "STOP Task 1"
   - Telegram notification

### Task 2 (Chiều):
1. **Start:** Random 12:00-12:15 VN (5:00-5:15 UTC)
   - VD: 12:03 VN (5:03 UTC)
2. **Calculate ngay stop:**
   - Target tổng: 7h59p55s (28795s)
   - Task 1 duration: 4h17p32s (15352s)
   - Task 2 duration: 28795s - 15352s = 13443s = 3h44p3s
   - Stop time = 12:03 + 3h44p3s = **15:47:03 VN** (8:47:03 UTC)
3. **Schedule stop với `at`:** Chạy đúng 8:47:03 UTC
4. **Khi stop trigger:**
   - Stop timer Toggl
   - Git commit "STOP Task 2"
   - Telegram notification

---

## ⏰ LỊCH TRÌNH TEST CASE

| Thời gian VN | Thời gian UTC | Hành động | Command |
|-------------|---------------|----------|---------|
| **7:00 Sáng** | 0:00 UTC | START Task 1 | `python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-morning` |
| **11:17:32 Sáng** | 4:17:32 UTC | STOP Task 1 | Triggered by `at` (không cần chạy thủ công) |
| **12:03 Trưa** | 5:03 UTC | START Task 2 | `python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-afternoon` |
| **15:47:03 Chiều** | 8:47:03 UTC | STOP Task 2 | Triggered by `at` (không cần chạy thủ công) |

---

## 📝 CHECKLIST TEST CASE

### 1. START Task 1 (7:00 Sáng)

**Expected:**
- [ ] Toggl timer start được
- [ ] Timer description: "Làm việc - Sáng"
- [ ] Calculate ngay stop time: 11:17:32 VN (4:17:32 UTC)
- [ ] Schedule stop với `at`: Chạy đúng 4:17:32 UTC
- [ ] Git commit message: "feat: START Task 1 - Sáng"
- [ ] Telegram notification gửi: "🌅 Đã bấm timer buổi sáng! 7:00 sáng"
- [ ] Có info stop time trong log
- [ ] Không push lên GitHub

**Test command:**
```bash
python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-morning
```

**Verify:**
- Check Toggl website: Timer đang chạy?
- Check Git: `git log -1` (có commit START Task 1?)
- Check Telegram: Nhận được tin nhắn?
- Check `at` jobs: `atq` (có job stop Task 1?)
- Check log file: Có info stop time không?

---

### 2. STOP Task 1 (11:17:32 Sáng - Triggered by `at`)

**Expected:**
- [ ] Toggl timer stop được (triggered by `at`)
- [ ] Duration: ~4h17p32s (15352s)
- [ ] Git commit message: "feat: STOP Task 1 - Sáng"
- [ ] Telegram notification gửi: "☕ Đã nghỉ trưa! Sáng làm việc xong."
- [ ] Không push lên GitHub
- [ ] `at` job removed sau khi chạy

**Verify:**
- Check Toggl website: Timer đã stop?
- Check Git: `git log -1` (có commit STOP Task 1?)
- Check Telegram: Nhận được tin nhắn?
- Check `at` jobs: Job stop Task 1 đã removed?
- Check log file: Có info STOP Task 1 không?
- Check Toggl: Duration có đúng ~4h17p32s?

---

### 3. START Task 2 (12:03 Trưa - Random)

**Expected:**
- [ ] Toggl timer start được
- [ ] Timer description: "Làm việc - Chiều"
- [ ] Calculate ngay stop time dựa trên Task 1: 15:47:03 VN (8:47:03 UTC)
- [ ] Schedule stop với `at`: Chạy đúng 8:47:03 UTC
- [ ] Git commit message: "feat: START Task 2 - Chiều"
- [ ] Telegram notification gửi: "☀️ Đã bấm timer buổi chiều!"
- [ ] Có info stop time trong log
- [ ] Không push lên GitHub

**Test command:**
```bash
python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-afternoon
```

**Verify:**
- Check Toggl website: Timer đang chạy?
- Check Git: `git log -1` (có commit START Task 2?)
- Check Telegram: Nhận được tin nhắn?
- Check `at` jobs: `atq` (có job stop Task 2?)
- Check log file: Có info stop time không?
- Check log: Có info Task 1 duration không?

---

### 4. STOP Task 2 (15:47:03 Chiều - Triggered by `at`)

**Expected:**
- [ ] Toggl timer stop được (triggered by `at`)
- [ ] Duration: ~3h44p3s (chiều)
- [ ] Total: ~7h59p35s (sáng + chiều)
- [ ] Git commit message: "feat: STOP Task 2 - Chiều"
- [ ] Telegram notification gửi: "🎉 Hoàn thành làm việc hôm nay!"
- [ ] Không push lên GitHub
- [ ] `at` job removed sau khi chạy

**Verify:**
- Check Toggl website: Timer đã stop?
- Check Git: `git log -1` (có commit STOP Task 2?)
- Check Telegram: Nhận được tin nhắn?
- Check `at` jobs: Job stop Task 2 đã removed?
- Check log file: Có info STOP Task 2 không?
- Check Toggl: Tổng thời gian hôm nay có đúng ~7h59p35s?
- Check Toggl: Tổng có trong 7h59p50s-7h59p55s?

---

## 📊 KPI TEST CASE

| Step | Success Criteria |
|------|-----------------|
| START Task 1 | Timer start OK, Calculate stop OK, Schedule `at` OK, Git commit OK, Telegram OK |
| STOP Task 1 | Timer stop OK (triggered by `at`), Duration ~4h17p32s, Git commit OK, Telegram OK |
| START Task 2 | Timer start OK, Calculate stop dựa trên Task 1 OK, Schedule `at` OK, Git commit OK, Telegram OK |
| STOP Task 2 | Timer stop OK (triggered by `at`), Duration ~3h44p3s, Total ~7h59p35s, Git commit OK, Telegram OK |

---

## 🔍 VERIFY COMMANDS

### Check `at` Jobs
```bash
atq
```

**Expected sau START Task 1:**
```
1  Fri Mar 21 04:17:32 2026 a root
```

**Expected sau START Task 2:**
```
1  Fri Mar 21 04:17:32 2026 a root
2  Fri Mar 21 08:47:03 2026 a root
```

**Expected sau STOP Task 1:**
```
2  Fri Mar 21 08:47:03 2026 a root
```

**Expected sau STOP Task 2:**
```
(No jobs)
```

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

### Check Toggl Website
1. Đăng nhập: https://track.toggl.com
2. Check Timer dashboard
3. Verify Time entries hôm nay:
   - Entry 1: "Làm việc - Sáng" (4h17p32s)
   - Entry 2: "Làm việc - Chiều" (3h44p3s)
   - **Total:** ~7h59p35s

### Check Telegram Messages
- Message 1: "🌅 Đã bấm timer buổi sáng! 7:00 sáng"
- Message 2: "☕ Đã nghỉ trưa! Sáng làm việc xong. Thời gian sáng: 4h17p"
- Message 3: "☀️ Đã bấm timer buổi chiều! Stop: 15:47:03 VN"
- Message 4: "🎉 Hoàn thành làm việc hôm nay! Tổng: 7h59p35s"

### Check Log Files
```bash
cat /root/.openclaw/workspace/logs/toggl_automation.log
```

**Expected:**
```
[2026-03-21 00:00:00] === BẮT ĐẦU LÀM VIỆC SÁNG ===
[2026-03-21 00:00:01] Đã bắt đầu timer: Làm việc - Sáng
[2026-03-21 00:00:02] Calculate stop time: 11:17:32 VN (4:17:32 UTC)
[2026-03-21 00:00:03] Schedule stop with 'at': Fri Mar 21 04:17:32 2026
[2026-03-21 04:17:33] === DỪNG LÀM VIỆC SÁNG ===
[2026-03-21 04:17:34] Đã dừng timer: Làm việc - Sáng (Thời gian: 4h17p32s)
[2026-03-21 05:03:00] === BẮT ĐẦU LÀM VIỆC CHIỀU ===
[2026-03-21 05:03:01] Đã bắt đầu timer: Làm việc - Chiều
[2026-03-21 05:03:02] Task 1 duration: 4h17p32s (15352s)
[2026-03-21 05:03:03] Target tổng: 7h59p55s (28795s)
[2026-03-21 05:03:04] Task 2 duration: 13443s (3h44p3s)
[2026-03-21 05:03:05] Calculate stop time: 15:47:03 VN (8:47:03 UTC)
[2026-03-21 05:03:06] Schedule stop with 'at': Fri Mar 21 08:47:03 2026
[2026-03-21 08:47:04] === STOP TASK 2 (TỔNG) ===
[2026-03-21 08:47:05] Tổng thời gian hôm nay: 7h59p35s (28795s)
[2026-03-21 08:47:06] Đã dừng timer: Làm việc - Chiều (Thời gian: 3h44p3s)
```

---

## 🚀 TEST CASE FLOW

### Step 1: START Task 1 (7:00 Sáng)
**Run:** `python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-morning`

**Verify:**
- [ ] Toggl website: Timer running?
- [ ] Git: Commit "START Task 1 - Sáng"?
- [ ] Telegram: Message received?
- [ ] `atq`: Có job stop Task 1 (04:17:32 UTC)?
- [ ] Log: Calculate stop time OK?
- [ ] Log: Schedule stop with 'at' OK?

### Step 2: Wait ~4h17p32s
**Do công việc thực tế**

### Step 3: STOP Task 1 (11:17:32 Sáng - Triggered by `at`)
**Verify:**
- [ ] Toggl website: Timer stopped?
- [ ] Git: Commit "STOP Task 1 - Sáng"?
- [ ] Telegram: Message received?
- [ ] `atq`: Job stop Task 1 removed?
- [ ] Log: STOP Task 1 OK?
- [ ] Toggl: Duration ~4h17p32s?

### Step 4: START Task 2 (12:03 Trưa)
**Run:** `python3 /root/.openclaw/workspace/scripts/toggl_automation.py start-afternoon`

**Verify:**
- [ ] Toggl website: Timer running?
- [ ] Git: Commit "START Task 2 - Chiều"?
- [ ] Telegram: Message received?
- [ ] `atq`: Có job stop Task 2 (08:47:03 UTC)?
- [ ] Log: Calculate stop time dựa trên Task 1 OK?
- [ ] Log: Schedule stop with 'at' OK?

### Step 5: Wait ~3h44p3s
**Do công việc thực tế**

### Step 6: STOP Task 2 (15:47:03 Chiều - Triggered by `at`)
**Verify:**
- [ ] Toggl website: Timer stopped?
- [ ] Git: Commit "STOP Task 2 - Chiều"?
- [ ] Telegram: Message received?
- [ ] `atq`: Job stop Task 2 removed?
- [ ] Log: STOP Task 2 OK?
- [ ] Toggl: Total ~7h59p35s?
- [ ] Toggl: Tổng trong 7h59p50s-7h59p55s?

---

## ✅ TEST CASE SUCCESS CRITERIA

**Test case PASS khi:**
1. ✅ Tất cả 4 steps đều success
2. ✅ Toggl timer hoạt động đúng (start/stop)
3. ✅ Calculate stop time ngay khi start (không check loop)
4. ✅ `at` jobs scheduled đúng (4:17:32 UTC, 8:47:03 UTC)
5. ✅ Stop triggered đúng giờ (by `at`)
6. ✅ Git commit OK cho mỗi step
7. ✅ Telegram notification OK cho mỗi step
8. ✅ **KHÔNG push GitHub** (chỉ commit)
9. ✅ **KHÔNG check loop** (không còn `check-morning`, `check-total`)
10. ✅ Tổng thời gian: 7h59p35s (trong 7h59p50s-7h59p55s)
11. ✅ **KHÔNG vượt 8h**

**Test case FAIL khi:**
1. ❌ Toggl API error (401, 500, v.v.)
2. ❌ Git commit error
3. ❌ Telegram notification error
4. ❌ Timer không start/stop được
5. ❌ `at` jobs không schedule được
6. ❌ Stop không trigger đúng giờ
7. ❌ Tổng thời gian vượt 8h
8. ❌ Tổng thời gian ngoài 7h59p50s-7h59p55s

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
- `at` command: Available

**Key Changes:**
- ❌ Remove: `check-morning`, `check-total` (check loop)
- ✅ Add: Calculate ngay stop time khi start
- ✅ Add: Schedule stop với `at` command
- ✅ Logic: Stop = start_time + duration (không check loop)

---

## 🎯 TEST CASE RESULT

**Result:** PENDING

**Notes:**
- [ ] Test case chưa chạy
- [ ] Đợi user chạy test case
- [ ] Sau khi test → Cập nhật result

---

**Created by:** KIKI 🐶
**Date:** 2026-03-21 15:05 UTC (22:05 VN)
**Version:** 2.0 (New logic: No check loop, calculate stop time immediately)
