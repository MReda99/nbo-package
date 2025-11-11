# NBO Project Resources

> **Purpose**: This page provides access to all NBO project data, outputs, technical diagrams, and development resources including the main Jupyter notebook and data flow documentation.

## Data and Output Folders

### Input Data
**Data/** Contains folders of input CSV files organized by snapshot date.

Each snapshot date has its own subfolder holding the corresponding input CSVs for that time period.

**[Access Input Data Folder](https://drive.google.com/drive/folders/1mmxN7z1garg77laIJvTU59xChbymuiBF?usp=drive_link)**

Core datasets: We load multiple datasets that serve distinct roles:

- **Feature Mart**: the inputs our model will use to make predictions
- **Label Set**: the outcomes we're trying to predict
- **Offer Catalog**: all available promotions and their details
- **Modelling Set**: a pre-assembled dataset designed specifically for training/testing the model
- **Customer Orders**: historical transaction data, which we'll filter to only include actual redemptions

Redemption activity: We focus only on transactions where a customer redeemed a promotion (promotion_id > 0). This ensures our analysis is meaningful and only considers actionable behavior.

Touch history and customer fatigue: We load the "touches" dataset to see when and how customers were contacted. We convert timestamps to a standard format and filter only the last 72 hours before DECISION_DAY. This helps us avoid over-contacting the same guest with repeated promotions. If no touch data exists, we create an empty placeholder so the workflow doesn't break.

Quality assurance (QA): We check that each guest–promotion pair is unique. Duplicates could distort analysis, so we print a simple QA check for quick verification.

- Organized by date (e.g., 2025_08_22_0000)

### Output Results
**Out/** Contains folders of output CSV files organized by snapshot date.

Each snapshot date has its own subfolder holding the generated output CSVs from the NBO pipeline.

**[Access Output Data Folder](https://drive.google.com/drive/folders/1mZCjfZyijS9mb-41DsWSeA7Ph-v6NBdP?usp=drive_link)**

- Model scoring results
- Final offer decisions
- Marketing campaign views
- Decision logs with provenance
- Organized by date (e.g., 2025_08_22_0000)

## Technical Documentation

### Data Flow Diagram
**sql_tables_flow_20251007.png** Visual diagram showing the complete data flow architecture.

**[View Data Flow Diagram](https://drive.google.com/file/d/1aHSnklxH2L1BWZ9vt3y0N1iyz260WfyY/view?usp=drive_link)**

This diagram illustrates:

- Data flow from EDW (Enterprise Data Warehouse)
- GDP (Guest Data Platform) integration
- Transition to GDP 2.0
- Python processing pipeline
- Final output generation

### Main Development Notebook
**Subway NBO v2.ipynb** The primary Jupyter Notebook containing all engine code.

**[Access Main Notebook](https://drive.google.com/file/d/1I-6C4Wk4GFIZH4kSisct9Wm4Pt-OBWc5/view?usp=drive_link)**

This notebook contains:

- Complete NBO pipeline implementation
- Model training and validation code
- Data processing and transformation logic
- Business rules and guardrails implementation
- Output generation and formatting

## Resource Organization

### By Date Snapshots
All data (both input and output) is organized by snapshot dates:

- **Format**: `YYYY_MM_DD_HHMM` (e.g., `2025_08_22_0000`)
- **Input**: Raw data and features for that time period
- **Output**: Generated results and decisions for that snapshot

### Data Lineage
- **EDW to GDP to GDP 2.0**: Source data progression
- **Python Pipeline**: Processing and model application  
- **Output Generation**: Final results and decision logs
- **Full Provenance**: Complete tracking from input to output

## Quick Links

- **[Input Data Folder](https://drive.google.com/drive/folders/1mmxN7z1garg77laIJvTU59xChbymuiBF?usp=drive_link)** Historical input CSV files
- **[Output Data Folder](https://drive.google.com/drive/folders/1mZCjfZyijS9mb-41DsWSeA7Ph-v6NBdP?usp=drive_link)** Generated output CSV files  
- **[Data Flow Diagram](https://drive.google.com/file/d/1aHSnklxH2L1BWZ9vt3y0N1iyz260WfyY/view?usp=drive_link)** Technical architecture visualization
- **[Main Notebook](https://drive.google.com/file/d/1I-6C4Wk4GFIZH4kSisct9Wm4Pt-OBWc5/view?usp=drive_link)** Complete engine implementation

**[Back to Main Hub](index.html)** | **[Go to Package Documentation](package-docs.html)**
