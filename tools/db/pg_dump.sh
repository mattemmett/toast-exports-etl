#!/bin/bash

# Get the project root directory (2 levels up from this script)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Load environment variables from .env file
set -a
source "$PROJECT_ROOT/.env"
set +a

# Create diagrams directory in the project if it doesn't exist
DIAGRAMS_DIR="$PROJECT_ROOT/diagrams"
mkdir -p "$DIAGRAMS_DIR"

# Run pg_dump in Docker with schema-only output formatted for dbdiagram.io
sudo docker run --rm --network=host \
  -e PGPASSWORD="$PG_PASSWORD" \
  -v "$DIAGRAMS_DIR:/tmp/dump" \
  postgres:latest \
  pg_dump \
    --host=$PG_HOST \
    --username=$PG_USER \
    --dbname=$PG_DBNAME \
    --schema-only \
    --no-owner \
    --no-privileges \
    --no-tablespaces \
    --no-security-labels \
    --no-comments \
    -F p \
    -f "/tmp/dump/schema_dbdiagram.sql"

# Fix permissions on the output file
sudo chown $USER:$USER "$DIAGRAMS_DIR/schema_dbdiagram.sql"

echo "Schema dump created at: $DIAGRAMS_DIR/schema_dbdiagram.sql"
echo "You can now import this file directly into dbdiagram.io" 