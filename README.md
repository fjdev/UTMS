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

## 🔄 CI/CD Integration

### Azure Pipelines Example

```yaml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - '**/*.tf'
      - '**/*.tfvars'

schedules:
  - cron: "0 2 * * 1"
    displayName: Weekly module compliance scan
    branches:
      include:
        - main
    always: true

pr:
  branches:
    include:
      - main

variables:
  UTMS_VERSION: 'v2.0.0'
  FAIL_ON_OUTDATED: 'false'

jobs:
- job: Scan
  displayName: Terraform Module Compliance Scan
  pool:
    vmImage: 'ubuntu-latest'
  steps:
  - checkout: self
    persistCredentials: true

  - task: UsePythonVersion@0
    displayName: Use Python 3.x
    inputs:
      versionSpec: '3.x'

  - script: |
      curl -sSfL "https://raw.githubusercontent.com/fjdev/UTMS/$(UTMS_VERSION)/utms" -o utms
      chmod +x utms
    displayName: Download UTMS

  - script: |
      COLLECTION_URI="$(System.TeamFoundationCollectionUri)"
      COLLECTION_URI="${COLLECTION_URI%/}"
      ORGANIZATION="${COLLECTION_URI##*/}"

      PROJECT="$(System.TeamProject)"
      REPOSITORY="$(Build.Repository.Name)"
      BRANCH="$(Build.SourceBranchName)"

      ./utms --source azure-devops --organization "$ORGANIZATION" --project "$PROJECT" --repository "$REPOSITORY" --clean
    displayName: Run UTMS Module Scan
    env:
      AZURE_DEVOPS_PAT: $(System.AccessToken)
      GITHUB_TOKEN: $(GITHUB_TOKEN)

  - script: |
      cat > generate_report.py << 'EOF'
      import json
      import os
      import sys
      import urllib.parse
      from datetime import datetime, timezone
      from zoneinfo import ZoneInfo
      from pathlib import Path

      result_file = Path("results").glob("*.json").__next__()
      with open(result_file) as f:
          data = json.load(f)

      metadata = data.get("metadata", {})
      modules = data.get("modules", [])

      collection_uri = (os.environ.get("SYSTEM_COLLECTIONURI") or "").rstrip("/")
      organization = collection_uri.split("/")[-1] if collection_uri else metadata.get("organization", "")
      project = os.environ.get("SYSTEM_TEAMPROJECT") or metadata.get("project", "")
      repository = os.environ.get("BUILD_REPOSITORY_NAME") or metadata.get("repository", "")
      branch = os.environ.get("BUILD_SOURCEBRANCHNAME") or "main"

      def file_link(path: str) -> str:
          clean_path = path.lstrip("/")
          if not (collection_uri and project and repository):
              return f"`{clean_path}`"
          path_q = urllib.parse.quote("/" + clean_path, safe="")
          branch_q = urllib.parse.quote(branch, safe="")
          url = f"{collection_uri}/{project}/_git/{repository}?path={path_q}&version=GB{branch_q}"
          return f"[`{clean_path}`]({url})"

      def format_scan_date(ts: str) -> str:
          if not ts:
              return "N/A"
          try:
              dt = datetime.fromisoformat(ts)
              if dt.tzinfo is None:
                  dt = dt.replace(tzinfo=timezone.utc)
              ams = dt.astimezone(ZoneInfo("Europe/Amsterdam"))
              return ams.strftime("%Y-%m-%d %H:%M %Z")
          except Exception:
              return ts

      scan_date = format_scan_date(metadata.get("scan_timestamp", ""))

      # Generate markdown report
      with open("module-report.md", "w") as report:
          report.write(f"# Terraform Module Compliance Report\n\n")
          report.write(f"**Repository:** {metadata.get('organization')}/{metadata.get('repository')}\n")
          report.write(f"**Scan Date:** {scan_date}\n")
          report.write(f"**Total Modules:** {metadata.get('total_modules_found', 0)}\n\n")
          
          # Summary statistics
          outdated = [m for m in modules if m.get("is_outdated")]
          local = [m for m in modules if m.get("source_type") == "local"]
          uptodate = [m for m in modules if m.get("source_type") == "git" and not m.get("is_outdated")]
          
          report.write(f"## Summary\n\n")
          report.write(f"- ✅ Up-to-date: {len(uptodate)}\n")
          report.write(f"- ⚠️  Outdated: {len(outdated)}\n")
          report.write(f"- 📁 Local: {len(local)}\n\n")
          
          # Detailed table
          report.write(f"## Module Details\n\n")
          report.write(f"| Status | File | Module | Source | Current | Latest |\n")
          report.write(f"|--------|------|--------|--------|---------|--------|\n")
          
          for module in sorted(modules, key=lambda m: (m.get("file_path", ""), m.get("local_name", ""))):
              file_path = module.get("file_path", "")
              local_name = module.get("local_name", "")
              source = module.get("source", "")[:50] + "..." if len(module.get("source", "")) > 50 else module.get("source", "")
              current = module.get("version") or "-"
              latest = module.get("latest_version") or "-"
              
              if module.get("is_outdated"):
                  status = "⚠️ OUTDATED"
              elif module.get("source_type") == "local":
                  status = "📁 LOCAL"
              else:
                  status = "✅ UP-TO-DATE"
              
              report.write(f"| {status} | {file_link(file_path)} | {local_name} | {source} | {current} | {latest} |\n")

      print(f"Report generated: {len(modules)} modules")
      print(f"  Up-to-date: {len(uptodate)}")
      print(f"  Outdated: {len(outdated)}")
      print(f"  Local: {len(local)}")
      sys.exit(1 if len(outdated) > 0 and "$(FAIL_ON_OUTDATED)" == "true" else 0)
      EOF
      python3 generate_report.py
    displayName: Generate markdown report
    condition: always()

  # Render markdown report directly in the pipeline summary
  - script: |
      echo "##vso[task.uploadsummary]$(System.DefaultWorkingDirectory)/module-report.md"
    displayName: Publish report to pipeline summary
    condition: always()

  - task: PublishBuildArtifacts@1
    displayName: Publish scan results
    inputs:
      PathtoPublish: 'results'
      ArtifactName: 'module-scan-results'
    condition: always()
```

The pipeline generates both JSON (for automation) and a markdown report (for humans) with:
- Summary statistics (up-to-date, outdated, local counts)
- Detailed table with status flags (⚠️ OUTDATED, 📁 LOCAL, ✅ UP-TO-DATE)
- Published as build artifacts

Set `FAIL_ON_OUTDATED: 'true'` to enforce module version compliance.

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
