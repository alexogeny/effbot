from datetime import datetime
import peewee as pw 
from playhouse.postgres_ext import *
from .base import BaseModel

class User(BaseModel):
    tt = JSONField()
    timers = JSONField()
    xp = JSONField()
    currency = JSONField()
    fun = JSONField()