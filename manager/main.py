import sys
import signal
import tomllib
from pathlib import Path

from scheduler import BackupScheduler, FrequencyController
from backup import backup_and_monitor, get_repo_size
import database

CONFIG_PATH = Path(__file__).parent.parent / "config" / "app.toml"


def load_config() -> dict:
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


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
    
    scheduler.init(controller, do_backup)
    
    record_times = monitor_config["record_times"]
    if "startup" in record_times:
        repo_size = get_repo_size(profile)
        if repo_size:
            database.record_disk_usage(path_id, repo_size)
    
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
    
    print("Rustic Manager started")
    print(f"Profile: {profile}")
    print(f"Initial interval: {controller.current_interval} minutes")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
