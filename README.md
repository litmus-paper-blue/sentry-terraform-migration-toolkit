# Sentry Terraform Discovery Tool

A Python tool to discover existing Sentry resources and generate Terraform configurations for infrastructure-as-code migration.

## 🎯 Purpose

This tool helps you migrate from manually managed Sentry projects, teams, and members to Terraform-managed infrastructure by:

- Discovering all existing Sentry resources via API
- Generating Terraform configuration files
- Creating import scripts for seamless migration
- Providing validation and best practices

## 📁 Repository Structure

```
sentry-terraform-discovery/
├── README.md                    # This file
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── .gitignore                  # Git ignore patterns
├── .github/                    # GitHub workflows
│   └── workflows/
│       └── ci.yml              # CI/CD pipeline
├── src/                        # Source code
│   └── sentry_discovery/
│       ├── __init__.py
│       ├── cli.py              # CLI interface
│       ├── discovery.py        # Main discovery logic
│       ├── terraform.py        # Terraform generation
│       ├── config.py           # Configuration management
│       └── utils.py            # Utility functions
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_discovery.py
│   ├── test_terraform.py
│   └── fixtures/               # Test data
│       └── sample_responses.json
├── examples/                   # Example configurations
│   ├── basic_usage.py
│   ├── custom_templates/
│   └── sample_outputs/
├── docs/                       # Documentation
│   ├── installation.md
│   ├── usage.md
│   ├── configuration.md
│   └── troubleshooting.md
├── scripts/                    # Utility scripts
│   ├── install.sh
│   └── validate_imports.sh
└── templates/                  # Terraform templates
    ├── project.tf.j2
    ├── team.tf.j2
    └── variables.tf.j2
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sentry-terraform-discovery.git
cd sentry-terraform-discovery

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Basic Usage

```bash
# Interactive mode
sentry-discovery

# Direct command
sentry-discovery --token YOUR_TOKEN --org your-org-slug

# Generate only specific resources
sentry-discovery --token YOUR_TOKEN --projects-only

# Use custom templates
sentry-discovery --token YOUR_TOKEN --template-dir ./custom-templates
```

### Configuration File

Create `~/.sentry-discovery.yaml`:

```yaml
sentry:
  base_url: "https://sentry.io/api/0"
  token: "your-token-here"  # Can also use env var SENTRY_AUTH_TOKEN
  organization: "your-default-org"

terraform:
  output_dir: "./terraform"
  module_style: true  # Generate modules vs flat files
  import_script: true

output:
  format: "hcl"  # hcl, json, yaml
  include_comments: true
  terraform_version: ">=1.0"
```

## 📖 Detailed Usage

### Command Line Options

```bash
sentry-discovery [OPTIONS]

Options:
  --token TEXT              Sentry auth token (or set SENTRY_AUTH_TOKEN)
  --base-url TEXT          Sentry base URL [default: https://sentry.io/api/0]
  --org TEXT               Organization slug
  --output-dir TEXT        Output directory [default: ./terraform]
  --config-file TEXT       Configuration file path
  --projects-only          Discover projects only
  --teams-only            Discover teams only
  --dry-run               Show what would be generated without writing files
  --template-dir TEXT     Custom template directory
  --format [hcl|json]     Output format [default: hcl]
  --verbose              Enable verbose logging
  --help                 Show this message and exit
```

### Environment Variables

```bash
export SENTRY_AUTH_TOKEN="your-token-here"
export SENTRY_BASE_URL="https://your-sentry.example.com/api/0"
export SENTRY_ORG="default-org"
```

## 🔧 Advanced Features

### Custom Templates

The tool uses Jinja2 templates for generating Terraform configurations. You can customize the output by providing your own templates:

```bash
sentry-discovery --template-dir ./my-templates
```

Template variables available:
- `organization`: Organization data
- `projects`: List of projects
- `teams`: List of teams
- `members`: List of team members

### Module Generation

Generate reusable Terraform modules:

```bash
sentry-discovery --module-style
```

This creates:
```
terraform/
├── modules/
│   ├── sentry-project/
│   ├── sentry-team/
│   └── sentry-member/
└── environments/
    └── production/
        └── main.tf
```

### Validation

Validate your existing Terraform state against Sentry:

```bash
sentry-discovery --validate --terraform-dir ./existing-terraform
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/sentry_discovery

# Run specific test
pytest tests/test_discovery.py::TestSentryAPI::test_get_projects
```

## 📊 Output Examples

### Generated Files

- `terraform/main.tf` - Main Terraform configuration
- `terraform/variables.tf` - Variable definitions
- `terraform/outputs.tf` - Output values
- `terraform/imports.sh` - Import script
- `terraform/README.md` - Usage instructions

### Sample Output Structure

```hcl
# Generated Terraform configuration
resource "sentry_team" "backend_team" {
  organization = var.sentry_org_slug
  name         = "Backend Team"
  slug         = "backend-team"
}

resource "sentry_project" "api_service" {
  organization = var.sentry_org_slug
  name         = "API Service"
  slug         = "api-service"
  platform     = "python"
  teams        = [sentry_team.backend_team.id]
}
```

## 🔒 Security Considerations

- Never commit auth tokens to version control
- Use environment variables or secure secret management
- Rotate tokens regularly
- Use minimal required permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/sentry-terraform-discovery.git

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 🐛 Troubleshooting

### Common Issues

**Authentication Error**
```
Error: 401 Unauthorized
```
- Verify your auth token is correct and has proper permissions
- Check if token has expired

**Organization Not Found**
```
Error: Organization 'my-org' not found
```
- Verify organization slug is correct
- Ensure your token has access to the organization

**Import Failures**
```
Error: Resource already exists
```
- Check if resources are already managed by Terraform
- Use `terraform import` with `--force` flag if needed

### Debug Mode

```bash
sentry-discovery --verbose --dry-run
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Sentry](https://sentry.io/) for the excellent error tracking platform
- [Terraform Sentry Provider](https://github.com/jianyuan/terraform-provider-sentry) by @jianyuan
- Community contributors and feedback

---

**Need help?** Open an issue or start a discussion!