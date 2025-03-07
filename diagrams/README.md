# Database Diagrams

This directory contains database schema diagrams and related files.

## Files

- `schema_dbdiagram.sql`: PostgreSQL schema dump formatted for import into [dbdiagram.io](https://dbdiagram.io)

## Generating Schema

To generate a fresh schema dump:

```bash
./tools/db/pg_dump.sh
```

## Using with dbdiagram.io

1. Go to [dbdiagram.io](https://dbdiagram.io)
2. Click "Create new diagram"
3. Click "Import" in the top menu
4. Select "PostgreSQL" as the import format
5. Open `schema_dbdiagram.sql` and paste its contents

## Notes

- The schema dump is automatically generated and should not be edited manually
- If you make changes to the database schema, regenerate this file
- Consider committing the schema file to track database structure changes 