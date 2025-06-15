#!/usr/bin/env python3
"""
Utility functions for Sentry Discovery Tool
"""

import re
import logging
import sys
from typing import Optional, Dict, Any
from pathlib import Path

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)
    
    # Reduce noise from requests library
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def validate_token(token: str) -> bool:
    """Validate Sentry auth token format"""
    if not token:
        return False
    
    # Sentry tokens are typically 64 character hex strings
    # or can be in the format of "sntrys_..." for newer tokens
    if len(token) == 64 and re.match(r'^[a-f0-9]+$', token):
        return True
    
    if token.startswith('sntrys_') and len(token) > 20:
        return True
    
    return False

def safe_filename(name: str) -> str:
    """Convert string to safe filename"""
    # Replace invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Replace spaces with underscores
    safe = safe.replace(' ', '_')
    # Remove multiple underscores
    safe = re.sub(r'_+', '_', safe)
    # Remove leading/trailing underscores
    safe = safe.strip('_')
    # Ensure it's not empty
    return safe or 'unnamed'

def safe_resource_name(name: str) -> str:
    """Convert name to Terraform-safe resource name"""
    # Convert to lowercase
    safe = name.lower()
    # Replace non-alphanumeric with underscores
    safe = re.sub(r'[^a-z0-9_]', '_', safe)
    # Remove multiple underscores
    safe = re.sub(r'_+', '_', safe)
    # Remove leading/trailing underscores
    safe = safe.strip('_')
    # Ensure it starts with letter or underscore
    if safe and safe[0].isdigit():
        safe = f'_{safe}'
    # Ensure it's not empty
    return safe or 'unnamed'

def ensure_directory(path: str) -> Path:
    """Ensure directory exists and return Path object"""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def format_bytes(bytes_count: int) -> str:
    """Format bytes in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"

def truncate_string(text: str, max_length: int = 50) -> str:
    """Truncate string with ellipsis if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def extract_org_from_url(url: str) -> Optional[str]:
    """Extract organization slug from Sentry URL"""
    # Match patterns like https://sentry.io/organizations/my-org/
    pattern = r'sentry\.io/organizations/([^/]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def sanitize_terraform_string(value: str) -> str:
    """Sanitize string for use in Terraform configuration"""
    # Escape special characters
    escaped = value.replace('\\', '\\\\')
    escaped = escaped.replace('"', '\\"')
    escaped = escaped.replace('\n', '\\n')
    escaped = escaped.replace('\r', '\\r')
    escaped = escaped.replace('\t', '\\t')
    return escaped

def generate_import_id(org_slug: str, resource_type: str, resource_slug: str, extra: str = None) -> str:
    """Generate Terraform import ID for Sentry resources"""
    if resource_type == 'team_member' and extra:
        return f"{org_slug}/{resource_slug}/{extra}"
    return f"{org_slug}/{resource_slug}"

class ProgressTracker:
    """Simple progress tracking utility"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
    
    def update(self, step: int = None, description: str = None):
        """Update progress"""
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
        
        if description:
            self.description = description
        
        percentage = (self.current_step / self.total_steps) * 100
        print(f"\r{self.description}: {percentage:.1f}% ({self.current_step}/{self.total_steps})", end='', flush=True)
    
    def finish(self, final_message: str = "Complete"):
        """Finish progress tracking"""
        print(f"\r{final_message}: 100.0% ({self.total_steps}/{self.total_steps})")

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file safely"""
    import json
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Error loading JSON file {file_path}: {e}")

def save_json_file(data: Dict[str, Any], file_path: str, indent: int = 2):
    """Save data to JSON file safely"""
    import json
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"Error saving JSON file {file_path}: {e}")

def get_file_hash(file_path: str) -> str:
    """Get SHA256 hash of file"""
    import hashlib
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def check_terraform_installed() -> bool:
    """Check if Terraform is installed and accessible"""
    import subprocess
    try:
        result = subprocess.run(['terraform', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def get_terraform_version() -> Optional[str]:
    """Get installed Terraform version"""
    import subprocess
    try:
        result = subprocess.run(['terraform', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Extract version from output like "Terraform v1.5.0"
            match = re.search(r'Terraform v(\d+\.\d+\.\d+)', result.stdout)
            return match.group(1) if match else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None

def validate_terraform_syntax(file_path: str) -> bool:
    """Validate Terraform file syntax"""
    import subprocess
    try:
        # Change to directory containing the file
        file_dir = Path(file_path).parent
        result = subprocess.run(['terraform', 'validate'], 
                              cwd=file_dir, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def get_env_bool(env_var: str, default: bool = False) -> bool:
    """Get boolean value from environment variable"""
    import os
    value = os.getenv(env_var, '').lower()
    if value in ('true', '1', 'yes', 'on'):
        return True
    elif value in ('false', '0', 'no', 'off'):
        return False
    return default

def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function on exception"""
    import time
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        raise e
                    
                    print(f"Attempt {retries} failed: {e}. Retrying in {current_delay} seconds...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator

def find_files_by_pattern(directory: str, pattern: str) -> list:
    """Find files matching pattern in directory"""
    import glob
    search_pattern = str(Path(directory) / pattern)
    return glob.glob(search_pattern, recursive=True)

def backup_file(file_path: str) -> str:
    """Create backup of file with timestamp"""
    import shutil
    from datetime import datetime
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(f".{timestamp}.backup{path.suffix}")
    
    shutil.copy2(file_path, backup_path)
    return str(backup_path)