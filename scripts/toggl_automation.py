#!/usr/bin/env python3
"""
Toggl Automation Script
Auto start/stop timer theo lịch trình
Sử dụng Toggl API để track thời gian làm việc
"""

import os
import sys
import subprocess
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cấu hình
TOGGL_API_TOKEN = os.getenv("TOGGL_API_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Ho_Chi_Minh")

# Toggl API Base URL
TOGGL_API_URL = "https://api.track.toggl.com/api/v9"

# Headers cho Toggl API
TOGGL_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOGGL_API_TOKEN}"
}

def log_message(message):
    """Log message vào file"""
    log_file = "/root/.openclaw/workspace/logs/toggl_automation.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(log_file, "a") as f:
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

def get_toggl_workspaces():
    """Lấy danh sách workspaces từ Toggl"""
    url = f"{TOGGL_API_URL}/me/workspaces"
    response = requests.get(url, headers=TOGGL_HEADERS)
    if response.status_code == 200:
        workspaces = response.json()
        log_message(f"Lấy được {len(workspaces)} workspace(s)")
        return workspaces
    else:
        error_msg = f"Lỗi lấy workspace: {response.status_code} - {response.text}"
        log_message(error_msg)
        return None

def get_toggl_projects(workspace_id):
    """Lấy danh sách projects từ workspace"""
    url = f"{TOGGL_API_URL}/workspaces/{workspace_id}/projects"
    response = requests.get(url, headers=TOGGL_HEADERS)
    if response.status_code == 200:
        projects = response.json()
        log_message(f"Lấy được {len(projects)} project(s) từ workspace {workspace_id}")
        return projects
    else:
        error_msg = f"Lỗi lấy projects: {response.status_code} - {response.text}"
        log_message(error_msg)
        return None

def start_timer(description="Làm việc"):
    """Bắt đầu timer Toggl"""
    # Get workspace đầu tiên
    workspaces = get_toggl_workspaces()
    if not workspaces or len(workspaces) == 0:
        log_message("Không tìm thấy workspace!")
        return False

    workspace_id = workspaces[0]["id"]
    log_message(f"Sử dụng workspace: {workspaces[0]['name']} (ID: {workspace_id})")

    # Tạo time entry
    data = {
        "workspace_id": workspace_id,
        "description": description,
        "duration": -1,  # -1 = timer đang chạy
        "created_with": "Toggl Automation by KIKI"
    }

    url = f"{TOGGL_API_URL}/workspaces/{workspace_id}/time_entries"
    response = requests.post(url, headers=TOGGL_HEADERS, json=data)

    if response.status_code == 200:
        time_entry = response.json()
        log_message(f"Đã bắt đầu timer: {description}")
        return time_entry
    else:
        error_msg = f"Lỗi bắt đầu timer: {response.status_code} - {response.text}"
        log_message(error_msg)
        return None

def stop_current_timer():
    """Dừng timer đang chạy"""
    # Get workspace đầu tiên
    workspaces = get_toggl_workspaces()
    if not workspaces or len(workspaces) == 0:
        log_message("Không tìm thấy workspace!")
        return False

    workspace_id = workspaces[0]["id"]

    # Get timer đang chạy
    url = f"{TOGGL_API_URL}/workspaces/{workspace_id}/time_entries?in_progress=true"
    response = requests.get(url, headers=TOGGL_HEADERS)

    if response.status_code == 200:
        current_entries = response.json()
        if len(current_entries) == 0:
            log_message("Không có timer đang chạy!")
            return False

        current_entry = current_entries[0]
        entry_id = current_entry["id"]
        stop_url = f"{TOGGL_API_URL}/workspaces/{workspace_id}/time_entries/{entry_id}/stop"

        # Stop timer
        stop_response = requests.patch(stop_url, headers=TOGGL_HEADERS)

        if stop_response.status_code == 200:
            stopped_entry = stop_response.json()
            duration_seconds = stopped_entry.get("duration", 0)
            duration_hours = duration_seconds / 3600
            log_message(f"Đã dừng timer: {current_entry['description']} (Thời gian: {duration_hours:.2f}h)")
            return stopped_entry
        else:
            error_msg = f"Lỗi dừng timer: {stop_response.status_code} - {stop_response.text}"
            log_message(error_msg)
            return None
    else:
        error_msg = f"Lỗi lấy timer đang chạy: {response.status_code} - {response.text}"
        log_message(error_msg)
        return None

def get_today_total_time():
    """Lấy tổng thời gian làm việc hôm nay (giây)"""
    # Get workspace đầu tiên
    workspaces = get_toggl_workspaces()
    if not workspaces or len(workspaces) == 0:
        return 0

    workspace_id = workspaces[0]["id"]

    # Get time entries hôm nay
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{TOGGL_API_URL}/workspaces/{workspace_id}/time_entries?start_date={today}T00:00:00Z"
    response = requests.get(url, headers=TOGGL_HEADERS)

    if response.status_code == 200:
        entries = response.json()
        total_seconds = sum(entry.get("duration", 0) for entry in entries if entry.get("duration") > 0)
        total_hours = total_seconds / 3600
        log_message(f"Tổng thời gian hôm nay: {total_hours:.2f}h ({total_seconds}s)")
        return total_seconds
    else:
        error_msg = f"Lỗi lấy tổng thời gian: {response.status_code} - {response.text}"
        log_message(error_msg)
        return 0

def start_morning():
    """Bắt đầu làm việc buổi sáng (7:00 VN)"""
    log_message("=== BẮT ĐẦU LÀM VIỆC SÁNG ===")

    # Bắt đầu timer
    result = start_timer("Làm việc - Sáng")
    if result:
        message = """🌅 Đã bấm timer buổi sáng! 7:00 sáng

Task: Làm việc - Sáng

KIKI sẽ tự động stop khi đạt 4h15p-4h20p.

Chúc một ngày làm việc hiệu quả! 💪"""
        send_telegram_message(message)
    else:
        message = "⚠️ Không thể bắt đầu timer sáng! Kiểm tra Toggl API."
        send_telegram_message(message)

def stop_morning():
    """Dừng timer buổi sáng (11:15-11:20 VN)"""
    log_message("=== DỪNG LÀM VIỆC SÁNG ===")

    # Dừng timer
    result = stop_current_timer()
    if result:
        message = """☕ Đã nghỉ trưa! Sáng làm việc xong.

Tổng thời gian sáng: {duration}

Đã nghỉ trưa 12:00. Chiều bắt đầu random trong 12:00-12:15! ☀️""".format(duration=result.get("duration", 0) / 3600)
        send_telegram_message(message)
    else:
        log_message("Không có timer đang chạy để dừng!")

def check_morning_time():
    """Check xem đã đến lúc stop buổi sáng chưa (4h15p-4h20p)"""
    log_message("=== CHECK SÁNG ===")

    # Get timer đang chạy
    workspaces = get_toggl_workspaces()
    if not workspaces or len(workspaces) == 0:
        return

    workspace_id = workspaces[0]["id"]
    url = f"{TOGGL_API_URL}/workspaces/{workspace_id}/time_entries?in_progress=true"
    response = requests.get(url, headers=TOGGL_HEADERS)

    if response.status_code == 200:
        current_entries = response.json()
        if len(current_entries) > 0:
            current_entry = current_entries[0]
            duration_seconds = current_entry.get("duration", 0) * -1  # Timer đang chạy, duration là số âm
            duration_hours = duration_seconds / 3600

            # Check xem đã đạt 4h15p-4h20p chưa (15300-15600 giây)
            if 15300 <= duration_seconds <= 15600:
                log_message(f"Đã đến lúc stop sáng! Đã làm {duration_hours:.2f}h")
                stop_morning()
            else:
                log_message(f"Sáng chưa đủ thời gian: {duration_hours:.2f}h (cần 4h15p-4h20p)")
        else:
            log_message("Không có timer đang chạy!")

def start_afternoon():
    """Bắt đầu làm việc buổi chiều (random 12:00-12:15 VN)"""
    log_message("=== BẮT ĐẦU LÀM VIỆC CHIỀU ===")

    # Bắt đầu timer
    result = start_timer("Làm việc - Chiều")
    if result:
        message = """☀️ Đã bấm timer buổi chiều!

Task: Làm việc - Chiều

KIKI sẽ tự động stop khi tổng = 7h59p50s-7h59p55s.

Chúc buổi chiều làm việc hiệu quả! ☀️"""
        send_telegram_message(message)
    else:
        message = "⚠️ Không thể bắt đầu timer chiều! Kiểm tra Toggl API."
        send_telegram_message(message)

def check_total_time_and_stop():
    """Check tổng thời gian và stop khi đạt 7h59p50s-7h59p55s"""
    log_message("=== CHECK TỔNG THỜI GIAN ===")

    total_seconds = get_today_total_time()
    total_hours = total_seconds / 3600

    # Check xem đã đạt 7h59p50s-7h59p55s chưa (28790-28795 giây)
    if 28790 <= total_seconds <= 28795:
        log_message(f"Đã đến lúc stop! Tổng: {total_hours:.2f}h ({total_seconds}s)")

        # Dừng timer
        result = stop_current_timer()
        if result:
            message = """🎉 Hoàn thành làm việc hôm nay!

Tổng thời gian: {duration}

Đã đạt 7h59p50s-7h59p55s! Không làm thêm nhé!

Hẹn gặp lại ngày mai! 🌙""".format(duration=result.get("duration", 0) / 3600)
            send_telegram_message(message)
        else:
            log_message("Không có timer đang chạy để dừng!")
    elif total_seconds >= 28800:  # 8h = 28800 giây
        log_message(f"⚠️ Đã vượt quá 8h! Tổng: {total_hours:.2f}h")

        # Dừng timer ngay lập tức
        stop_current_timer()
        message = f"⚠️ Đã vượt quá 8h! Tổng: {total_hours:.2f}h\n\nKIKI đã dừng timer!"
        send_telegram_message(message)
    else:
        log_message(f"Tổng chưa đủ: {total_hours:.2f}h (cần 7h59p50s-7h59p55s)")

def main():
    """Main function"""
    # Check argument
    if len(sys.argv) < 2:
        print("Cách dùng: python3 toggl_automation.py [action]")
        print("Actions: start-morning, stop-morning, check-morning, start-afternoon, check-total, test")
        sys.exit(1)

    action = sys.argv[1]

    # Create log directory
    import os
    os.makedirs(os.path.dirname("/root/.openclaw/workspace/logs/toggl_automation.log"), exist_ok=True)

    # Execute action
    if action == "start-morning":
        start_morning()
    elif action == "stop-morning":
        stop_morning()
    elif action == "check-morning":
        check_morning_time()
    elif action == "start-afternoon":
        start_afternoon()
    elif action == "check-total":
        check_total_time_and_stop()
    elif action == "test":
        # Test script
        print("=== TEST TOGGL AUTOMATION ===")
        workspaces = get_toggl_workspaces()
        if workspaces:
            print(f"✅ Toggl API OK! Found {len(workspaces)} workspace(s)")
            for ws in workspaces:
                print(f"   - {ws['name']} (ID: {ws['id']})")
        else:
            print("❌ Toggl API FAILED!")
    else:
        print(f"Action không hợp lệ: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
