#!/usr/bin/env python3
"""
CLI interface for Sentry Terraform Discovery Tool
"""

import click
import os
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from .discovery import SentryDiscovery
from .terraform import TerraformGenerator
from .config import Config, load_config
from .utils import setup_logging, validate_token

console = Console()

@click.command()
@click.option(
    "--token",
    envvar="SENTRY_AUTH_TOKEN",
    help="Sentry auth token (or set SENTRY_AUTH_TOKEN env var)",
)
@click.option(
    "--base-url",
    envvar="SENTRY_BASE_URL",
    default="https://sentry.io/api/0",
    help="Sentry base URL",
)
@click.option(
    "--org",
    envvar="SENTRY_ORG",
    help="Organization slug",
)
@click.option(
    "--output-dir",
    default="./terraform",
    help="Output directory for generated files",
)
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Configuration file path",
)
@click.option(
    "--projects-only",
    is_flag=True,
    help="Discover projects only",
)
@click.option(
    "--teams-only",
    is_flag=True,
    help="Discover teams only",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be generated without writing files",
)
@click.option(
    "--template-dir",
    type=click.Path(exists=True),
    help="Custom template directory",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["hcl", "json"]),
    default="hcl",
    help="Output format",
)
@click.option(
    "--module-style",
    is_flag=True,
    help="Generate Terraform modules",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.option(
    "--validate",
    is_flag=True,
    help="Validate against existing Terraform state",
)
@click.option(
    "--terraform-dir",
    type=click.Path(exists=True),
    help="Existing Terraform directory for validation",
)
def main(
    token: Optional[str],
    base_url: str,
    org: Optional[str],
    output_dir: str,
    config_file: Optional[str],
    projects_only: bool,
    teams_only: bool,
    dry_run: bool,
    template_dir: Optional[str],
    output_format: str,
    module_style: bool,
    verbose: bool,
    validate: bool,
    terraform_dir: Optional[str],
):
    """
    Sentry Terraform Discovery Tool
    Discover existing Sentry resources and generate Terraform configurations
    for infrastructure-as-code migration.
    """
    setup_logging(verbose)

    # 1. Load config file if present, else use defaults
    config = load_config(config_file) if config_file else load_config()
    print("DEBUG: Loaded token from config:", config.sentry.token)

    # 2. Only override config values if CLI options are explicitly set (not just their default)
    # Use Click's 'ctx.get_parameter_source' to check if a value was set by the user
    import click
    ctx = click.get_current_context()
    
    if ctx.get_parameter_source('token').name == 'COMMANDLINE':
        config.sentry.token = token
    if ctx.get_parameter_source('base_url').name == 'COMMANDLINE':
        config.sentry.base_url = base_url
    if ctx.get_parameter_source('org').name == 'COMMANDLINE':
        config.sentry.organization = org
    if ctx.get_parameter_source('output_dir').name == 'COMMANDLINE':
        config.terraform.output_dir = output_dir
    if ctx.get_parameter_source('template_dir').name == 'COMMANDLINE':
        config.terraform.template_dir = template_dir
    if ctx.get_parameter_source('output_format').name == 'COMMANDLINE':
        config.output.format = output_format
    if ctx.get_parameter_source('module_style').name == 'COMMANDLINE':
        config.terraform.module_style = module_style
    if ctx.get_parameter_source('dry_run').name == 'COMMANDLINE':
        config.output.dry_run = dry_run

    # 3. Only prompt for output-dir if it exists and is not empty
    from pathlib import Path
    output_path = Path(config.terraform.output_dir)
    if output_path.exists() and any(output_path.iterdir()):
        config.terraform.output_dir = get_output_directory(str(output_path))

    # 4. Validate required parameters (prompt only if missing)
    if not config.sentry.token:
        if not sys.stdin.isatty():
            console.print("❌ [red]Auth token is required. Set SENTRY_AUTH_TOKEN or use --token[/red]")
            sys.exit(1)
        config.sentry.token = click.prompt("Enter your Sentry Auth Token", hide_input=True)

    if not validate_token(config.sentry.token):
        console.print("❌ [red]Invalid token format[/red]")
        sys.exit(1)

    if verbose:
        show_config(config)

    try:
        # Initialize discovery
        discovery = SentryDiscovery(
            auth_token=config.sentry.token,
            base_url=config.sentry.base_url,
            verbose=verbose
        )
        
        # Discover resources
        console.print(Panel.fit("🔍 [bold blue]Discovering Sentry Resources[/bold blue]"))
        
        with Progress() as progress:
            task = progress.add_task("Discovering...", total=100)
            
            # Discover all resources
            data = discovery.discover_all(
                target_org_slug=config.sentry.organization,
                projects_only=projects_only,
                teams_only=teams_only,
                progress_callback=lambda p: progress.update(task, completed=p)
            )
        
        if not data:
            console.print("❌ [red]Failed to discover resources[/red]")
            sys.exit(1)
        
        # Show summary
        show_discovery_summary(data)
        
        # Generate Terraform configurations
        if not validate:
            console.print(Panel.fit("📝 [bold green]Generating Terraform Configurations[/bold green]"))
            
            generator = TerraformGenerator(config)
            
            if dry_run:
                console.print("🔍 [yellow]Dry run mode - showing what would be generated:[/yellow]")
                generator.preview(data)
            else:
                output_files = generator.generate(data)
                show_generated_files(output_files)
                show_next_steps(output_files)
        
        # Validation mode
        if validate:
            if not terraform_dir:
                console.print("❌ [red]--terraform-dir required for validation[/red]")
                sys.exit(1)
            
            console.print(Panel.fit("✅ [bold purple]Validating Terraform State[/bold purple]"))
            # TODO: Implement validation logic
            console.print("🚧 [yellow]Validation feature coming soon![/yellow]")
    
    except KeyboardInterrupt:
        console.print("\n❌ [red]Operation cancelled by user[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)

def get_output_directory(default_dir: str) -> str:
    """Get output directory with interactive prompts for conflicts"""
    import sys
    from datetime import datetime
    from pathlib import Path
    
    while True:
        if sys.stdin.isatty():  # Interactive terminal
            output_dir = input(f"Enter output directory (default: {default_dir}): ").strip()
            if not output_dir:
                output_dir = default_dir
        else:
            # Non-interactive mode
            output_dir = default_dir
        
        output_path = Path(output_dir)
        
        if output_path.exists() and any(output_path.iterdir()):
            if sys.stdin.isatty():
                print(f"\n⚠️  Directory '{output_dir}' already exists and is not empty!")
                print(f"Contents: {len(list(output_path.iterdir()))} files/folders")
                choice = input("Choose action: (r)eplace, (m)erge, (n)ew directory, (a)bort: ").lower().strip()
                
                if choice in ['r', 'replace']:
                    # Create backup of existing directory
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_dir = Path(f"{output_dir}_backup_{timestamp}")
                    output_path.rename(backup_dir)
                    print(f"📁 Backup created: {backup_dir}")
                    return output_dir
                elif choice in ['m', 'merge']:
                    print(f"📁 Merging into existing directory: {output_dir}")
                    return output_dir
                elif choice in ['n', 'new', 'new directory']:
                    continue  # Ask for new directory name
                else:  # abort
                    print("❌ Operation aborted")
                    sys.exit(1)
            else:
                # Non-interactive mode, auto-rename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = f"{default_dir}_{timestamp}"
                print(f"📁 Auto-renamed to: {output_dir}")
                return output_dir
        else:
            return output_dir

def show_config(config: Config):
    """Display current configuration"""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Base URL", config.sentry.base_url)
    table.add_row("Organization", config.sentry.organization or "Auto-detect")
    table.add_row("Output Directory", config.terraform.output_dir)
    table.add_row("Output Format", config.output.format)
    table.add_row("Module Style", "Yes" if config.terraform.module_style else "No")
    table.add_row("Dry Run", "Yes" if config.output.dry_run else "No")
    
    console.print(table)
    console.print()

def detect_version_changes(output_dir: str) -> bool:
    """Detect if this is a new version of discovery data"""
    import json
    from pathlib import Path
    from datetime import datetime
    
    metadata_file = Path(output_dir) / ".sentry-discovery-metadata.json"
    
    current_metadata = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",  # Tool version
        "discovery_id": datetime.now().strftime("%Y%m%d_%H%M%S")
    }
    
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r') as f:
                previous_metadata = json.load(f)
            
            # Check if significant time has passed (new discovery session)
            from datetime import datetime, timedelta
            prev_time = datetime.fromisoformat(previous_metadata["timestamp"])
            current_time = datetime.now()
            
            if current_time - prev_time > timedelta(hours=1):
                print(f"🔄 New discovery session detected")
                print(f"   Previous: {prev_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Current:  {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                return True
        except Exception as e:
            print(f"⚠️  Could not read previous metadata: {e}")
    
    # Save current metadata
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        with open(metadata_file, 'w') as f:
            json.dump(current_metadata, f, indent=2)
    except Exception as e:
        print(f"⚠️  Could not save metadata: {e}")
    
    return False
    """Display current configuration"""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Base URL", config.sentry.base_url)
    table.add_row("Organization", config.sentry.organization or "Auto-detect")
    table.add_row("Output Directory", config.terraform.output_dir)
    table.add_row("Output Format", config.output.format)
    table.add_row("Module Style", "Yes" if config.terraform.module_style else "No")
    table.add_row("Dry Run", "Yes" if config.output.dry_run else "No")
    
    console.print(table)
    console.print()

def show_discovery_summary(data: dict):
    """Display summary of discovered resources"""
    org = data.get('organization', {})
    teams = data.get('teams', [])
    projects = data.get('projects', [])
    
    # Summary table
    table = Table(title=f"📊 Discovery Summary - {org.get('name', 'Unknown')} ({org.get('slug', 'unknown')})")
    table.add_column("Resource Type", style="cyan")
    table.add_column("Count", style="green", justify="right")
    table.add_column("Details", style="yellow")
    
    # Team details
    team_members = sum(len(team.get('members', [])) for team in teams)
    table.add_row("Teams", str(len(teams)), f"{team_members} total members")
    
    # Project details
    project_platforms = {}
    for project in projects:
        platform = project.get('platform', 'unknown')
        project_platforms[platform] = project_platforms.get(platform, 0) + 1
    
    platform_summary = ", ".join(f"{count} {platform}" for platform, count in project_platforms.items())
    table.add_row("Projects", str(len(projects)), platform_summary)
    
    console.print(table)
    console.print()

def show_generated_files(output_files: list):
    """Display list of generated files"""
    if not output_files:
        console.print("⚠️  [yellow]No files generated[/yellow]")
        return
    
    table = Table(title="📁 Generated Files")
    table.add_column("File", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Size", style="yellow", justify="right")
    
    for file_path in output_files:
        path = Path(file_path)
        file_type = "Terraform" if path.suffix == ".tf" else "Script" if path.suffix == ".sh" else "Other"
        size = f"{path.stat().st_size:,} bytes" if path.exists() else "Unknown"
        table.add_row(str(path), file_type, size)
    
    console.print(table)
    console.print()

def show_next_steps(output_files: list):
    """Display next steps for the user"""
    console.print(Panel.fit("🚀 [bold green]Next Steps[/bold green]"))
    
    steps = [
        "1. Review the generated Terraform configuration files",
        "2. Initialize Terraform: [bold cyan]terraform init[/bold cyan]",
        "3. Run the import script: [bold cyan]chmod +x imports.sh && ./imports.sh[/bold cyan]",
        "4. Verify the import: [bold cyan]terraform plan[/bold cyan]",
        "5. Apply if everything looks good: [bold cyan]terraform apply[/bold cyan]"
    ]
    
    for step in steps:
        console.print(f"   {step}")
    
    console.print()
    console.print("💡 [blue]Tip: Run with --dry-run first to preview changes[/blue]")

if __name__ == "__main__":
    main()