import subprocess
import json
import time
from pathlib import Path
from typing import Optional, Tuple
import database
import platform

if platform.system() == "Windows":
    from win10toast import ToastNotifier
    toaster = ToastNotifier()


def run_rustic_backup(profile: str) -> Tuple[bool, Optional[str], float]:
    start_time = time.time()
    
    cmd = ["rustic", "-P", profile, "backup", "--skip-if-unchanged"]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600
        )
        
        duration = time.time() - start_time
        
        if "no changes" in result.stdout.lower() or "skipping" in result.stdout.lower():
            return False, None, duration
        
        snapshot_id = None
        for line in result.stdout.split("\n"):
            if "snapshot" in line.lower():
                parts = line.split()
                for part in parts:
                    if len(part) == 64:
                        snapshot_id = part
                        break
        
        return True, snapshot_id, duration
    
    except subprocess.TimeoutExpired:
        return False, None, 0
    except Exception as e:
        print(f"Backup error: {e}")
        return False, None, 0


def get_repo_size(profile: str) -> Optional[int]:
    cmd = ["rustic", "-P", profile, "repoinfo", "--json"]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        for line in result.stdout.split("\n"):
            if line.strip().startswith("{"):
                data = json.loads(line)
                total_size = 0
                for item in data.get("files", {}).get("repo", []):
                    total_size += item.get("size", 0)
                return total_size
        
        return None
    
    except Exception as e:
        print(f"Get repo size error: {e}")
        return None


def send_notification(title: str, message: str):
    print(f"[{title}] {message}")
    
    if platform.system() == "Windows":
        try:
            toaster.show_toast(title, message, duration=5)
        except Exception as e:
            print(f"Notification error: {e}")


def backup_and_monitor(profile: str, path_id: int, change_limit: int) -> Tuple[bool, float]:
    old_size = database.get_latest_disk_usage(path_id)
    
    has_changes, snapshot_id, duration = run_rustic_backup(profile)
    
    new_size = get_repo_size(profile)
    
    if new_size is not None:
        database.record_disk_usage(path_id, new_size)
    
    if has_changes and new_size is not None:
        space_change = 0
        if old_size is not None:
            space_change = new_size - old_size
        
        database.record_backup(path_id, snapshot_id, duration, space_change)
        
        if abs(space_change) > change_limit * 1024 * 1024:
            change_mb = space_change / (1024 * 1024)
            direction = "增加" if space_change > 0 else "减少"
            send_notification(
                "Rustic Manager - 空间变化预警",
                f"仓库空间{direction} {abs(change_mb):.1f} MB"
            )
    
    return has_changes, duration
