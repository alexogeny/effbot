import os
import asyncpg
import json
from datetime import datetime
from collections import defaultdict


async def init_connection(conn):
    await conn.set_type_codec(
        'json',
        encoder=json.dumps,
        decoder=json.loads,
        schema='pg_catalog'
    )

async def get_db():
    path = os.environ.get('DATABASE_URL', 'postgres://postgres:admin@localhost/postgres')
    pool = await asyncpg.create_pool(dsn=path, command_timeout=60, max_size=5, min_size=1, init=init_connection)
    async with pool.acquire() as connection:
        await connection.execute(_server)
        await connection.execute(_user)
        await connection.execute(_titanlord)
        for migrator in _migrators:
            await connection.execute(migrator)
    return pool

_base = """
CREATE TABLE IF NOT EXISTS "{name}"(
    id numeric PRIMARY KEY,
    "create" timestamp,
    "update" timestamp,
    {fields}
);
"""
_js = "json default '{}'::json"
_server = _base.format(
    name='server',
    fields=',\n    '.join(f'{k} {v}' for k,v in dict(
        tt=_js,
        users="json default '[]'::json",
        logs=_js,
        roles=_js,
        restrictions=_js,
        channels=_js,
        texts=_js,
        warnings=_js,
        extra=_js,
        prefix='text'
    ).items())
)
print(_server)

_user = _base.format(
    name='user',
    fields=',\n    '.join(f'{k} {v}' for k,v in dict(
        tt=_js,
        timers=_js,
        xp=_js,
        currency=_js,
        fun=_js
    ).items())
)
print(_user)

_titanlord = """CREATE TABLE IF NOT EXISTS Titanlord(
    id serial primary key,
    guild numeric,
    name text,
    clanname text,
    shortcode text,
    "create" timestamp,
    "update" timestamp,
    timezone numeric,
    cq_number numeric,
    pinged_at numeric,
    ping_at json default '[]'::json,
    next timestamp,
    message numeric,
    timer text,
    now text,
    ping text,
    round text,
    after text,
    when_message numeric,
    when_channel numeric,
    channel numeric,
    paste_channel numeric,
    report_channel numeric,
    masters_channel numeric,
    loa_channel numeric,
    ms_requirement numeric,
    tcq_requirement numeric,
    prestige_requirement numeric,
    tpcq_requirement numeric,
    hpcq_requirement numeric,
    top10_min numeric,
    round_number numeric,
    export_data jsonb default '{}'::jsonb
);"""

_migrators = (
    """ALTER TABLE Titanlord ADD COLUMN IF NOT EXISTS round_number numeric;""",
    """ALTER TABLE Titanlord ADD COLUMN IF NOT EXISTS export_data jsonb default '{}'::jsonb""",
    """ALTER TABLE Server ADD COLUMN IF NOT EXISTS prefix text;""",
    """ALTER TABLE Titanlord DROP COLUMN IF EXISTS active;""",
    """ALTER TABLE Server DROP COLUMN IF EXISTS active;""",
    """ALTER TABLE "user" DROP COLUMN IF EXISTS active;"""
)

Server = defaultdict(lambda: dict(
    id=0, create=datetime.utcnow(), update=datetime.utcnow(), tt={}, users=[], logs={}, roles={},
    restrictions={}, channels={}, texts={}, warnings={}, extra={}, prefix='e@'
))
User = defaultdict(lambda: dict(
    id=0, create=datetime.utcnow(), update=datetime.utcnow(), tt={}, timers={}, xp={}, 
    currency={}, fun={}
))
Titanlord = defaultdict(lambda: dict(
    id='DEFAULT', guild=0, name='default', clanname=None, shortcode=None, create=datetime.utcnow(), update=datetime.utcnow(),
    timezone=0, cq_number=1, pinged_at=3600, ping_at=[], next=None, message=0,
    timer='{TIME} until boss #{CQ} ({SPAWN} UTC)',
    now='{TIME} until boss #{CQ} ({SPAWN} UTC) @everyone',
    ping='BOSS #{CQ} SPAWNED @everyone!!!',
    round='Ding! Time for round {ROUND}, @everyone',
    after='Hey {TIMER}, set the timer and export CQ data!',
    when_message=0, when_channel=0, channel=0, paste_channel=0, report_channel=0,
    masters_channel=0, loa_channel=0, round_number=0, export_data={}
))
