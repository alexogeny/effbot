from datetime import datetime
import peewee as pw 
from .base import BaseModel

class Server(BaseModel):
    config = pw.BlobField(null=True) 

class Titanlord(BaseModel):
    config = pw.BlobField(null=True)
    clan_code = pw.TextField(null=False, index=True)
    spawned_at = pw.DateTimeField(default=datetime.utcnow, null=True)
