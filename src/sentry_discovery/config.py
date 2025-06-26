#!/usr/bin/env python3
"""
Configuration management for Sentry Discovery Tool
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class SentryConfig:
    """Sentry API configuration"""
    token: Optional[str] = None
    base_url: str = "https://sentry.io/api/0"
    organization: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    is_self_hosted: bool = False  # New flag for self-hosted instances
    
    def __post_init__(self):
        # Load from environment if not set
        if not self.token:
            self.token = os.getenv("SENTRY_AUTH_TOKEN")
        if self.base_url == "https://sentry.io/api/0":
            self.base_url = os.getenv("SENTRY_BASE_URL", self.base_url)
        if not self.organization:
            self.organization = os.getenv("SENTRY_ORG")
        
        # Auto-detect self-hosted if not using sentry.io
        if "sentry.io" not in self.base_url:
            self.is_self_hosted = True

@dataclass
class TerraformConfig:
    """Terraform generation configuration"""
    output_dir: str = "./terraform"
    module_style: bool = False
    import_script: bool = True
    terraform_version: str = ">=1.0"
    provider_version: str = "~> 0.14.0"
    template_dir: Optional[str] = None
    
    # Resource naming
    resource_prefix: str = ""
    safe_naming: bool = True
    
    # Generation options
    include_comments: bool = True
    include_locals: bool = True
    include_outputs: bool = True

@dataclass
class OutputConfig:
    """Output formatting configuration"""
    format: str = "hcl"  # hcl, json, yaml
    dry_run: bool = False
    verbose: bool = False
    include_metadata: bool = True
    
    # File organization
    separate_files: bool = True  # Split into multiple .tf files
    file_naming: str = "resource_type"  # resource_type, alphabetical, custom

@dataclass
class FilterConfig:
    """Resource filtering configuration"""
    include_projects: list = field(default_factory=list)
    exclude_projects: list = field(default_factory=list)
    include_teams: list = field(default_factory=list)
    exclude_teams: list = field(default_factory=list)
    
    # Platform filtering
    include_platforms: list = field(default_factory=list)
    exclude_platforms: list = field(default_factory=list)
    
    # Status filtering
    include_active_only: bool = True

@dataclass
class Config:
    """Main configuration container"""
    sentry: SentryConfig = field(default_factory=SentryConfig)
    terraform: TerraformConfig = field(default_factory=TerraformConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'sentry': {
                'base_url': self.sentry.base_url,
                'organization': self.sentry.organization,
                'timeout': self.sentry.timeout,
                'retry_attempts': self.sentry.retry_attempts,
            },
            'terraform': {
                'output_dir': self.terraform.output_dir,
                'module_style': self.terraform.module_style,
                'import_script': self.terraform.import_script,
                'terraform_version': self.terraform.terraform_version,
                'provider_version': self.terraform.provider_version,
                'template_dir': self.terraform.template_dir,
                'resource_prefix': self.terraform.resource_prefix,
                'safe_naming': self.terraform.safe_naming,
                'include_comments': self.terraform.include_comments,
                'include_locals': self.terraform.include_locals,
                'include_outputs': self.terraform.include_outputs,
            },
            'output': {
                'format': self.output.format,
                'dry_run': self.output.dry_run,
                'verbose': self.output.verbose,
                'include_metadata': self.output.include_metadata,
                'separate_files': self.output.separate_files,
                'file_naming': self.output.file_naming,
            },
            'filters': {
                'include_projects': self.filters.include_projects,
                'exclude_projects': self.filters.exclude_projects,
                'include_teams': self.filters.include_teams,
                'exclude_teams': self.filters.exclude_teams,
                'include_platforms': self.filters.include_platforms,
                'exclude_platforms': self.filters.exclude_platforms,
                'include_active_only': self.filters.include_active_only,
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create config from dictionary"""
        config = cls()
        
        # Update sentry config
        if 'sentry' in data:
            sentry_data = data['sentry']
            config.sentry.base_url = sentry_data.get('base_url', config.sentry.base_url)
            config.sentry.organization = sentry_data.get('organization', config.sentry.organization)
            config.sentry.token = sentry_data.get('token', config.sentry.token)
            config.sentry.timeout = sentry_data.get('timeout', config.sentry.timeout)
            config.sentry.retry_attempts = sentry_data.get('retry_attempts', config.sentry.retry_attempts)
        
        # Update terraform config
        if 'terraform' in data:
            tf_data = data['terraform']
            config.terraform.output_dir = tf_data.get('output_dir', config.terraform.output_dir)
            config.terraform.module_style = tf_data.get('module_style', config.terraform.module_style)
            config.terraform.import_script = tf_data.get('import_script', config.terraform.import_script)
            config.terraform.terraform_version = tf_data.get('terraform_version', config.terraform.terraform_version)
            config.terraform.provider_version = tf_data.get('provider_version', config.terraform.provider_version)
            config.terraform.template_dir = tf_data.get('template_dir', config.terraform.template_dir)
            config.terraform.resource_prefix = tf_data.get('resource_prefix', config.terraform.resource_prefix)
            config.terraform.safe_naming = tf_data.get('safe_naming', config.terraform.safe_naming)
            config.terraform.include_comments = tf_data.get('include_comments', config.terraform.include_comments)
            config.terraform.include_locals = tf_data.get('include_locals', config.terraform.include_locals)
            config.terraform.include_outputs = tf_data.get('include_outputs', config.terraform.include_outputs)
        
        # Update output config
        if 'output' in data:
            output_data = data['output']
            config.output.format = output_data.get('format', config.output.format)
            config.output.dry_run = output_data.get('dry_run', config.output.dry_run)
            config.output.verbose = output_data.get('verbose', config.output.verbose)
            config.output.include_metadata = output_data.get('include_metadata', config.output.include_metadata)
            config.output.separate_files = output_data.get('separate_files', config.output.separate_files)
            config.output.file_naming = output_data.get('file_naming', config.output.file_naming)
        
        # Update filters config
        if 'filters' in data:
            filter_data = data['filters']
            config.filters.include_projects = filter_data.get('include_projects', config.filters.include_projects)
            config.filters.exclude_projects = filter_data.get('exclude_projects', config.filters.exclude_projects)
            config.filters.include_teams = filter_data.get('include_teams', config.filters.include_teams)
            config.filters.exclude_teams = filter_data.get('exclude_teams', config.filters.exclude_teams)
            config.filters.include_platforms = filter_data.get('include_platforms', config.filters.include_platforms)
            config.filters.exclude_platforms = filter_data.get('exclude_platforms', config.filters.exclude_platforms)
            config.filters.include_active_only = filter_data.get('include_active_only', config.filters.include_active_only)
        
        return config

def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file"""
    if config_path:
        config_file = Path(config_path)
    else:
        # Try default locations
        possible_configs = [
            Path.cwd() / ".sentry-discovery.yaml",
            Path.cwd() / ".sentry-discovery.yml",
            Path.home() / ".sentry-discovery.yaml",
            Path.home() / ".sentry-discovery.yml",
        ]
        config_file = None
        for path in possible_configs:
            if path.exists():
                config_file = path
                break
    
    if not config_file or not config_file.exists():
        return Config()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return Config()
        
        return Config.from_dict(data)
    
    except Exception as e:
        raise ValueError(f"Error loading config file {config_file}: {e}")

def save_config(config: Config, config_path: str):
    """Save configuration to file"""
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False, indent=2)
    except Exception as e:
        raise ValueError(f"Error saving config file {config_file}: {e}")

def get_default_config_paths() -> list:
    """Get list of default configuration file paths"""
    return [
        str(Path.cwd() / ".sentry-discovery.yaml"),
        str(Path.home() / ".sentry-discovery.yaml"),
    ]

def create_sample_config(output_path: str):
    """Create a sample configuration file"""
    config = Config()
    
    # Add some example values
    config.sentry.organization = "your-org-slug"
    config.terraform.module_style = True
    config.terraform.include_comments = True
    config.output.format = "hcl"
    config.output.separate_files = True
    
    # Add some example filters
    config.filters.exclude_platforms = ["native"]  # Example: exclude native apps
    config.filters.include_active_only = True
    
    save_config(config, output_path)

def validate_config(config: Config) -> list:
    """Validate configuration and return list of issues"""
    issues = []
    
    # Validate sentry config
    if not config.sentry.token:
        issues.append("Sentry auth token is required")
    
    if not config.sentry.base_url:
        issues.append("Sentry base URL is required")
    
    if config.sentry.timeout <= 0:
        issues.append("Sentry timeout must be positive")
    
    if config.sentry.retry_attempts < 0:
        issues.append("Sentry retry attempts must be non-negative")
    
    # Validate terraform config
    if not config.terraform.output_dir:
        issues.append("Terraform output directory is required")
    
    if config.terraform.template_dir and not Path(config.terraform.template_dir).exists():
        issues.append(f"Template directory does not exist: {config.terraform.template_dir}")
    
    # Validate output config
    if config.output.format not in ["hcl", "json", "yaml"]:
        issues.append("Output format must be 'hcl', 'json', or 'yaml'")
    
    if config.output.file_naming not in ["resource_type", "alphabetical", "custom"]:
        issues.append("File naming must be 'resource_type', 'alphabetical', or 'custom'")
    
    return issues