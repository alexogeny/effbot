from datetime import datetime
import peewee as pw 
from .base import BaseModel

class ServerTT2(BaseModel):
    code = pw.CharField(max_length=10, index=True)
    name = pw.CharField(max_length=32)
    pwd = pw.IntegerField()
    cq = pw.IntegerField()
    ms = pw.IntegerField(default=10000)
    prestiges = pw.IntegerField(default=250)
    tcq = pw.IntegerField(default=1000)
    recruitment = pw.DecimalField(max_digits=38, decimal_places=0)
    timerinterval = pw.CharField(max_length=32)
    inxtext = pw.TextField()
    nowtext = pw.TextField()
    timerchannel = pw.DecimalField(max_digits=38, decimal_places=0)
    whenchannel = pw.DecimalField(max_digits=38, decimal_places=0)
    gm = pw.DecimalField(max_digits=38, decimal_places=0)
    master = pw.DecimalField(max_digits=38, decimal_places=0)
    captain = pw.DecimalField(max_digits=38, decimal_places=0)
    knight = pw.DecimalField(max_digits=38, decimal_places=0)
    recruit = pw.DecimalField(max_digits=38, decimal_places=0)
    alumni = pw.DecimalField(max_digits=38, decimal_places=0)
    guest = pw.DecimalField(max_digits=38, decimal_places=0)
    applicant = pw.DecimalField(max_digits=38, decimal_places=0)
    timerperms = pw.DecimalField(max_digits=38, decimal_places=0)
    recruitperms = pw.DecimalField(max_digits=38, decimal_places=0)
    settingsperms = pw.DecimalField(max_digits=38, decimal_places=0)
    hofchannel = pw.DecimalField(max_digits=38, decimal_places=0)
    loachannel = pw.DecimalField(max_digits=38, decimal_places=0)

class Titanlord(BaseModel):
    clan_code = pw.ForeignKeyField(ServerTT2, backref='cqs', index=True)
    quest_number = pw.IntegerField()
    spawned_at = pw.DateTimeField(default=datetime.utcnow)
    killed_at = pw.DateTimeField(default=datetime.utcnow)
    export_data = pw.BlobField()


#class Starfever(BaseModel):
# class Settings(BaseModel):
