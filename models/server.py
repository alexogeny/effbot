from datetime import datetime
import peewee as pw 
from .base import BaseModel

class Server(BaseModel):
    config = pw.BlobField(null=True)

class Titanlord(BaseModel):
    config = pw.BlobField(null=True)
    clan_code = pw.TextField(null=False, index=True)
    # clan_code = pw.ForeignKeyField(ServerTT2, backref='cqs', index=True)
    # quest_number = pw.IntegerField(null=True)
    spawned_at = pw.DateTimeField(default=datetime.utcnow, null=True)
    # killed_at = pw.DateTimeField(default=datetime.utcnow, null=True)
    # export_data = pw.BlobField(null=True)


#class Starfever(BaseModel):
# class Settings(BaseModel):
