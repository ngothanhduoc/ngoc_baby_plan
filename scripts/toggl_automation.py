#!/usr/bin/env python3
"""
Toggl Automation Script (Final - No Check Loop)
Calculate ngay stop time khi start, schedule với 'at' command
Sử dụng Toggl API để track thời gian làm việc
"""

import os
import sys
import subprocess
import requests
import json
import random
import base64
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

# Headers cho Toggl API (Basic Auth)
auth = base64.b64encode(f"{TOGGL_API_TOKEN}:api_token".encode()).decode()
TOGGL_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth}"
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

def git_commit(message):
    """Git commit (KHÔNG push)"""
    cmd = [
        "git", "commit",
        "-m", message
    ]
    try:
        subprocess.run(cmd, cwd="/root/.openclaw/workspace", check=True, capture_output=True, text=True)
        log_message(f"Git commit: {message}")
        return True
    except subprocess.CalledProcessError as e:
        error_msg = f"Lỗi git commit: {e.stderr}"
        log_message(error_msg)
        return False

def schedule_at(command, utc_time_str):
    """Schedule command với 'at'"""
    try:
        # Format: echo "command" | at HH:MM
        full_command = f'echo "{command}" | at {utc_time_str}'
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log_message(f"Schedule with 'at': {full_command}")
            return True
        else:
            error_msg = f"Lỗi schedule 'at': {result.stderr}"
            log_message(error_msg)
            return False
    except Exception as e:
        error_msg = f"Lỗi exception schedule 'at': {e}"
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

def format_duration(seconds):
    """Format giây sang giờ:phút:giây"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}h{minutes}p{secs}s"

def format_time_from_seconds(seconds):
    """Format giây sang HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def start_morning():
    """Bắt đầu làm việc buổi sáng (7:00 VN) - Calculate ngay stop time"""
    log_message("=== BẮT ĐẦU LÀM VIỆC SÁNG ===")

    # Bắt đầu timer
    result = start_timer("Làm việc - Sáng")
    if result:
        # Calculate ngay stop time: random 4h15p-4h20p (15300-15600s)
        random_seconds = random.randint(15300, 15600)  # 4h15p-4h20p
        stop_duration = timedelta(seconds=random_seconds)
        
        # Calculate stop time UTC
        start_time_utc = datetime.utcnow()
        stop_time_utc = start_time_utc + stop_duration
        
        # Format stop time for 'at' command
        stop_time_str = stop_time_utc.strftime("%H:%M")
        stop_time_vn = stop_time_utc + timedelta(hours=7)  # UTC+7
        stop_time_vn_str = stop_time_vn.strftime("%H:%M:%S")
        
        # Schedule stop với 'at'
        command = f"python3 /root/.openclaw/workspace/scripts/toggl_automation.py stop-morning"
        schedule_success = schedule_at(command, stop_time_str)
        
        if schedule_success:
            log_message(f"Schedule stop: {stop_time_utc} UTC ({stop_time_vn_str} VN)")
            
            # Git commit
            commit_msg = f"""feat: START Task 1 - Sáng

Time: 7:00 VN (0:00 UTC)
Stop: {stop_time_vn_str} VN ({stop_time_str} UTC)
Duration: ~{format_duration(random_seconds)}
Description: Làm việc - Sáng

Started by KIKI Task Automation
Stop scheduled with 'at' at {stop_time_str} UTC"""
            git_commit(commit_msg)

            # Gửi Telegram
            message = f"""🌅 Đã bấm timer buổi sáng! 7:00 sáng

Task: Làm việc - Sáng
Stop: {stop_time_vn_str} VN

KIKI sẽ tự động stop vào {stop_time_str} UTC ({stop_time_vn_str} VN).

Chúc một ngày làm việc hiệu quả! 💪"""
            send_telegram_message(message)
        else:
            log_message("❌ Không schedule stop được!")
            message = "⚠️ Không thể bắt đầu timer sáng! Schedule stop failed."
            send_telegram_message(message)
    else:
        message = "⚠️ Không thể bắt đầu timer sáng! Kiểm tra Toggl API."
        send_telegram_message(message)

def stop_morning():
    """Dừng timer buổi sáng (Triggered by 'at')"""
    log_message("=== DỪNG LÀM VIỆC SÁNG (TRIGGERED BY 'at') ===")

    # Dừng timer
    result = stop_current_timer()
    if result:
        duration_seconds = result.get("duration", 0)
        duration_formatted = format_duration(duration_seconds)

        # Git commit
        commit_msg = f"""feat: STOP Task 1 - Sáng

Time: {datetime.utcnow().strftime('%H:%M')} UTC ({(datetime.utcnow() + timedelta(hours=7)).strftime('%H:%M')} VN)
Duration: {duration_formatted}
Description: Làm việc - Sáng

Stopped by KIKI Task Automation (Triggered by 'at')
Total today: {duration_formatted} / 7h59p50s-7h59p55s"""
        git_commit(commit_msg)

        # Gửi Telegram
        message = f"""☕ Đã nghỉ trưa! Sáng làm việc xong.

Thời gian sáng: {duration_formatted}

Đã nghỉ trưa 12:00. Chiều bắt đầu random trong 12:00-12:15! ☀️"""
        send_telegram_message(message)
    else:
        log_message("Không có timer đang chạy để dừng!")

def start_afternoon():
    """Bắt đầu làm việc buổi chiều (random 12:00-12:15 VN) - Calculate ngay stop time dựa trên Task 1"""
    log_message("=== BẮT ĐẦU LÀM VIỆC CHIỀU ===")

    # Get Task 1 duration
    today_total = get_today_total_time()
    task1_duration = today_total  # Tổng hiện tại = Task 1 (vì chưa có Task 2)
    
    # Random start chiều trong 12:00-12:15 VN (5:00-5:15 UTC)
    random_minutes = random.randint(0, 15)
    random_seconds = random_minutes * 60
    start_afternoon_utc = datetime.utcnow().replace(hour=5, minute=0, second=0) + timedelta(seconds=random_seconds)
    
    # Bắt đầu timer
    result = start_timer("Làm việc - Chiều")
    if result:
        # Calculate stop time: Target 7h59p50s-7h59p55s (28790-28795s)
        target_total_seconds = random.randint(28790, 28795)  # 7h59p50s-7h59p55s
        task2_duration_seconds = target_total_seconds - task1_duration
        
        # Calculate stop time
        stop_time_utc = start_afternoon_utc + timedelta(seconds=task2_duration_seconds)
        stop_time_str = stop_time_utc.strftime("%H:%M")
        stop_time_vn = stop_time_utc + timedelta(hours=7)
        stop_time_vn_str = stop_time_vn.strftime("%H:%M:%S")
        
        # Schedule stop với 'at'
        command = f"python3 /root/.openclaw/workspace/scripts/toggl_automation.py stop-afternoon"
        schedule_success = schedule_at(command, stop_time_str)
        
        if schedule_success:
            log_message(f"Schedule stop: {stop_time_utc} UTC ({stop_time_vn_str} VN)")
            log_message(f"Task 1 duration: {format_duration(task1_duration)} ({task1_duration}s)")
            log_message(f"Task 2 duration: {format_duration(task2_duration_seconds)} ({task2_duration_seconds}s)")
            log_message(f"Target total: {format_duration(target_total_seconds)} ({target_total_seconds}s)")
            
            # Git commit
            commit_msg = f"""feat: START Task 2 - Chiều

Time: {(start_afternoon_utc + timedelta(hours=7)).strftime('%H:%M')} VN ({start_afternoon_utc.strftime('%H:%M')} UTC)
Stop: {stop_time_vn_str} VN ({stop_time_str} UTC)
Duration: ~{format_duration(task2_duration_seconds)}
Description: Làm việc - Chiều

Task 1 duration: {format_duration(task1_duration)} ({task1_duration}s)
Target total: {format_duration(target_total_seconds)} ({target_total_seconds}s)

Started by KIKI Task Automation (Random start 12:00-12:15 VN)
Stop scheduled with 'at' at {stop_time_str} UTC"""
            git_commit(commit_msg)

            # Gửi Telegram
            message = f"""☀️ Đã bấm timer buổi chiều!

Task: Làm việc - Chiều
Start: {(start_afternoon_utc + timedelta(hours=7)).strftime('%H:%M')} VN
Stop: {stop_time_vn_str} VN

Thời gian Task 1: {format_duration(task1_duration)}
Target tổng: {format_duration(target_total_seconds)}

KIKI sẽ tự động stop vào {stop_time_str} UTC ({stop_time_vn_str} VN).

Chúc buổi chiều làm việc hiệu quả! ☀️"""
            send_telegram_message(message)
        else:
            log_message("❌ Không schedule stop được!")
            message = "⚠️ Không thể bắt đầu timer chiều! Schedule stop failed."
            send_telegram_message(message)
    else:
        message = "⚠️ Không thể bắt đầu timer chiều! Kiểm tra Toggl API."
        send_telegram_message(message)

def stop_afternoon():
    """Dừng timer buổi chiều (Triggered by 'at')"""
    log_message("=== DỪNG LÀM VIỆC CHIỀU (TRIGGERED BY 'at') ===")

    # Dừng timer
    result = stop_current_timer()
    if result:
        duration_seconds = result.get("duration", 0)
        duration_formatted = format_duration(duration_seconds)
        
        # Get total time
        total_seconds = get_today_total_time()
        total_formatted = format_duration(total_seconds)

        # Git commit
        commit_msg = f"""feat: STOP Task 2 - Chiều

Time: {datetime.utcnow().strftime('%H:%M')} UTC ({(datetime.utcnow() + timedelta(hours=7)).strftime('%H:%M')} VN)
Duration: {duration_formatted}
Description: Làm việc - Chiều

Stopped by KIKI Task Automation (Triggered by 'at')
Total today: {total_formatted} / 7h59p50s-7h59p55s ✅"""
        git_commit(commit_msg)

        # Gửi Telegram
        message = f"""🎉 Hoàn thành làm việc hôm nay!

Tổng thời gian: {total_formatted}

Đã đạt 7h59p50s-7h59p55s! Không làm thêm nhé!

Hẹn gặp lại ngày mai! 🌙"""
        send_telegram_message(message)
    else:
        log_message("Không có timer đang chạy để dừng!")

def main():
    """Main function"""
    # Check argument
    if len(sys.argv) < 2:
        print("Cách dùng: python3 toggl_automation.py [action]")
        print("Actions: start-morning, stop-morning, start-afternoon, stop-afternoon, test")
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
    elif action == "start-afternoon":
        start_afternoon()
    elif action == "stop-afternoon":
        stop_afternoon()
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
