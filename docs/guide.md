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
- Sentry auth token
- Git (for version control)

## Step-by-Step Guide

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd sentry-instance-discovery-tool

# Install the tool
make install-dev
```

### 2. Configuration

Create a `.sentry-discovery.yaml` file in your project root:

```yaml
sentry:
  base_url: "https://your-sentry-instance/api/0"  # For self-hosted Sentry
  token: "${SENTRY_AUTH_TOKEN}"  # Use environment variable for security
  organization: "your-org-slug"

terraform:
  output_dir: "./terraform"
  module_style: true  # Generate modules vs flat files
  import_script: true

output:
  format: "hcl"  # hcl, json, yaml
  include_comments: true
  terraform_version: ">=1.0"
```

### 3. Set Environment Variables

```bash
# Set your Sentry auth token
export SENTRY_AUTH_TOKEN="your-token-here"
```

### 4. Discovery and Generation

```bash
# Run the discovery tool with verbose output
sentry-discovery --verbose

# This will create:
# - terraform/main.tf          (Provider configuration)
# - terraform/variables.tf     (Variable definitions)
# - terraform/teams.tf         (Team resources)
# - terraform/projects.tf      (Project resources)
# - terraform/imports.sh       (Import script)
```

### 5. Review Generated Files

1. **main.tf**: Contains provider configuration
2. **variables.tf**: Defines required variables
3. **teams.tf**: Sentry team resources
4. **projects.tf**: Sentry project resources
5. **imports.sh**: Import script for existing resources

### 6. Initialize Terraform

```bash
cd terraform
terraform init
```

### 7. Import Existing Resources

```bash
# Make the import script executable
chmod +x imports.sh

# Run the import script
./imports.sh
```

### 8. Verify Imports

```bash
# Check that everything imported correctly
terraform plan
```

You should see "No changes. Your infrastructure matches the configuration."

### 9. Start Managing with Terraform

From this point on, you can use Terraform to manage your Sentry resources:

```bash
# Make changes through Terraform
terraform plan    # Preview changes
terraform apply   # Apply changes
```

## Common Issues and Solutions

### 1. Authentication Issues
- Ensure your token has sufficient permissions
- For self-hosted Sentry, verify the base URL is correct
- Check that the token format is correct (no spaces or prefixes)

### 2. Import Errors
- Verify organization slug is correct
- Ensure resources exist in Sentry
- Check import ID format (should be `organization/resource-slug`)

### 3. Base URL Format
- Self-hosted Sentry: `https://your-sentry-instance`
- Cloud Sentry: `https://sentry.io`
- Don't include `/api/0` in base URL (provider adds this automatically)

## Best Practices

1. **Version Control**
   - Commit generated Terraform files to Git
   - Exclude sensitive files (terraform.tfstate, .sentry-discovery.yaml)

2. **Security**
   - Use environment variables for sensitive values
   - Don't commit tokens to version control
   - Use separate tokens for different environments

3. **Organization**
   - Use consistent naming for resources
   - Group related resources together
   - Use descriptive comments

4. **Workflow**
   - Always review generated configurations
   - Test imports in a non-production environment first
   - Use `terraform plan` before applying changes

## Maintenance

After initial import:
1. Use Terraform for all Sentry changes
2. Keep configurations in version control
3. Use CI/CD for automated deployments
4. Regularly update provider and Terraform versions

## Reference

### Command Line Options
```bash
sentry-discovery [OPTIONS]

Options:
  --token TEXT              Sentry auth token
  --base-url TEXT          Sentry base URL
  --org TEXT               Organization slug
  --output-dir TEXT        Output directory
  --config-file TEXT       Config file path
  --projects-only          Only discover projects
  --teams-only            Only discover teams
  --dry-run               Show what would be generated
  --verbose              Enable verbose logging
```

### Resource Types
- Teams
- Projects
- Team Members
- Project Settings

### File Structure
```
terraform/
├── main.tf           # Provider configuration
├── variables.tf      # Variable definitions
├── teams.tf         # Team resources
├── projects.tf      # Project resources
└── imports.sh       # Import script
```

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Enable verbose logging with `--verbose`
3. Review error messages carefully
4. Check Sentry API documentation
5. Open an issue in the repository
