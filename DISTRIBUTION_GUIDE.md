# NBO Package - Distribution Guide

## 📦 For Package Maintainers (You)

### Building Distribution Packages

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates:
# dist/
#   ├── nbo_package-1.0.0-py3-none-any.whl  (wheel - recommended)
#   └── nbo_package-1.0.0.tar.gz            (source distribution)
```

### Distribution Options

#### Option 1: Private Distribution

```bash
# Share the wheel file directly
# Users install with:
pip install nbo_package-1.0.0-py3-none-any.whl
```

#### Option 2: Internal Package Repository

```bash
# Upload to internal PyPI server
twine upload --repository-url http://your-internal-pypi.com dist/*
```

#### Option 3: Public PyPI (if desired)

```bash
# Upload to public PyPI
twine upload dist/*

# Users can then install with:
pip install nbo-package
```

## 👥 For End Users

### Installation Methods

#### Method 1: From Wheel File (Recommended)

```bash
# Download the .whl file, then:
pip install nbo_package-1.0.0-py3-none-any.whl

# Verify installation
nbo-run --version
```

#### Method 2: From Source Code

```bash
# If you have access to source code:
git clone <repository-url>
cd nbo-package
pip install -e .
```

#### Method 3: From PyPI (if published)

```bash
pip install nbo-package
```

### System Requirements

- Python 3.8 or higher
- Windows, macOS, or Linux
- 50MB free disk space

### Quick Start After Installation

```bash
# 1. Create your data templates
nbo-run setup-data-templates --output-dir my_nbo_data

# 2. Edit the CSV files with your data
# (Replace sample data in my_nbo_data/ with your actual data)

# 3. Validate your data
nbo-run --data-path my_nbo_data validate-user-data

# 4. Run the pipeline
nbo-run --data-path my_nbo_data --output-path results pipeline

# 5. Check results in the results/ folder
```

## 🔧 No Additional Setup Required

Once installed, users get:

- ✅ All CLI commands globally available
- ✅ Python package for programmatic use
- ✅ Data templates and validation
- ✅ Complete pipeline orchestration
- ✅ Built-in help and documentation

## 📋 User Workflow

1. **Install** the package (one command)
2. **Generate** data templates (one command)
3. **Replace** sample data with their actual data
4. **Validate** their data (one command)
5. **Run** the pipeline (one command)
6. **Get** results

**Total user effort: ~10 minutes setup + data preparation time**
