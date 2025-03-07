# Sample Data

This directory contains sample data for development and testing purposes. The data is anonymized and safe for development use.

## Directory Structure

```
sample_data/
└── YYYYMMDD/           # Date-based directories for different data snapshots
    ├── MenuExport_*.json   # Menu export data
    ├── OrderDetails.csv    # Order details
    └── TimeEntries.csv     # Time entries data
```

## Data Description

- **MenuExport_*.json**: Contains menu items, prices, and availability
- **OrderDetails.csv**: Contains order information including items, prices, and servers
- **TimeEntries.csv**: Contains employee time entry records

## Usage

This sample data is used for:
1. Development testing
2. Unit test fixtures
3. Example data for documentation

## Notes

- All data in this directory is anonymized
- Do not store sensitive or production data in this directory
- Keep sample data minimal while still being useful for testing 