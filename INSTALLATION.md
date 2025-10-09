# 🚀 NBO Package - Installation Instructions

## For End Users (Simple Installation)

### Option 1: Install from Wheel File (Recommended)

1. **Get the wheel file:**

   - Download `nbo_package-1.0.0-py3-none-any.whl` from the `dist/` folder
   - Or have it shared with you by the package maintainer

2. **Install the package:**

   ```bash
   pip install nbo_package-1.0.0-py3-none-any.whl
   ```

3. **Verify installation:**

   ```bash
   nbo-run --version
   # Should output: nbo-package 1.0.0
   ```

4. **Start using it:**

   ```bash
   # Create data templates
   nbo-run setup-data-templates --output-dir my_data

   # Edit the CSV files in my_data/ with your actual data

   # Validate your data
   nbo-run --data-path my_data validate-user-data

   # Run the pipeline
   nbo-run --data-path my_data --output-path results pipeline
   ```

### Option 2: Install from Source

1. **Get the source code:**

   - Download and extract the entire `nbo-package` folder
   - Or clone from repository

2. **Install:**

   ```bash
   cd nbo-package
   pip install -e .
   ```

3. **Verify and use** (same as Option 1)

## System Requirements

- **Python:** 3.8 or higher
- **Operating System:** Windows, macOS, or Linux
- **Disk Space:** ~50MB
- **Dependencies:** Automatically installed (pandas, numpy, scikit-learn, pyarrow)

## What Gets Installed

✅ **Global CLI commands:**

- `nbo-run` - Main command-line interface
- `nbo-pipeline` - Direct pipeline runner

✅ **Python package:**

- `import nbo` - For programmatic use
- All data validation and pipeline functionality

✅ **Built-in data templates and validation**

## Quick Test

After installation, run this to verify everything works:

```bash
# Create test data
nbo-run setup-data-templates --output-dir test_nbo

# Validate the templates (should pass)
nbo-run --data-path test_nbo validate-user-data

# Check pipeline configuration
nbo-run check-pipeline
```

## No Additional Setup Required!

Once installed, users can immediately:

- ✅ Create data templates
- ✅ Validate their CSV files against your schema
- ✅ Run the complete NBO pipeline
- ✅ Get professional results with full provenance

## Getting Help

```bash
# General help
nbo-run --help

# Specific command help
nbo-run validate-user-data --help
nbo-run pipeline --help

# List all available pipeline steps
nbo-run list-steps
```

## Troubleshooting

**"Command not found: nbo-run"**

- Make sure you installed with `pip install` (not just downloaded)
- Try `python -m nbo.cli` instead

**"Missing required files"**

- Use `nbo-run setup-data-templates` to create proper templates
- Make sure your CSV files have the required columns

**"Permission denied"**

- On some systems, use `pip install --user` instead

---

## For Developers/IT Teams

### Distribution Options

1. **Share the wheel file directly** (simplest)
2. **Set up internal package repository**
3. **Publish to PyPI** (if desired for public use)

### Building from Source

```bash
pip install build
python -m build
# Creates dist/nbo_package-1.0.0-py3-none-any.whl
```

The wheel file is completely self-contained and can be installed on any compatible system.
