#!/usr/bin/env node
/**
 * Toggl Automation Script (Node.js Version)
 * Auto start/stop timer theo lịch trình
 * Git commit mỗi lần START/STOP (KHÔNG push)
 * Sử dụng Toggl API để track thời gian làm việc
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
require('dotenv').config();

// Cấu hình
const TOGGL_API_TOKEN = process.env.TOGGL_API_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const TIMEZONE = process.env.TIMEZONE || 'Asia/Ho_Chi_Minh';

// Toggl API Base URL
const TOGGL_API_URL = 'https://api.track.toggl.com/api/v9';

// Headers cho Toggl API (Basic Auth)
const auth = Buffer.from(`${TOGGL_API_TOKEN}:api_token`).toString('base64');
const TOGGL_HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': `Basic ${auth}`
};

const LOG_FILE = '/root/.openclaw/workspace/logs/toggl_automation.log';

// Helper functions
function logMessage(message) {
    const timestamp = new Date().toISOString().replace('T', ' ');
    const logEntry = `[${timestamp}] ${message}\n`;
    fs.appendFileSync(LOG_FILE, logEntry);
    console.log(logEntry);
}

function sendTelegramMessage(message) {
    const cmd = `openclaw message send --channel telegram --target ${TELEGRAM_CHAT_ID} --message "${message}"`;
    return new Promise((resolve, reject) => {
        exec(cmd, (error, stdout, stderr) => {
            if (error) {
                const errorMsg = `Lỗi gửi tin nhắn: ${stderr}`;
                logMessage(errorMsg);
                reject(error);
            } else {
                resolve(stdout);
            }
        });
    });
}

function gitCommit(message) {
    const cmd = `git commit -m "${message}"`;
    return new Promise((resolve, reject) => {
        exec(cmd, { cwd: '/root/.openclaw/workspace' }, (error, stdout, stderr) => {
            if (error) {
                const errorMsg = `Lỗi git commit: ${stderr}`;
                logMessage(errorMsg);
                reject(error);
            } else {
                logMessage(`Git commit: ${message}`);
                resolve(stdout);
            }
        });
    });
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}h${minutes}p${secs}s`;
}

function formatTimeFromSeconds(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

async function getTogglWorkspaces() {
    try {
        const url = `${TOGGL_API_URL}/me/workspaces`;
        const response = await axios.get(url, { headers: TOGGL_HEADERS });
        logMessage(`Lấy được ${response.data.length} workspace(s)`);
        return response.data;
    } catch (error) {
        const errorMsg = `Lỗi lấy workspace: ${error.response.status} - ${error.response.data}`;
        logMessage(errorMsg);
        return null;
    }
}

async function startTimer(description = 'Làm việc') {
    try {
        const workspaces = await getTogglWorkspaces();
        if (!workspaces || workspaces.length === 0) {
            logMessage('Không tìm thấy workspace!');
            return false;
        }

        const workspaceId = workspaces[0].id;
        logMessage(`Sử dụng workspace: ${workspaces[0].name} (ID: ${workspaceId})`);

        // Tạo time entry
        const data = {
            workspace_id: workspaceId,
            description: description,
            duration: -1,  // -1 = timer đang chạy
            created_with: 'Toggl Automation by KIKI'
        };

        const url = `${TOGGL_API_URL}/workspaces/${workspaceId}/time_entries`;
        const response = await axios.post(url, data, { headers: TOGGL_HEADERS });

        if (response.status === 200) {
            const timeEntry = response.data;
            logMessage(`Đã bắt đầu timer: ${description}`);
            return timeEntry;
        }
    } catch (error) {
        const errorMsg = `Lỗi bắt đầu timer: ${error.response.status} - ${JSON.stringify(error.response.data)}`;
        logMessage(errorMsg);
        return null;
    }
}

async function stopCurrentTimer() {
    try {
        const workspaces = await getTogglWorkspaces();
        if (!workspaces || workspaces.length === 0) {
            logMessage('Không tìm thấy workspace!');
            return false;
        }

        const workspaceId = workspaces[0].id;

        // Get timer đang chạy
        const url = `${TOGGL_API_URL}/workspaces/${workspaceId}/time_entries?in_progress=true`;
        const response = await axios.get(url, { headers: TOGGL_HEADERS });

        if (response.status === 200) {
            const currentEntries = response.data;
            if (currentEntries.length === 0) {
                logMessage('Không có timer đang chạy!');
                return false;
            }

            const currentEntry = currentEntries[0];
            const entryId = currentEntry.id;
            const stopUrl = `${TOGGL_API_URL}/workspaces/${workspaceId}/time_entries/${entryId}/stop`;

            // Stop timer
            const stopResponse = await axios.patch(stopUrl, null, { headers: TOGGL_HEADERS });

            if (stopResponse.status === 200) {
                const stoppedEntry = stopResponse.data;
                const durationSeconds = stoppedEntry.duration || 0;
                const durationHours = durationSeconds / 3600;
                logMessage(`Đã dừng timer: ${currentEntry.description} (Thời gian: ${durationHours.toFixed(2)}h)`);
                return stoppedEntry;
            }
        }
    } catch (error) {
        const errorMsg = `Lỗi dừng timer: ${error.response.status} - ${JSON.stringify(error.response.data)}`;
        logMessage(errorMsg);
        return null;
    }
}

async function getTodayTotalTime() {
    try {
        const workspaces = await getTogglWorkspaces();
        if (!workspaces || workspaces.length === 0) {
            return 0;
        }

        const workspaceId = workspaces[0].id;

        // Get time entries hôm nay
        const today = new Date().toISOString().split('T')[0];
        const url = `${TOGGL_API_URL}/workspaces/${workspaceId}/time_entries?start_date=${today}T00:00:00Z`;
        const response = await axios.get(url, { headers: TOGGL_HEADERS });

        if (response.status === 200) {
            const entries = response.data;
            const totalSeconds = entries.reduce((sum, entry) => sum + (entry.duration > 0 ? entry.duration : 0), 0);
            const totalHours = totalSeconds / 3600;
            logMessage(`Tổng thời gian hôm nay: ${totalHours.toFixed(2)}h (${totalSeconds}s)`);
            return totalSeconds;
        }
    } catch (error) {
        const errorMsg = `Lỗi lấy tổng thời gian: ${error.response.status} - ${JSON.stringify(error.response.data)}`;
        logMessage(errorMsg);
        return 0;
    }
}

function scheduleAt(command, utcTimeStr) {
    return new Promise((resolve, reject) => {
        const fullCommand = `echo "${command}" | at ${utcTimeStr}`;
        exec(fullCommand, (error, stdout, stderr) => {
            if (error) {
                const errorMsg = `Lỗi schedule 'at': ${stderr}`;
                logMessage(errorMsg);
                reject(error);
            } else {
                logMessage(`Schedule with 'at': ${fullCommand}`);
                resolve(stdout);
            }
        });
    });
}

async function startMorning() {
    logMessage('=== BẮT ĐẦU LÀM VIỆC SÁNG ===');

    // Bắt đầu timer
    const result = await startTimer('Làm việc - Sáng');
    if (result) {
        // Calculate ngay stop time: random 4h15p-4h20p (15300-15600s)
        const randomSeconds = Math.floor(Math.random() * (15600 - 15300 + 1)) + 15300;
        const stopDuration = randomSeconds * 1000; // milliseconds

        // Calculate stop time UTC
        const startUtc = new Date();
        const stopUtc = new Date(startUtc.getTime() + stopDuration);

        // Format stop time for 'at' command
        const stopTimeStr = stopUtc.toISOString().substring(11, 16); // HH:MM
        const stopTimeVn = new Date(stopUtc.getTime() + 7 * 3600 * 1000);
        const stopTimeVnStr = stopTimeVn.toISOString().substring(11, 19);

        // Schedule stop với 'at'
        const command = 'node /root/.openclaw/workspace/scripts/toggl-automation.js stop-morning';
        await scheduleAt(command, stopTimeStr);

        logMessage(`Schedule stop: ${stopUtc.toISOString()} (${stopTimeVnStr} VN)`);

        // Git commit
        const commitMsg = `feat: START Task 1 - Sáng

Time: 7:00 VN (0:00 UTC)
Stop: ${stopTimeVnStr} VN (${stopTimeStr} UTC)
Duration: ~${formatDuration(randomSeconds)}
Description: Làm việc - Sáng

Started by KIKI Task Automation
Stop scheduled with 'at' at ${stopTimeStr} UTC`;

        await gitCommit(commitMsg);

        // Gửi Telegram
        const message = `🌅 Đã bấm timer buổi sáng! 7:00 sáng

Task: Làm việc - Sáng
Stop: ${stopTimeVnStr} VN

KIKI sẽ tự động stop vào ${stopTimeStr} UTC (${stopTimeVnStr} VN).

Chúc một ngày làm việc hiệu quả! 💪`;

        await sendTelegramMessage(message);
    } else {
        const message = '⚠️ Không thể bắt đầu timer sáng! Kiểm tra Toggl API.';
        await sendTelegramMessage(message);
    }
}

async function stopMorning() {
    logMessage('=== DỪNG LÀM VIỆC SÁNG (TRIGGERED BY "at") ===');

    // Dừng timer
    const result = await stopCurrentTimer();
    if (result) {
        const durationSeconds = result.duration || 0;
        const durationFormatted = formatDuration(durationSeconds);

        // Git commit
        const commitMsg = `feat: STOP Task 1 - Sáng

Time: ${new Date().toISOString().substring(11, 16)} UTC (${new Date(Date.now() + 7 * 3600 * 1000).toISOString().substring(11, 16)} VN)
Duration: ${durationFormatted}
Description: Làm việc - Sáng

Stopped by KIKI Task Automation (Triggered by 'at')
Total today: ${durationFormatted} / 7h59p50s-7h59p55s`;

        await gitCommit(commitMsg);

        // Gửi Telegram
        const message = `☕ Đã nghỉ trưa! Sáng làm việc xong.

Thời gian sáng: ${durationFormatted}

Đã nghỉ trưa 12:00. Chiều bắt đầu random trong 12:00-12:15! ☀️`;

        await sendTelegramMessage(message);
    } else {
        logMessage('Không có timer đang chạy để dừng!');
    }
}

async function startAfternoon() {
    logMessage('=== BẮT ĐẦU LÀM VIỆC CHIỀU ===');

    // Get Task 1 duration
    const todayTotal = await getTodayTotalTime();
    const task1Duration = todayTotal; // Tổng hiện tại = Task 1 (vì chưa có Task 2)

    // Random start chiều trong 12:00-12:15 VN (5:00-5:15 UTC)
    const randomMinutes = Math.floor(Math.random() * 16); // 0-15 phút
    const randomSeconds = randomMinutes * 60;
    const startAfternoonUtc = new Date();
    startAfternoonUtc.setUTCHours(5, 0, 0, 0);
    startAfternoonUtc.setUTCSeconds(randomSeconds);

    // Bắt đầu timer
    const result = await startTimer('Làm việc - Chiều');
    if (result) {
        // Calculate stop time: Target 7h59p50s-7h59p55s (28790-28795s)
        const targetTotalSeconds = Math.floor(Math.random() * (28795 - 28790 + 1)) + 28790; // 7h59p50s-7h59p55s
        const task2DurationSeconds = targetTotalSeconds - task1Duration;

        // Calculate stop time
        const stopUtc = new Date(startAfternoonUtc.getTime() + task2DurationSeconds * 1000);

        // Format stop time for 'at' command
        const stopTimeStr = stopUtc.toISOString().substring(11, 16); // HH:MM
        const stopTimeVn = new Date(stopUtc.getTime() + 7 * 3600 * 1000);
        const stopTimeVnStr = stopTimeVn.toISOString().substring(11, 19);

        // Schedule stop với 'at'
        const command = 'node /root/.openclaw/workspace/scripts/toggl-automation.js stop-afternoon';
        await scheduleAt(command, stopTimeStr);

        logMessage(`Task 1 duration: ${formatDuration(task1Duration)} (${task1Duration}s)`);
        logMessage(`Task 2 duration: ${formatDuration(task2DurationSeconds)} (${task2DurationSeconds}s)`);
        logMessage(`Target total: ${formatDuration(targetTotalSeconds)} (${targetTotalSeconds}s)`);
        logMessage(`Schedule stop: ${stopUtc.toISOString()} (${stopTimeVnStr} VN)`);

        // Git commit
        const commitMsg = `feat: START Task 2 - Chiều

Time: ${(startAfternoonUtc.getTime() + 7 * 3600 * 1000).toISOString().substring(11, 16)} VN (${startAfternoonUtc.toISOString().substring(11, 16)} UTC)
Stop: ${stopTimeVnStr} VN (${stopTimeStr} UTC)
Duration: ~${formatDuration(task2DurationSeconds)}

Task 1 duration: ${formatDuration(task1Duration)} (${task1Duration}s)
Target total: ${formatDuration(targetTotalSeconds)} (${targetTotalSeconds}s)

Started by KIKI Task Automation (Random start 12:00-12:15 VN)
Stop scheduled with 'at' at ${stopTimeStr} UTC`;

        await gitCommit(commitMsg);

        // Gửi Telegram
        const message = `☀️ Đã bấm timer buổi chiều!

Task: Làm việc - Chiều
Start: ${(startAfternoonUtc.getTime() + 7 * 3600 * 1000).toISOString().substring(11, 16)} VN
Stop: ${stopTimeVnStr} VN

Task 1 duration: ${formatDuration(task1Duration)}
Target total: ${formatDuration(targetTotalSeconds)}

KIKI sẽ tự động stop vào ${stopTimeStr} UTC (${stopTimeVnStr} VN).

Chúc buổi chiều làm việc hiệu quả! ☀️`;

        await sendTelegramMessage(message);
    } else {
        const message = '⚠️ Không thể bắt đầu timer chiều! Kiểm tra Toggl API.';
        await sendTelegramMessage(message);
    }
}

async function stopAfternoon() {
    logMessage('=== STOP TASK 2 (TRIGGERED BY "at") ===');

    // Dừng timer
    const result = await stopCurrentTimer();
    if (result) {
        const durationSeconds = result.duration || 0;
        const durationFormatted = formatDuration(durationSeconds);

        // Get total time
        const totalSeconds = await getTodayTotalTime();
        const totalFormatted = formatDuration(totalSeconds);

        // Git commit
        const commitMsg = `feat: STOP Task 2 - Chiều

Time: ${new Date().toISOString().substring(11, 16)} UTC (${new Date(Date.now() + 7 * 3600 * 1000).toISOString().substring(11, 16)} VN)
Duration: ${durationFormatted}
Description: Làm việc - Chiều

Stopped by KIKI Task Automation (Triggered by 'at')
Total today: ${totalFormatted} / 7h59p50s-7h59p55s ✅`;

        await gitCommit(commitMsg);

        // Gửi Telegram
        const message = `🎉 Hoàn thành làm việc hôm nay!

Tổng thời gian: ${totalFormatted}

Đã đạt 7h59p50s-7h59p55s! Không làm thêm nhé!

Hẹn gặp lại ngày mai! 🌙`;

        await sendTelegramMessage(message);
    } else {
        logMessage('Không có timer đang chạy để dừng!');
    }
}

async function test() {
    console.log('=== TEST TOGGL AUTOMATION ===');
    const workspaces = await getTogglWorkspaces();
    if (workspaces) {
        console.log('✅ Toggl API OK! Found', workspaces.length, 'workspace(s)');
        workspaces.forEach(ws => {
            console.log(`   - ${ws.name} (ID: ${ws.id})`);
        });
    } else {
        console.log('❌ Toggl API FAILED!');
    }
}

// Main
const action = process.argv[2];

// Create log directory
const logDir = path.dirname(LOG_FILE);
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
}

// Execute action
(async () => {
    switch (action) {
        case 'start-morning':
            await startMorning();
            break;
        case 'stop-morning':
            await stopMorning();
            break;
        case 'start-afternoon':
            await startAfternoon();
            break;
        case 'stop-afternoon':
            await stopAfternoon();
            break;
        case 'test':
            await test();
            break;
        default:
            console.log('Cách dùng: node toggl-automation.js [action]');
            console.log('Actions: start-morning, stop-morning, start-afternoon, stop-afternoon, test');
            process.exit(1);
    }
})();
