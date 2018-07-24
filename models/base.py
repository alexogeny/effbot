import uuid
import os
import psycopg2
from datetime import datetime
from pathlib import Path
import peewee as pw
from playhouse.postgres_ext import PostgresqlExtDatabase
from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.db_url import parse
if not os.environ.get('DATABASE_URL'):
    db = SqliteExtDatabase(':memory:')
else:
    auth = parse(os.environ.get(
        'DATABASE_URL', 'postgres://postgres:admin@localhost/postgres'))
    db = PostgresqlExtDatabase(auth['database'], user=auth['user'],
        password=auth['password'], host=auth['host'])
class BaseModel(pw.Model):
    id = pw.DecimalField(max_digits=38, decimal_places=0, index=True, primary_key=True)
    create_ = pw.DateTimeField(column_name='create', default=datetime.utcnow)
    update_ = pw.DateTimeField(column_name='update', null = True)

    class Meta:
        database = db
