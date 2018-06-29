from datetime import datetime
import peewee as pw 
from .base import BaseModel

class UserTT2(BaseModel):
    supportcode = pw.CharField(max_length=10, index=True)
    clancode = pw.DeferredForeignKey('ServerTT2', null=True)
    ms = pw.IntegerField(default=10000)
    prestiges = pw.IntegerField(default=250)
    tcq = pw.IntegerField(default=1000)
    maxtaps = pw.IntegerField(default=300,
                               constraints=[pw.Check('max_taps >= 1'),
                                            pw.Check('max_taps <= 600')])
    tapslifetime = pw.BigIntegerField()
    playtime = pw.CharField(max_length=16)
    artifacts = pw.BlobField()
    country = pw.CharField(max_length=4)
