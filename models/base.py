import uuid
from datetime import datetime
from pathlib import Path
import peewee as pw
print(str(Path('.').absolute()/'data'/'db.db'))
db = pw.SqliteDatabase(str(Path('.').absolute()/'data'/'db.db'))

class BaseModel(pw.Model):
    # uuid = pw.UUIDField(primary_key=True)
    id = pw.DecimalField(max_digits=38, decimal_places=0, index=True, primary_key=True)
    create_ = pw.DateTimeField(column_name='create', default=datetime.utcnow)
    update_ = pw.DateTimeField(column_name='update', null = True)

    class Meta:
        database = db
