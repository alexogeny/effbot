from datetime import datetime
import peewee as pw 
from playhouse.postgres_ext import *
from .base import BaseModel

class Server(BaseModel):
    tt = JSONField(default={})
    users = JSONField(default=[])
    logs = JSONField(default={})
    roles = JSONField(default={})
    restrictions = JSONField(default={})
    channels = JSONField(default={})
    texts = JSONField(default={})
    warnings = JSONField(default={})
    extra = JSONField(default={})