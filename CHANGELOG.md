# CHANGELOG - Toggl API Token Change

## 2026-03-21

### Toggl API Token Update
- **Old Token:** 2c16d14befa2afbc38f52e596d815391 (test account)
- **New Token:** 76a236da101fe009b2d00c18e741d981 (production account)
- **Reason:** Chuyển từ test account sang production account thật

### Workspace Changes
- **Old Workspace ID:** 21266568 (test account)
- **New Workspace ID:** 21271402 (production account)
- **Change:** Token mới → Workspace khác

### API Test Results
- **Test Date:** 2026-03-21 15:16 UTC (22:16 VN)
- **Test Tool:** Node.js (scripts/toggl_automation.js test)
- **Result:** ✅ OK (Found 1 workspace: Workspace (ID: 21271402))
- **API Version:** Toggl API v9 (Basic Auth)

### Files Updated
- `.env` - Updated TOGGL_API_TOKEN and workspace log
- `scripts/toggl_automation.js` - Node.js version created
- `scripts/toggl_automation.py` - Python version created
- `test_case_toggl.md` - Old test case (check loop)
- `test_case_toggl_v2.md` - New test case (no check loop)
- `package.json` - Node.js project with axios, dotenv

### Scripts Available
- **Node.js Version:** `scripts/toggl_automation.js`
  - Actions: start-morning, stop-morning, start-afternoon, stop-afternoon, test
  - Features: No check loop, calculate stop time immediately, schedule with 'at', git commit, telegram notification
  - Usage: `node scripts/toggl_automation.js [action]`

- **Python Version:** `scripts/toggl_automation.py` (backup)
  - Actions: start-morning, stop-morning, check-morning, start-afternoon, check-total, test
  - Features: No check loop, calculate stop time immediately, git commit, telegram notification
  - Usage: `python3 scripts/toggl_automation.py [action]`

### Automation Flow
1. **START Task 1 (7:00 VN)** → Git commit + Telegram notification
2. **STOP Task 1 (11:15-11:20 VN)** → Git commit + Telegram notification (triggered by 'at')
3. **START Task 2 (12:00-12:15 VN, random)** → Git commit + Telegram notification
4. **STOP Task 2 (15:47 VN)** → Git commit + Telegram notification (triggered by 'at', calculate based on Task 1)

### Success Criteria
- Toggl timer: Start/stop OK
- Git commit: OK for each step
- Telegram notification: OK for each step
- Total time: 7h59p50s-7h59p55s (no push to GitHub)
- No check loop: Immediate calculate and schedule

---

**Last Updated:** 2026-03-21 15:16 UTC (22:16 VN)
**Updated By:** KIKI 🐶
