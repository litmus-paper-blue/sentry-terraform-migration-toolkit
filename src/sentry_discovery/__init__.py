#!/usr/bin/env python3
"""
Sentry Terraform Discovery Tool

A tool to discover existing Sentry resources and generate Terraform configurations
for infrastructure-as-code migration.
"""

__version__ = "1.0.0"
__author__ = "Ogonna Nnamani"
__email__ = "ogonnannamani11@gmail.com"
__description__ = "Discover Sentry resources and generate Terraform configurations"

from .discovery import SentryDiscovery, SentryAPIError
from .config import Config, load_config, save_config
from .utils import (
    safe_resource_name,
    safe_filename,
    validate_token,
    setup_logging
)

__all__ = [
    "SentryDiscovery",
    "SentryAPIError", 
    "Config",
    "load_config",
    "save_config",
    "safe_resource_name",
    "safe_filename",
    "validate_token",
    "setup_logging",
]