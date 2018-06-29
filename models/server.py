from datetime import datetime
import peewee as pw 
from base import BaseModel

class ServerTT2(BaseModel):
    clan_code = pw.CharField(max_length=10, index=True)
    clan_name = pw.CharField(max_length=32)
    clan_pass = pw.IntegerField()
    clan_quest = pw.DeferredForeignKey('Titanlord', null=True)
    req_maxstage = pw.IntegerField(default=10000)
    req_prestiges = pw.IntegerField(default=250)
    req_cqs = pw.IntegerField(default=1000)
    req_channel = pw.DecimalField(max_digits=38, decimal_places=0)
    timer_interval = pw.CharField(max_length=32)
    timer_inxtext = pw.TextField()
    timer_nowtext = pw.TextField()
    timer_channel = pw.DecimalField(max_digits=38, decimal_places=0)
    when_channel = pw.DecimalField(max_digits=38, decimal_places=0)
    role_gm = pw.DecimalField(max_digits=38, decimal_places=0)
    role_master = pw.DecimalField(max_digits=38, decimal_places=0)
    role_captain = pw.DecimalField(max_digits=38, decimal_places=0)
    role_knight = pw.DecimalField(max_digits=38, decimal_places=0)
    role_recruit = pw.DecimalField(max_digits=38, decimal_places=0)
    role_alumni = pw.DecimalField(max_digits=38, decimal_places=0)
    role_guest = pw.DecimalField(max_digits=38, decimal_places=0)
    role_applicant = pw.DecimalField(max_digits=38, decimal_places=0)
    perm_timer = pw.DecimalField(max_digits=38, decimal_places=0)
    perm_recruit = pw.DecimalField(max_digits=38, decimal_places=0)
    perm_settings = pw.DecimalField(max_digits=38, decimal_places=0)
    hof_channel = pw.DecimalField(max_digits=38, decimal_places=0)
    loa_channel = pw.DecimalField(max_digits=38, decimal_places=0)

class Titanlord(BaseModel):
    clan_code = pw.ForeignKeyField(ServerTT2, backref='cqs', index=True)
    quest_number = pw.IntegerField()
    spawned_at = pw.DateTimeField(default=datetime.utcnow)
    killed_at = pw.DateTimeField(default=datetime.utcnow)
    export_data = pw.BlobField()


#class Starfever(BaseModel):
# class Settings(BaseModel):
