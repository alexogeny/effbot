from datetime import datetime
import peewee as pw 
from .base import BaseModel

class ServerTT2(BaseModel):
    code = pw.CharField(max_length=10, index=True, null=True)
    name = pw.CharField(max_length=32, null=True)
    pwd = pw.IntegerField(null=True)
    cq = pw.IntegerField(null=True)
    ms = pw.IntegerField(default=10000, null=True)
    prestiges = pw.IntegerField(default=250, null=True)
    tcq = pw.IntegerField(default=1000, null=True)
    recruitment = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    timerinterval = pw.CharField(max_length=32, null=True)
    inxtext = pw.TextField(null=True)
    nowtext = pw.TextField(null=True)
    timerchannel = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    whenchannel = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    gm = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    master = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    captain = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    knight = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    recruit = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    alumni = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    guest = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    applicant = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    timerperms = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    recruitperms = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    settingsperms = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    hofchannel = pw.DecimalField(max_digits=38, decimal_places=0, null=True)
    loachannel = pw.DecimalField(max_digits=38, decimal_places=0, null=True)

class Titanlord(BaseModel):
    clan_code = pw.ForeignKeyField(ServerTT2, backref='cqs', index=True)
    quest_number = pw.IntegerField(null=True)
    spawned_at = pw.DateTimeField(default=datetime.utcnow, null=True)
    killed_at = pw.DateTimeField(default=datetime.utcnow, null=True)
    export_data = pw.BlobField(null=True)


#class Starfever(BaseModel):
# class Settings(BaseModel):
