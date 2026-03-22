import sys
import signal
import tomllib
import time
from pathlib import Path

from scheduler import BackupScheduler, FrequencyController
from backup import backup_and_monitor, get_repo_size
from http_server import HTTPServerThread, check_heartbeat_timeout
import database

CONFIG_PATH = Path(__file__).parent.parent / "config" / "app.toml"


def load_config() -> dict:
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def parse_time_record(record: str):
    if record.startswith("time:"):
        time_str = record[5:]
        parts = time_str.split(":")
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
    return None, None


def main():
    config = load_config()
    
    database.init_db()
    
    profile = config["rustic"]["profile"]
    path_id = database.register_path(profile)
    
    backup_config = config["backup"]
    monitor_config = config["monitor"]
    
    controller = FrequencyController(
        min_interval=backup_config["min"],
        max_interval=backup_config["max"],
        init_interval=backup_config["init"]
    )
    
    scheduler = BackupScheduler()
    
    change_limit = monitor_config["change_limit"]
    
    def do_backup():
        return backup_and_monitor(profile, path_id, change_limit)
    
    def do_daily_record():
        repo_size = get_repo_size(profile)
        if repo_size:
            database.record_disk_usage(path_id, repo_size)
            print(f"Daily record: {repo_size} bytes")
    
    scheduler.init(controller, do_backup)
    
    record_times = monitor_config["record_times"]
    if "startup" in record_times:
        repo_size = get_repo_size(profile)
        if repo_size:
            database.record_disk_usage(path_id, repo_size)
    
    for record in record_times:
        hour, minute = parse_time_record(record)
        if hour is not None:
            scheduler.add_daily_job(do_daily_record, hour, minute)
            print(f"Scheduled daily record at {hour:02d}:{minute:02d}")
    
    def signal_handler(sig, frame):
        if "shutdown" in record_times:
            repo_size = get_repo_size(profile)
            if repo_size:
                database.record_disk_usage(path_id, repo_size)
        
        scheduler.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    scheduler.start()
    
    http_server = HTTPServerThread(port=8765)
    http_server.start(controller)
    
    print("Rustic Manager started")
    print(f"Profile: {profile}")
    print(f"Initial interval: {controller.current_interval} minutes")
    
    try:
        while True:
            time.sleep(1)
            check_heartbeat_timeout()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
