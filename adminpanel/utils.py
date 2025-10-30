# adminpanel/utils.py

"""
Utility functions for adminpanel system operations.
Includes validators, formatters, and configuration sanity checks.
"""

import os
import ipaddress
from django.conf import settings
from django.db import connection
from .models import SystemConfiguration

# -------------------------------
# Configuration Validation
# -------------------------------
def validate_admin_configurations():
    """
    Validates critical system configurations at runtime.

    This function is safe to call from views, tasks, or commands.
    It checks for required keys and logs warnings if any are missing.

    ⚠️ Do NOT call this during app startup (e.g., in AppConfig.ready()).
    """
    # Ensure the table exists before querying
    if 'system_configurations' not in connection.introspection.table_names():
        return  # Table not ready — skip validation

    required_keys = ['SYSTEM_EMAIL', 'MAINTENANCE_MODE', 'MAX_BACKUP_SIZE_MB']
    missing_keys = []

    for key in required_keys:
        config = SystemConfiguration.objects.filter(key=key, is_active=True).first()
        if not config:
            missing_keys.append(key)

    if missing_keys:
        from .services import log_system_event
        log_system_event(
            level='WARNING',
            category='CONFIGURATION',
            message=f"Missing critical configuration keys: {', '.join(missing_keys)}",
            metadata={'missing_keys': missing_keys}
        )

# -------------------------------
# File Size Formatter
# -------------------------------
def format_file_size(bytes_size):
    """
    Converts file size in bytes to human-readable MB string.
    """
    if not bytes_size:
        return "0 MB"
    mb = round(bytes_size / (1024 * 1024), 2)
    return f"{mb} MB"

# -------------------------------
# Metadata Generator
# -------------------------------
def generate_backup_metadata(backup_type, user=None):
    """
    Generates structured metadata for a backup operation.
    """
    return {
        'backup_type': backup_type,
        'initiated_by': user.username if user else 'system',
        'timestamp': str(settings.TIME_ZONE),
        'environment': 'development' if settings.DEBUG else 'production'
    }

# -------------------------------
# IP Address Validator
# -------------------------------
def is_valid_ip(ip):
    """
    Validates IPv4 or IPv6 address format.
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# -------------------------------
# JSON Safe Extractor
# -------------------------------
def safe_json_extract(data, key, default=None):
    """
    Safely extracts a key from a JSON-like dict.
    """
    if isinstance(data, dict):
        return data.get(key, default)
    return default
