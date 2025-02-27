-- Drop checks table first (because it depends on orders)
BEGIN;
TRUNCATE TABLE checks RESTART IDENTITY CASCADE;
DROP TABLE IF EXISTS checks;
COMMIT;

-- Drop orders table (depends on locations and employees)
BEGIN;
TRUNCATE TABLE orders RESTART IDENTITY CASCADE;
DROP TABLE IF EXISTS orders;
COMMIT;

-- Drop time_entries table (depends on locations, employees, and jobs)
BEGIN;
TRUNCATE TABLE time_entries RESTART IDENTITY CASCADE;
DROP TABLE IF EXISTS time_entries;
COMMIT;

-- Drop jobs table
BEGIN;
TRUNCATE TABLE jobs RESTART IDENTITY CASCADE;
DROP TABLE IF EXISTS jobs;
COMMIT;

-- Drop employees table
BEGIN;
TRUNCATE TABLE employees RESTART IDENTITY CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
COMMIT;

-- Drop locations table
BEGIN;
TRUNCATE TABLE locations RESTART IDENTITY CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
COMMIT;

-- Drop menus table
BEGIN;
TRUNCATE TABLE menus RESTART IDENTITY CASCADE;
DROP TABLE IF EXISTS menus;
COMMIT;

