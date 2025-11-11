# NBO Package Documentation

> **Purpose**: This is the complete documentation for the NBO Package, providing installation guides, usage instructions, and developer resources.

**[Back to Main Hub](index.html)** | **[View Project Resources](project-resources.html)**

Welcome to the NBO Package documentation! This machine learning pipeline provides complete Next Best Offer optimization capabilities.

## Documentation Navigation

### Getting Started
• [Installation Guide](INSTALLATION.html)
• [Quick Reference](QUICK_REFERENCE.html)
• [User Workflow](USER_WORKFLOW.html)

### Comprehensive Guides
• [End User Guide](END_USER_GUIDE.html)
• [Usage Guide](USAGE_GUIDE.html)
• [Distribution Guide](DISTRIBUTION_GUIDE.html)

### Reference Documentation
• [Complete Functionality](COMPLETE_FUNCTIONALITY.html)
• [Project Overview](PROJECT_OVERVIEW.html)

## Quick Start

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

## What is NBO Package?

The NBO (Next Best Offer) Package is a complete machine learning pipeline that:

• **Validates** customer data against predefined schemas
• **Trains** uplift models for personalized offer optimization
• **Applies** business rules and guardrails
• **Generates** optimal offer recommendations
• **Provides** full provenance tracking

## Key Features

• **Complete Pipeline**: End to end NBO processing
• **Data Validation**: Schema validation and quality checks
• **ML Models**: Uplift modeling and scoring
• **Business Rules**: Fatigue management and margin floors
• **Easy Installation**: Single wheel file installation
• **CLI Interface**: Simple command line tools

**Need help?** Start with the [Installation Guide](INSTALLATION.html) or check the [Quick Reference](QUICK_REFERENCE.html) for essential commands.
