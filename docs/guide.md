# Sentry Terraform Discovery Tool Guide

This guide explains how to use the Sentry Terraform Discovery tool to import your existing Sentry setup into Terraform.

## Overview

The Sentry Terraform Discovery tool helps you:
1. Discover existing Sentry resources (teams, projects, members)
2. Generate Terraform configurations
3. Create import scripts
4. Migrate to Infrastructure as Code

## Prerequisites

- Python 3.8 or higher
- Terraform installed
- Sentry auth token (see below for config)
- Git (for version control)

## Step-by-Step Guide

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/litmus-paper-blue/sentry-terraform-migration-toolkit.git
cd sentry-instance-discovery-tool

# Install the tool
make install-dev
```

### 2. Configuration

Create a `.sentry-discovery.yaml` file in your project root **(required)**:

```yaml
sentry:
  base_url: "https://your-sentry-instance/api/0"  # For self-hosted Sentry
  token: "your-token-here"  # Required, or set SENTRY_AUTH_TOKEN env var
  organization: "your-org-slug"

terraform:
  output_dir: "./terraform"
  import_script: true

output:
  format: "hcl"  # hcl, json, yaml
  terraform_version: ">=1.0"
```

- The `token` field is **required** in the config file, or you must set the `SENTRY_AUTH_TOKEN` environment variable.
- The config file is loaded first; CLI options only override if explicitly set.
- You will only be prompted if the output directory already exists and would be overwritten.

### 3. Set Environment Variables (Optional)

```bash
# Set your Sentry auth token (if not in config file)
export SENTRY_AUTH_TOKEN="your-token-here"
```

### 4. Discovery and Generation

```bash
# Run the discovery tool with verbose output
sentry-discovery --verbose

# You can also override config values via CLI:
sentry-discovery --token YOUR_TOKEN --org your-org-slug
```

- The tool will generate:
  - `terraform/main.tf`          (Provider configuration)
  - `terraform/variables.tf`     (Variable definitions)
  - `terraform/teams.tf`         (Team resources)
  - `terraform/projects.tf`      (Project resources)
  - `terraform/imports.sh`       (Import script)

### 5. Docker Usage

You can run the tool in Docker, mounting your config and output directories:

```bash
docker run --rm -it \
  -v $(pwd)/.sentry-discovery.yaml:/app/.sentry-discovery.yaml \
  -v $(pwd)/terraform:/app/terraform \
  -e SENTRY_AUTH_TOKEN \
  sentry-terraform-discovery:latest
```

### 6. Review Generated Files

1. **main.tf**: Contains provider configuration
2. **variables.tf**: Defines required variables
3. **teams.tf**: Sentry team resources
4. **projects.tf**: Sentry project resources
5. **imports.sh**: Import script for existing resources

### 7. Initialize Terraform

```bash
cd terraform
terraform init
```

### 8. Import Existing Resources

```bash
chmod +x imports.sh
./imports.sh
```

### 9. Verify Imports

```bash
terraform plan
```

You should see "No changes. Your infrastructure matches the configuration."

### 10. Start Managing with Terraform

```bash
terraform plan    # Preview changes
terraform apply   # Apply changes
```

## Configuration Precedence

- The tool loads `.sentry-discovery.yaml` first.
- CLI options only override config file values if explicitly set.
- Prompts only occur for output directory conflicts.

## Troubleshooting

- **Token Issues:** Ensure your token is present in the config file or as `SENTRY_AUTH_TOKEN`. The token must be valid for your Sentry instance (self-hosted or SaaS).
- **Base URL:** For self-hosted Sentry, set the correct `base_url` (e.g., `https://your-sentry-instance/api/0`).
- **Import Errors:** Check that your organization slug and resource slugs are correct. The tool now generates import commands using the correct `org_slug/project_slug` format.
- **Makefile:** Use `make` commands for development, testing, and linting (see `Makefile`).

## Need help?
Open an issue or start a discussion!
