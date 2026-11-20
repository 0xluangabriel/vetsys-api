#!/bin/bash
set -e

mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<-EOSQL
    CREATE USER 'vetsys_app'@'%' IDENTIFIED BY '${DB_PASSWORD}';
    GRANT SELECT, INSERT, UPDATE, DELETE ON vetsys.* TO 'vetsys_app'@'%';

    CREATE USER 'vetsys_migrator'@'%' IDENTIFIED BY '${DB_MIGRATOR_PASSWORD}';
    GRANT ALL PRIVILEGES ON vetsys.* TO 'vetsys_migrator'@'%';
EOSQL