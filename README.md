# Universal Terraform Module Scanner (UTMS)

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A tool for scanning source code repositories to discover and analyze Terraform module references across multiple source providers (Azure DevOps, GitHub) with comprehensive reporting and cross-referencing capabilities.

## ✨ Features

- **Single-Repository Scanning**: Focused scanning of specific repositories per execution
- **Multi-Source Support**: Azure DevOps and GitHub fully supported
- **Version Checking**: Automatically detects outdated Git modules and compares against latest releases
- **Simple Authentication**: Token via CLI argument or environment variables
- **Comprehensive Scanning**: Discovers all Terraform module references (LOCAL, GIT) with detailed analysis
- **Module Source Types**: Supports local modules (./modules/vpc), Git modules (git::https://...), and semantic/Git versioning
- **Clean Output**: Minimal JSON format with only essential module information
- **Production Ready**: Robust error handling, logging, and progress tracking
- **Zero Dependencies**: Pure Python stdlib implementation for maximum compatibility

## 🚀 Quick Start

### Installation

```bash
# Download the executable (example - adjust URL to your distribution method)
wget utms  # or download from your preferred location
chmod +x utms
# Ready to use!
```

### Basic Usage

```bash
# Scan a specific repository in Azure DevOps
./utms --source azure-devops --organization my-org --project MyProject --repository my-repo

# With debug mode for troubleshooting
./utms --source azure-devops --organization my-org --project MyProject --repository my-repo --debug

# Clean existing result file before scanning
./utms --source azure-devops --organization my-org --project MyProject --repository my-repo --clean

# GitHub repository
./utms --source github --organization my-org --repository my-repo
```

## 📦 Module Detection

**Local Modules**: `./modules/vpc`, `../shared/network`, `/absolute/path`

**Git Modules**: `git::https://...`, `git::ssh://...`, `git@github.com:...`

**Versions**: Semantic (`1.0.0`, `~> 2.0`), Git tags/branches/commits

## 📋 Requirements

- Python 3.7+ (standard library only)
- PAT token with Repository Read permissions
- Network access to Azure DevOps or GitHub

## ⚙️ Performance

Concurrent processing (10 files), LRU caching (1000 entries), streaming for large files (>100KB), 1MB file limit, 30s timeout

## 🔐 Authentication

Two methods (tried in order):
1. `--token YOUR_TOKEN` (command line)
2. Environment variables: `AZURE_DEVOPS_PAT`, `AZURE_PAT`, `ADO_PAT`, `GITHUB_TOKEN`, `GH_TOKEN`

```bash
# Via environment
export AZURE_DEVOPS_PAT="your_token"
./utms --source azure-devops --organization my-org --project MyProject --repository my-repo

# Via CLI
./utms --source github --organization my-org --repository my-repo --token "your_token"
```

**Cross-Platform Module Version Checking**

When scanning Azure DevOps but your modules reference GitHub repositories (or vice versa), set both tokens:

```bash
# Scanning Azure DevOps with GitHub modules
export AZURE_DEVOPS_PAT="ado_token"
export GITHUB_TOKEN="github_token"
./utms --source azure-devops --organization my-org --project MyProject --repository my-repo

# Scanning GitHub with Azure DevOps modules
export GITHUB_TOKEN="github_token"
export AZURE_DEVOPS_PAT="ado_token"
./utms --source github --organization my-org --repository my-repo
```

This allows version checking for Git modules from any source, regardless of where you're scanning.

## 📊 Output Format

JSON files in `results/`: `{org}-{project}-{repo}.json` (Azure DevOps) or `{org}-{repo}.json` (GitHub)

```json
{
  "metadata": {
    "organization": "myorg",
    "project": "MyProject",
    "repository": "myrepo",
    "source_type": "azure-devops",
    "scan_timestamp": "2026-01-22T09:25:15.314161",
    "total_modules_found": 4,
    "total_files_scanned": 12
  },
  "modules": [
    {
      "file_path": "/terraform/core/main.tf",
      "local_name": "network",
      "source": "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=v5.0.0",
      "source_type": "git",
      "version": "v5.0.0",
      "latest_version": "v5.13.0",
      "is_outdated": true
    },
    {
      "file_path": "/terraform/core/main.tf",
      "local_name": "local_mod",
      "source": "./modules/local",
      "source_type": "local",
      "version": null,
      "latest_version": null,
      "is_outdated": null
    }
  ]
}
```

**Metadata Fields**:
- `organization`: Organization/owner name
- `project`: Project name (null for GitHub)
- `repository`: Repository name
- `source_type`: `azure-devops` or `github`
- `scan_timestamp`: ISO 8601 timestamp
- `total_modules_found`: Total modules in output (respects filters)
- `total_files_scanned`: Number of Terraform files scanned

**Module Fields**:
- `latest_version`: Latest release/tag from the Git repository (null for local modules or if unavailable)
- `is_outdated`: True if current version < latest version (null for local modules or if version not specified)

## 🛠️ Usage Examples

```bash
# Azure DevOps
./utms --source azure-devops --organization myorg --project MyProject --repository myrepo

# GitHub
./utms --source github --organization myorg --repository myrepo

# With options
./utms --source azure-devops --organization myorg --project MyProject --repository myrepo --token "token" --clean --debug

# Compliance reporting - show only outdated modules
./utms --source azure-devops --organization myorg --project MyProject --repository myrepo --filter outdated

# Compliance reporting - show only local modules
./utms --source azure-devops --organization myorg --project MyProject --repository myrepo --filter local

# Compliance reporting - show outdated OR local modules
./utms --source azure-devops --organization myorg --project MyProject --repository myrepo --filter outdated --filter local
```

**Filter Options:**
- `--filter outdated`: Show only Git modules where current version < latest version
- `--filter local`: Show only local modules (not from Git)
- Multiple filters can be specified (OR logic)

## 🏗️ Architecture

Single-responsibility design with authentication strategies, API client abstractions, centralized configuration, and comprehensive logging

## 🧪 Testing

```bash
python3 -m py_compile utms  # Syntax check
./utms --version            # Version
./utms --help               # Help
```

## 🔍 Troubleshooting

Use `--debug` for detailed logging. Common issues:
- **Auth failures**: Verify token and permissions
- **Repo not found**: Check names (case-sensitive) and access
- **Empty results**: Ensure `.tf` files exist and aren't ignored

## 📄 License

MIT License - see LICENSE file

## 👤 Author

fjdev - [GitHub](https://github.com/fjdev)
