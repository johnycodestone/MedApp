# adminpanel/tasks.py

"""
Asynchronous and scheduled tasks for adminpanel system operations.
Designed for use with Celery, Django-Q, or other task queues.
"""

import time
import logging
from django.utils import timezone
from .models import BackupRecord, SystemMetric
from .services import complete_backup, fail_backup, log_system_event
from .repositories import get_latest_metrics

logger = logging.getLogger(__name__)

# -------------------------------
# Simulated Backup Task
# -------------------------------
def run_backup_task(backup_id):
    """
    Simulates a backup operation.
    In production, replace this with actual backup logic (e.g., DB dump, file archiving).
    """
    try:
        logger.info(f"Starting backup task for ID {backup_id}")
        time.sleep(5)  # Simulate time-consuming backup

        # Simulated results
        file_path = f"/backups/backup_{backup_id}.zip"
        file_size = 1024 * 1024 * 50  # 50 MB
        metadata = {'simulated': True}

        complete_backup(backup_id, file_path, file_size, metadata)
        logger.info(f"Backup {backup_id} completed successfully")

    except Exception as e:
        logger.error(f"Backup {backup_id} failed: {str(e)}")
        fail_backup(backup_id, str(e))

# -------------------------------
# Periodic System Metric Snapshot
# -------------------------------
def collect_system_metrics():
    """
    Collects and stores system metrics.
    This can be scheduled to run periodically (e.g., every 15 minutes).
    """
    try:
        logger.info("Collecting system metrics")

        # Simulated metrics
        metrics = [
            {'name': 'active_users', 'value': 42, 'type': 'GAUGE'},
            {'name': 'error_logs_last_hour', 'value': 3, 'type': 'COUNTER'},
            {'name': 'avg_response_time_ms', 'value': 120.5, 'type': 'GAUGE'},
        ]

        for metric in metrics:
            SystemMetric.objects.create(
                metric_name=metric['name'],
                metric_value=metric['value'],
                metric_type=metric['type'],
                recorded_at=timezone.now()
            )

        logger.info("System metrics collected successfully")

    except Exception as e:
        logger.error(f"Metric collection failed: {str(e)}")
        log_system_event(
            level='ERROR',
            category='PERFORMANCE',
            message='Metric collection failed',
            metadata={'error': str(e)}
        )

# -------------------------------
# Log Rotation Task (Optional)
# -------------------------------
def rotate_old_logs(days=30):
    """
    Deletes system logs older than the specified number of days.
    Helps manage database size and performance.
    """
    from .models import SystemLog
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted, _ = SystemLog.objects.filter(created_at__lt=cutoff).delete()

    logger.info(f"Rotated {deleted} old system logs older than {days} days")
    return deleted
