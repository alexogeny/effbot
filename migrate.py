from datetime import datetime
from models import Server, User, db
from pathlib import Path
from copy import deepcopy
from collections import defaultdict
import json
from pprint import pprint

def ingest_timestring(string):
    return datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')

servers = list(Path('data/servers').iterdir())
users = list(Path('data/users').iterdir())

j_servers = []
j_users = []

for server in servers:
    with server.open('r') as fh:
        j_servers.append(json.load(fh))

for user in users:
    with user.open('r') as fh:
        j_users.append(json.load(fh)) 

sjson = []
ujson = []

for server in j_servers:
    s = {}
    s['id'] = int(server['id'])
    s['create_'] = ingest_timestring(server['create_'])
    s['update_'] = ingest_timestring(server['update_'])
    s['tt'] = {}
    s['users'] = server['config'].get('xp', [])
    s['logs'] = {}
    s['roles'] = {}
    s['restrictions'] = {}
    s['channels'] = {}
    s['texts'] = {}
    s['warnings'] = {}
    s['extra'] = {}
    s['extra']['quotes'] = server['config'].get('list_quotes',[])
    sjson.append(s)

for user in j_users:
    u = {}
    u['id'] = int(user['id'])
    u['create_'] = ingest_timestring(user['create_'])
    u['update_'] = ingest_timestring(user['update_'])
    u['tt'] = {}
    u['tt']['code'] = user['config'].get('tt_code', "")
    u['timers'] = {}
    u['xp'] = {}
    u['xp']['amount'] = user['config'].get('xp', 0)
    u['currency'] = {}
    u['fun'] = {}
    ujson.append(u)

pprint(ujson[0])
pprint(sjson[1])

with db.atomic():
    db.drop_tables([Server, User])

with db.atomic():
    db.create_tables([Server, User])

with db.atomic():
    Server.insert_many(sjson).execute()

with db.atomic():
    User.insert_many(ujson).execute()

user = User.get_by_id(305879281580638228)
print(user.__class__)
pprint(user.xp)
pprint(user.create_)