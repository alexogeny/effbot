from datetime import datetime
import peewee as pw 
from playhouse.postgres_ext import *
from .base import BaseModel

class Server(BaseModel):
    tt = JSONField()
    users = JSONField()
    logs = JSONField()
    roles = JSONField()
    restrictions = JSONField()
    channels = JSONField()
    texts = JSONField()
    warnings = JSONField()
    extra = JSONField()