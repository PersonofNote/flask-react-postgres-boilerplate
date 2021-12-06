#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py create_db

exec "$@"


# This checks to make sure that the database is up and healthy before creating tables, etc
# Remember to run chmod +x services/web/entrypoint.sh to update permissions locally