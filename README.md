# Toast Exports ETL

## Introduction

The Toast PoS system provides data via CSV files. The purpose of this project is to extract data from these CSV files and recombine it into a relational database, creating a Data Warehouse for analysis.

## Steps Involved

1. **Extract Data**: Extract data from the provided CSV files.
2. **Transform Data**: Recombine the extracted data into a relational database.
3. **Load Data**: Load the transformed data into the Data Warehouse.

## Sample Data

The repository contains sample CSV files in the `samaple-data/20240410/` directory. These files are used for data extraction and include:

- `AllItemsReport.csv`
- `CashEntries.csv`
- `CheckDetails.csv`
- `ItemSelectionDetails.csv`
- `KitchenTimings.csv`
- `ModifiersSelectionDetails.csv`
- `OrderDetails.csv`
- `PaymentDetails.csv`
- `TimeEntries.csv`
