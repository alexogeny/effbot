from datetime import datetime
import peewee as pw 
from .base import BaseModel

class UserTT2(BaseModel):
    supportcode = pw.CharField(max_length=10, index=True, null=True)
    clancode = pw.DeferredForeignKey('ServerTT2', null=True)
    ms = pw.IntegerField(default=10000, null=True)
    prestiges = pw.IntegerField(default=250, null=True)
    tcq = pw.IntegerField(default=1000, null=True)
    maxtaps = pw.IntegerField(default=300,
                               constraints=[pw.Check('maxtaps >= 1'),
                                            pw.Check('maxtaps <= 600')], null=True)
    tapslifetime = pw.BigIntegerField(null=True)
    playtime = pw.CharField(max_length=16, null=True)
    artifacts = pw.BlobField(null=True)
    country = pw.CharField(max_length=4, null=True)
