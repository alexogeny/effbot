from datetime import datetime
import peewee as pw 
from .base import BaseModel

class User(BaseModel):
    config = pw.BlobField(null=True)