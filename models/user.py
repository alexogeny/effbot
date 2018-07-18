from datetime import datetime
import peewee as pw 
from playhouse.postgres_ext import *
from .base import BaseModel

class User(BaseModel):
    tt = JSONField(default={})
    timers = JSONField(default={})
    xp = JSONField(default={})
    currency = JSONField(default={})
    fun = JSONField(default={})