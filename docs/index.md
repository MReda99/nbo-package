# NBO Package Documentation

> **Purpose**: This is the main documentation hub for the NBO Package, providing easy navigation to all documentation resources.

Welcome to the NBO Package documentation! This machine learning pipeline provides complete Next Best Offer optimization capabilities.

## 📚 **Documentation Navigation**

### **Getting Started**
- [📋 Installation Guide](INSTALLATION.html) - Simple installation instructions
- [⚡ Quick Reference](QUICK_REFERENCE.html) - Essential commands and workflow
- [👤 User Workflow](USER_WORKFLOW.html) - Complete user experience examples

### **Comprehensive Guides**
- [📖 End User Guide](END_USER_GUIDE.html) - Complete guide for repository users
- [🔧 Usage Guide](USAGE_GUIDE.html) - Detailed usage for developers and analysts
- [📦 Distribution Guide](DISTRIBUTION_GUIDE.html) - Package distribution instructions

### **Reference Documentation**
- [🎯 Complete Functionality](COMPLETE_FUNCTIONALITY.html) - Full feature overview
- [📄 Project Overview](PROJECT_OVERVIEW.html) - Project overview and technical details

## 🚀 **Quick Start**

1. **Install the package**:
   ```bash
   pip install nbo_package-1.0.0-py3-none-any.whl
   ```

2. **Create data templates**:
   ```bash
   nbo-run setup-data-templates --output-dir my_data
   ```

3. **Validate your data**:
   ```bash
   nbo-run --data-path my_data validate-user-data
   ```

4. **Run the pipeline**:
   ```bash
   nbo-run --data-path my_data --output-path results pipeline
   ```

## 🎯 **What is NBO Package?**

The NBO (Next Best Offer) Package is a complete machine learning pipeline that:

- ✅ **Validates** customer data against predefined schemas
- ✅ **Trains** uplift models for personalized offer optimization
- ✅ **Applies** business rules and guardrails
- ✅ **Generates** optimal offer recommendations
- ✅ **Provides** full provenance tracking

## 📊 **Key Features**

- **Complete Pipeline**: End-to-end NBO processing
- **Data Validation**: Schema validation and quality checks
- **ML Models**: Uplift modeling and scoring
- **Business Rules**: Fatigue management and margin floors
- **Easy Installation**: Single wheel file installation
- **CLI Interface**: Simple command-line tools

---

**Need help?** Start with the [Installation Guide](INSTALLATION.html) or check the [Quick Reference](QUICK_REFERENCE.html) for essential commands.
