from datetime import datetime
import peewee as pw 
from base import BaseModel

class UserTT2(BaseModel):
    support_code = pw.CharField(max_length=10, index=True)
    clan_code = pw.DeferredForeignKey('ServerTT2', null=True)
    max_stage = pw.IntegerField(default=10000)
    num_prestiges = pw.IntegerField(default=250)
    num_cqs = pw.IntegerField(default=1000)
    max_taps = pw.IntegerField(default=300,
                               constraints=[pw.Check('max_taps >= 1'),
                                            pw.Check('max_taps <= 600')])
    lifetime_taps = pw.BigIntegerField()
    playtime = pw.CharField(max_length=16)
    artifact_data = pw.BlobField()
    country_code = pw.CharField(max_length=4)
