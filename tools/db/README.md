# Database Tools

This directory contains utility scripts for database management and schema operations.

## Tools

### pg_dump.sh
A shell script that dumps the PostgreSQL schema in a format compatible with [dbdiagram.io](https://dbdiagram.io).

Usage:
```bash
./pg_dump.sh
```

The script will:
1. Connect to the database using the configuration from the main project
2. Extract the schema information
3. Save the schema to `diagrams/schema_dbdiagram.sql`

## Adding New Tools

When adding new database utility scripts:
1. Place them in this directory
2. Update this README with usage instructions
3. Ensure they use the project's configuration system for database connections 