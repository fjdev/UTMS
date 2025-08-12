# Universal Terraform Module Scanner (UTMS)

[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/fjdev/utms)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A professional tool for scanning source code repositories to discover and analyze Terraform module references across multiple source providers (Azure DevOps, GitHub) with comprehensive reporting and cross-referencing capabilities.

## Features

- **Multi-source support**: Azure DevOps and GitHub integration
- **Intelligent authentication**: Automatic token detection from environment, keychain, or interactive input
- **Comprehensive scanning**: Discovers all Terraform module references with detailed analysis
- **High-performance processing**: Concurrent repository and file scanning with intelligent caching
- **Professional output**: JSON reports per source with formatted console summaries
- **Advanced filtering**: Repository and project-level filtering support
- **Production-ready**: Robust error handling, logging, and progress tracking
- **Zero dependencies**: Pure Python stdlib implementation for maximum compatibility
- **Fully tested**: 126 comprehensive unit tests with 100% success rate

### Performance Optimizations

UTMS includes advanced performance optimizations for enterprise-scale scanning:

- **Concurrent repository processing**: Up to 3 repositories scanned simultaneously
- **Concurrent file processing**: Up to 2 files per repository processed in parallel  
- **Intelligent API caching**: LRU cache for API responses (1000 entries)
- **Streaming file processing**: Memory-efficient processing for files >1MB
- **Batch processing**: Intelligent batching to prevent API rate limiting
- **Progress tracking**: Real-time progress reporting with ETA calculations

Performance optimizations are automatically enabled for multi-repository scans and can significantly reduce scan times for large organizations.

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
# Scan Azure DevOps organization
./utms --source azure-devops --organization my-azure-org

# Scan GitHub organization
./utms --source github --organization my-github-org

# Filter by specific projects (Azure DevOps)
./utms --source azure-devops --organization my-org --projects project1,project2

# Filter by specific repositories (GitHub)
./utms --source github --organization my-org --repositories repo1,repo2

# Clean existing files before generating new ones
./utms --source azure-devops --organization my-org --clean

# Cross-reference with TMVS registry data
./utms --source azure-devops --organization my-org --cross-reference ./tmvs/results/

# Debug mode for troubleshooting
./utms --source azure-devops --organization my-org --debug
```

## 📋 Requirements

- **Python 3.7+** (uses only standard library)
- **Authentication Token**:
  - Azure DevOps: Personal Access Token (PAT) with Repository Read permissions
  - GitHub: Personal Access Token with Repository Read permissions
- **Network Access** to target source providers

## ⚙️ Configuration

UTMS includes several performance and behavior configurations that automatically optimize based on workload:

### Performance Settings

The tool automatically enables performance optimizations for enterprise-scale scanning:

- **MAX_CONCURRENT_REPOS**: 3 repositories processed simultaneously
- **MAX_CONCURRENT_FILES**: 2 files per repository processed in parallel
- **CACHE_SIZE_LIMIT**: 1000 API responses cached using LRU strategy
- **STREAMING_THRESHOLD**: Files >1MB processed using memory-efficient streaming
- **BATCH_PROCESSING**: Intelligent batching prevents API rate limiting

### File Processing Settings

- **MAX_FILE_SIZE**: 10MB maximum file size limit (configurable)
- **SUPPORTED_PATTERNS**: `*.tf`, `*.tfvars`, `*.hcl` files
- **IGNORE_PATTERNS**: Common non-Terraform files automatically excluded
- **CACHE_TIMEOUT**: API responses cached with intelligent expiration

All performance optimizations use Python's standard library for zero external dependencies.

## 🔐 Authentication Methods

UTMS supports multiple authentication methods, tried in order of preference:

1. **Command Line Token**: `--token YOUR_TOKEN`
2. **Environment Variables**:
   - Azure DevOps: `AZURE_DEVOPS_TOKEN`, `AZURE_DEVOPS_PAT`
   - GitHub: `GITHUB_TOKEN`, `GITHUB_PAT`
3. **macOS Keychain**: Automatic storage and retrieval
4. **Interactive Prompt**: Secure token entry with optional keychain storage

### Setting Up Authentication

#### Azure DevOps
```bash
# Option 1: Environment variable
export AZURE_DEVOPS_TOKEN="your_pat_token_here"

# Option 2: Direct command line
./utms --source azure-devops --organization my-org --token "your_pat_token"

# Option 3: Interactive (will prompt and offer keychain storage)
./utms --source azure-devops --organization my-org
```

#### GitHub
```bash
# Option 1: Environment variable
export GITHUB_TOKEN="your_pat_token_here"

# Option 2: Direct command line
./utms --source github --organization my-org --token "your_pat_token"

# Option 3: Interactive (will prompt and offer keychain storage)
./utms --source github --organization my-org
```

## 📊 Output Format

UTMS generates comprehensive JSON output files in the `results/` directory:

### File Structure
```
results/
├── azure-devops-{organization}.json  # Azure DevOps scan results
├── github-{organization}.json        # GitHub scan results
└── cross-reference-report.json       # Cross-reference analysis (if enabled)
```

### Example Output
```json
{
  "scan_info": {
    "tool_name": "UTMS",
    "version": "1.0.0",
    "source_type": "azure-devops",
    "organization": "my-organization",
    "scan_date": "2024-08-12T09:30:00Z",
    "total_repositories": 25,
    "total_projects": 5
  },
  "summary": {
    "total_modules_found": 42,
    "unique_modules": 28,
    "public_registry_modules": 15,
    "private_registry_modules": 13,
    "version_constraints_found": 35,
    "repositories_with_modules": 18
  },
  "modules": [
    {
      "source": "registry.terraform.io/hashicorp/aws",
      "version_constraint": "~> 5.0",
      "resolved_version": "5.23.1",
      "constraint_type": "pessimistic",
      "is_latest": false,
      "found_in": [
        {
          "repository": "infrastructure-core",
          "project": "Platform",
          "file_path": "modules/vpc/main.tf",
          "line_number": 12
        }
      ]
    }
  ]
}
```

## 🔗 Cross-Reference Integration

UTMS can cross-reference discovered modules with TMVS registry data:

```bash
# Generate TMVS data first
./tmvs --organization my-terraform-org

# Then cross-reference with UTMS scan
./utms --source azure-devops --organization my-org --cross-reference ./tmvs/results/
```

This generates a comprehensive report showing:
- Which modules in your code are available in your private registry
- Version mismatches between code and registry
- Modules that could be migrated to private registry
- Usage patterns and recommendations

## 🛠️ Advanced Usage

### Filtering Options

```bash
# Azure DevOps - specific projects only
./utms --source azure-devops --organization my-org --projects "Infrastructure,Platform"

# GitHub - specific repositories only
./utms --source github --organization my-org --repositories "terraform-modules,infrastructure"

# Clean existing results before scan
./utms --source azure-devops --organization my-org --clean
```

### Debug Mode

```bash
# Enable detailed logging for troubleshooting
./utms --source azure-devops --organization my-org --debug
```

## 🏗️ Architecture

UTMS follows enterprise-grade software design patterns:

- **Provider Pattern**: Extensible source provider architecture
- **Authentication Strategy Pattern**: Multiple authentication methods
- **Repository Pattern**: Clean data access abstractions
- **Configuration Management**: Centralized configuration with `UTMSConfig`
- **Error Handling**: Custom exception hierarchy for robust error management
- **Logging**: Comprehensive logging with configurable levels

## 🧪 Testing

```bash
# Syntax validation
python3 -c "exec(open('utms').read())" --version

# Help system test
./utms --help

# Basic functionality test (requires valid token)
./utms --source azure-devops --organization test-org --debug
```

**Test Coverage**: UTMS includes comprehensive test coverage with 126 unit tests covering all functionality.

```bash
# Run test suite (development)
cd tests && PYTHONPATH=. python3 -m unittest discover -s . -p "test_*.py"
```

## 📝 File Size Limits

- **Maximum file size**: 1MB per file (configurable in `UTMSConfig.MAX_FILE_SIZE_MB`)
- **Performance**: Processes repositories in batches for optimal memory usage
- **Large repositories**: Automatically skips oversized files with logging

## ⚡ Performance

- **Concurrent processing**: Up to 10 concurrent file operations (configurable)
- **Batch processing**: Repositories processed in batches of 5
- **Memory efficient**: Streaming file processing for large repositories
- **Network optimization**: Connection reuse and proper timeout handling

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Failures**
   ```bash
   # Verify token manually
   ./utms --source azure-devops --organization test --token "your_token" --debug
   ```

2. **Network Issues**
   ```bash
   # Check with debug mode
   ./utms --source github --organization test --debug
   ```

3. **Empty Results**
   - Verify organization name spelling
   - Check token permissions (Repository Read required)
   - Ensure repositories contain Terraform files

### Debug Information

When using `--debug` flag, UTMS provides detailed information about:
- Authentication process and token validation
- Repository discovery and filtering
- File scanning progress and results
- API calls and responses
- Error details and stack traces

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

UTMS follows the VCC Toolkit coding standards defined in `CODING_STANDARDS.md`. All contributions should:

- Follow PEP 8 style guidelines
- Include comprehensive type hints
- Maintain zero external dependencies
- Include appropriate error handling
- Add tests for new functionality

## 🆘 Support

For issues, questions, or feature requests, please:
1. Check the troubleshooting section above
2. Run with `--debug` flag to gather diagnostic information
3. Create an issue with detailed information about your environment and the problem

---

**UTMS v1.0.0** - Part of the VCC (Version Control & Compliance) Toolkit
