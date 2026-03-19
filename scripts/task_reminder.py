#!/usr/bin/env python3
"""
Task Reminder Script
Nhắc người dùng gửi title task vào 7:00 sáng và 12:00 trưa (VN time)
"""

import subprocess
import json
from datetime import datetime
import sys

# Cấu hình
TELEGRAM_CHAT_ID = "320491154"
LOG_FILE = "/root/.openclaw/workspace/logs/task_reminder.log"

def log_message(message):
    """Log message vào file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    print(log_entry)

def send_telegram_message(message):
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
        error_msg = f"Lỗi gửi tin nhắn: {e.stderr}"
        log_message(error_msg)
        return False

def morning_reminder():
    """Nhắc sáng 7:00 VN"""
    message = """🌅 Chào buổi sáng Được Được! Đã 7:00 rồi.

Hãy gửi title Task 1 nhé!

Ví dụ: "Task 1: Code API auth cho dự án A""

Sau đó KIKI sẽ:
- Lưu title task
- (Sau này sẽ bấm timer Toggl tự động)

Chúc một ngày làm việc hiệu quả! 💪"""
    log_message("Reminder sáng 7:00 VN")
    return send_telegram_message(message)

def afternoon_reminder():
    """Nhắc trưa 12:00 VN"""
    message = """☀️ Đã 12:00 trưa! Nghỉ trưa.

Hãy gửi title Task 2 nhé!

Ví dụ: "Task 2: Review PR dự án B""

Sau đó KIKI sẽ:
- Lưu title task
- (Sau này sẽ bấm timer Toggl tự động)

Trưa nghỉ ngơi nhé! ☕"""
    log_message("Reminder trưa 12:00 VN")
    return send_telegram_message(message)

def main():
    """Main function"""
    # Check argument
    if len(sys.argv) < 2:
        print("Cách dùng: python3 task_reminder.py [morning|afternoon]")
        sys.exit(1)

    action = sys.argv[1]

    # Create log directory
    import os
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Execute action
    if action == "morning":
        log_message("Bắt đầu reminder sáng 7:00 VN")
        result = morning_reminder()
        if result:
            log_message("Reminder sáng thành công")
        else:
            log_message("Reminder sáng thất bại")
    elif action == "afternoon":
        log_message("Bắt đầu reminder trưa 12:00 VN")
        result = afternoon_reminder()
        if result:
            log_message("Reminder trưa thành công")
        else:
            log_message("Reminder trưa thất bại")
    else:
        print(f"Action không hợp lệ: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
