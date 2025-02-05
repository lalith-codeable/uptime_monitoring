import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uptime_monitor.settings")  
django.setup()

def drop_all_tables():
    with connection.cursor() as cursor:
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
            return

        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            print(f"Dropped table: {table_name}")

if __name__ == "__main__":
    drop_all_tables()
    print("All tables dropped successfully.")
    print("Please delete all the migration files.")
