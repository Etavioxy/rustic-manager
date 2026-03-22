from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import Callable, Optional
import time


class FrequencyController:
    def __init__(self, min_interval: int, max_interval: int, init_interval: int):
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.init_interval = init_interval
        self.current_interval = init_interval
    
    def on_change(self):
        self.current_interval = max(self.min_interval, self.current_interval // 2)
        return self.current_interval
    
    def on_no_change(self):
        self.current_interval = min(self.max_interval, self.current_interval * 2)
        return self.current_interval
    
    def reset(self):
        self.current_interval = self.init_interval
        return self.current_interval
    
    def set_params(self, min_interval: int, max_interval: int, init_interval: int):
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.init_interval = init_interval
        self.current_interval = init_interval


class BackupScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.controller: Optional[FrequencyController] = None
        self.job_id = "backup_job"
        self.backup_func: Optional[Callable] = None
    
    def init(self, controller: FrequencyController, backup_func: Callable):
        self.controller = controller
        self.backup_func = backup_func
        
    def _run_backup(self):
        if self.backup_func and self.controller:
            has_changes, _ = self.backup_func()
            
            if has_changes:
                new_interval = self.controller.on_change()
            else:
                new_interval = self.controller.on_no_change()
            
            self._reschedule(new_interval)
    
    def _reschedule(self, interval_minutes: int):
        self.scheduler.reschedule_job(
            self.job_id,
            trigger=IntervalTrigger(minutes=interval_minutes)
        )
    
    def start(self):
        if not self.controller or not self.backup_func:
            raise ValueError("Controller and backup_func must be initialized")
        
        self.scheduler.add_job(
            self._run_backup,
            trigger=IntervalTrigger(minutes=self.controller.current_interval),
            id=self.job_id,
            replace_existing=True
        )
        
        self.scheduler.start()
    
    def stop(self):
        self.scheduler.shutdown()
    
    def update_interval(self, interval_minutes: int):
        self._reschedule(interval_minutes)
