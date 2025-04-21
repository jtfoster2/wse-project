#!/bin/bash

# Define the name of the database
DB_NAME="database"  # Replace with your database name

# Connect to PostgreSQL (default user is assumed) and drop & recreate the database
psql postgres <<EOF
  -- Drop the database if it exists
  DROP DATABASE IF EXISTS $DB_NAME;

  -- Create the new database
  CREATE DATABASE $DB_NAME;

  \q

EOF

echo "Database $DB_NAME reset successfully."