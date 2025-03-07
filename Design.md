# Toast POS ETL

## Executive Summary
TODO: Add a concise summary of the project purpose, business value, and key objectives.

## Overview

The purpose of this project is to process the nightly export from Toast POS and load the data into a PostgreSQL database.

This project is part of a larger initiative to build an enterprise data warehouse for the company.

## Scope
TODO: Define what is in and out of scope for this project.

## Data Model

Toast provides a nightly export via a series of related on non related CSV files and JSON files. The data contains numberous calculatinos that should be maintained in the data warehouse.

The following is a list of the CSV and JSON files that are used in the ETL process. 

- AllItemsReport.csv - A report containing all items sold, organized by menu and menu groups
- CashEntries.csv - Containins all cash drawer operations
- CheckDetails.csv - Contains the details of invidual checks, which are part of an order
- ItemSelectionDetails.csv
- KitchenTimings.csv
- MenuExport_adddeea2[id string].json - Menu items and their prices
- MenuExportV2_adddeea[id string].json - Menu items and their prices
- ModifiersSelectionDetails.csv
- OrderDetails.csv
- PaymentDetails.csv
- TimeEntries.csv

TimeEntries.csv contains the time entries for each employee. This file includes employee names, position worked and times worked. The employees listed in this file are referenced in other files, such as Server for and order or expediter for a kitchen timing.

Orders are a main entry point for a lot of the exported data. An oder contains high level item details, with more detailed item infomration included in the linked ItemSelectionDetails.csv and ModifiersSelectionDetails.csv. files. An order contains checks, allowing for checks to be split. PaymentDetails.csv contains the payment details and is linked back to order and checks.


The two Menus JSON files detailed information about menus, menu subgroups, menu items, modifier groups and modifiers. Toast created v2 to support additonal information needed for online ordering partners, this project will focus on the v1 data. AllItemsReport.csv contains the most detailed information about items sold, including menu, menu group, item and modifier details. It is a daily report of sales from the entire menu, wheather the item was sold or not. It contains a large amount of calculations, which should be maintained in the data warehouse. It is a flat representation of the menu hierarchy from the Menus JSON files.

Menu Hierarchy Overview
Toast products use a hierarchical structure to organize restaurant menus efficiently:

Menus represent top-level categories (e.g., Food, Drinks, Lunch, Dinner).
Menu groups categorize related items within a menu (e.g., Entrees, Appetizers).
Menu sub-groups further classify menu groups (e.g., Vegetarian, From the Grill).
Menu items are the specific offerings (e.g., Roast Chicken, Pasta Primavera).
Modifier groups customize menu items (e.g., Cheese, Condiments).
Modifiers define specific item customizations (e.g., Cheddar, Provolone).
Modifier groups can be assigned at the menu group or item level, with optional inheritance controls. Modifiers themselves can have nested modifier groups for further customization.

Entity Sharing and Reuse
Shared Entities: Menu items, modifier groups, and modifiers can be used across multiple menus and menu groups.
Reused Entities: Menu groups can function as modifier groups, and menu items can be used as modifiers.

### Sample Data

The project contians sample data in the sample-data folder. The toast nightly expport process provides a directory of files, the directory is named for the date of the exported datawith the naming convention YYYYMMDD. Currently the sample data contains one export from 2024-04-10. It also includes a modified of the menu export, trimming parts for easier reading and LLM analysis.

### Database Schema
TODO: Document the database schema design including:
- Table definitions with columns and data types
- Primary and foreign key relationships
- Indexes and constraints
- Entity relationship diagram

## Data Pipeline
TODO: Describe the ETL process flow:
- Data extraction process
- Transformation rules and business logic
- Loading strategy (incremental vs. full refresh)
- Process dependencies and sequence

## System Overview
- The system will be written in Python
- The database will be PostgreSQL
- The database library will be psycopg3 
- This will eventually be used in some type of ETL orchestration, but for now will be used to process the sample data

### System Architecture
TODO: Add a detailed system architecture diagram showing:
- Data sources and destinations
- Processing components
- Data flows
- Integration points

## Design Principles
- Add new tables to db/create_tables.py
- Include drop table statements in db/drop_tables.py, ensure to handle cascade dependencies
- The codebase should be modular for readability and maintainability, major functions should be in individual files in file_processors.py and called from main.py
- It should be safe to process the same date multiple times, it should check for existing data and skip processing if present


## Error Handling & Recovery
TODO: Define how the system will:
- Detect and log errors
- Handle failures gracefully
- Support retry mechanisms
- Support data recovery

## Performance Considerations
TODO: Document:
- Expected data volumes
- Performance requirements
- Optimization strategies
- Scaling approach

## Security
TODO: Address:
- Data access controls
- Sensitive data handling
- Authentication requirements
- Audit trail needs

## Deployment
TODO: Describe:
- Deployment strategy
- Environment requirements
- Scheduling approach
- Maintenance procedures

## Testing
- The project will be tested using pytest
- The sample data will be used to test the project
- The project will be tested against the sample data using pytest
- Implement unit tests for all data processing functions
### Aproach
- Ensure that all rows are processed and loaded into the database
- Ensure that you can recreate the sample data from the database, even if joins and lookups are required. For example, ensure you can recreate the row: 1234 Elmwood Avenue,,900000004018475556,b8f86cb1-dac3-404d-9829-dbbd57878b17,900000000128688048,d49e83d8-22ef-4fbd-a710-a48cda91c24a,4286,"A, Cook",900000000004225865,189b038f-c0ab-4750-bf7d-f41f525b3620,,Cook,4/10/24 3:57 PM,4/10/24 9:01 PM,No,5.07,0.0,0.0,5.07,,0.0,0.0,0.0,0.0,14.0,5.07,0.0,70.98,0.0,70.98 from the TimeEntries.csv file.

TODO: Expand with:
- Test data strategy
- Integration testing approach
- Performance testing plan
- Test automation approach

## Monitoring & Alerting
TODO: Define:
- Key metrics to monitor
- Alerting thresholds
- Monitoring tools
- Incident response process

## Data Quality & Validation
TODO: Describe:
- Data quality checks
- Validation rules
- Handling of data anomalies
- Reconciliation processes

## Future Enhancements
TODO: Outline potential future improvements or extensions to the system.

## Appendix
TODO: Include any additional reference material, glossary of terms, etc.


