import discord
from datetime import datetime, timedelta
from discord.ext import commands
from string import ascii_lowercase
from itertools import chain, zip_longest
from random import choice
from math import log, log10, floor
from collections import defaultdict
from pprint import pprint
import os
import asyncio
import re
import datetime as dt
import time
UOT = 60
SCIFI = re.compile(r'^([^a-z]+)([A-Za-z]+)$')
LIFI = re.compile(r'^([0-9\.]+)[^0-9]+([0-9,]+)$')
TIME_SUCKER = re.compile(r'([0-9]+)([^0-9]+)?')
LETTERS = re.compile(r'^[wdhms]')
MAP = dict(w='weeks', d='days', h='hours', m='minutes', s='seconds')

def round_to_x(x, n):
    return round(x, -int(floor(log10(x))) + (n - 1))

def boss_hitpoints(level: int) -> int:
    return round(100000*pow(level, pow(level, .028))+.5)

def advance_start(level: int) -> float:
    return round(100*min(.003*pow(log(level+4),2.741), .9), 2)

def clan_damage(level: int) -> float:
    return round(pow(1.0233, level) + pow(level, 1.05), 2)

async def process_time(input_time: str) -> timedelta:
    match = TIME_SUCKER.findall(input_time)
    units = [
        MAP[getattr(LETTERS.match(m[1].strip()), 'string', None)
        or 'hms'[i]]
        for i, m
        in enumerate(match)
    ]
    measures = [int(x[0]) or 0 for x in match]
    return (timedelta(**{unit: measures[i] or 0 for i, unit in enumerate(units)}),
        {unit: measures[i] or 0 for i, unit in enumerate(units)})


def is_gm_or_admin():
    async def _is_gm_or_admin(ctx):
        msg = ctx.message
        roles = [r.id for r in msg.author.roles]
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        is_admin = g['roles'].get('admin') in roles
        is_owner = msg.author.id == msg.guild.owner_id
        is_gm = g['roles'].get('grandmaster') in roles
        if is_admin or is_owner or is_gm:
            return True
        elif not g['roles'].get('grandmaster'):
            await ctx.send('Ask your server admin to set the GM role')
        else:
            await ctx.send('Oof, you need to be a GM to do this.')
        return False
    return commands.check(_is_gm_or_admin)



def is_gm_or_master():
    async def _is_gm_or_master(ctx):
        m = ctx.message
        roles = [r.id for r in m.author.roles]
        g = await ctx.bot.cogs['Helpers'].get_record('server', m.guild.id)
        is_gm = g['roles'].get('grandmaster') in roles
        is_master = g['tt'].get('master') in roles
        if is_gm or is_master:
            return True
        elif not g['roles'].get('grandmaster'):
            await ctx.send('Ask your server admin to set the GM role')
        else:
            await ctx.send('Oof, you need to be a GM or master to do this.')
        return False
    return commands.check(_is_gm_or_master)

# def can_do_timers():
#     async def _can_do_timers(ctx):
#         m = ctx.message
#         g = await ctx.bot.cogs['Helpers'].get_record('server', m.guild.id)
#         roles = [a.id for a in m.author.roles]
#         is_gm = g['roles'].get('grandmaster') in roles
#         is_master = g['tt'].get('master') in roles
#         is_timer = g['tt'].get('timer') in roles
#         if is_gm or is_master or is_timer:
#             return True
#         asyncio.ensure_future(ctx.send('You do not have the necessary permissions.'))
#         return False
#     return commands.check(_can_do_timers)

# def tl_checks():
#     async def _tl_checks(ctx):
#         m = ctx.message
#         g = await ctx.bot.cogs['Helpers'].get_record('server', m.guild.id)
#         if not g['tt'].get('tl_channel'):
#             asyncio.ensure_future(ctx.send('The Gm or a master needs to set up a TL channel.\n'
#                            '`e.tt setchannel tl #abc123`'))
#             return False
#         elif not g['tt'].get('cq_number'):
#             asyncio.ensure_future(ctx.send('The Gm or a master should set the CQ number.\n'
#                            'This is the cq of the _next_ TL, not the one that\n'
#                            'was just killed.\n'
#                            '`e.tt setcq 1589`'))
#             return False
#         elif not g['tt'].get('timer_text') or not g.tt.get('ping_text') or not g.tt.get('now_text'):
#             asyncio.ensure_future(ctx.send(
#                 'The Gm or a master should set the timer texts.\n'
#                 'There are three separate texts to set.'))
#             return False
#         return True
#     return commands.check(_tl_checks)

# def when_check():
#     async def _when_check(ctx):
#         m = ctx.message
#         g = await ctx.bot.cogs['Helpers'].get_record('server', m.guild.id)
#         if not g.tt.get('when_channel'):
#             await ctx.send('GM or master needs to set up the when channel.\n'
#                            '`e.tt setchannel when #abc123`')
#             return False
#         return True
#     return commands.check(_when_check)

class TapTitans():
    """docstring for TapTitans"""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        self.last_check = int(time.time())

    async def timer_check(self):
        while self is self.bot.get_cog('TapTitans'):
            if int(time.time()) - self.last_check >= 9.999998:
                asyncio.ensure_future(self.helpers.update_tls())
            await asyncio.sleep(9.999999)

    

    @commands.group(pass_context=True, invoke_without_command=False, name="tt")
    async def tt(self, ctx):
        pass

    @tt.group(name='group', invoke_without_command=False)
    async def tt_group(self, ctx):
        pass

    @is_gm_or_master()
    @tt_group.command(name='add')
    async def tt_group_add(self, ctx, name='default'):
        if not name:
            asyncio.ensure_future(ctx.send('You need to supply a name when creating a group.'))
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = next((r for r in exists if r['name']==name.lower() and r['guild']==ctx.guild.id), None)
        if not exists:
            result = await self.helpers.sql_query_db(
                """INSERT INTO titanlord (id, "create", guild, name) VALUES (DEFAULT, $1, $2, $3)""",
                (datetime.utcnow(), ctx.guild.id, name.lower(),)
            )
            asyncio.ensure_future(ctx.send(f'Added new group with name: `{name}`!'))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{name}` already exists on `{ctx.guild.name}`.'))

    @is_gm_or_master()
    @tt_group.command(name='rename')
    async def tt_group_rename(self, ctx, name='default', newname='notdefault'):
        if not name or not newname:
            asyncio.ensure_future(ctx.send('You need to supply the old name and new name, in that order.'))
        exists = await self.helpers.sql_query_db('SELECT * FROM titanlord')
        new_exists = next((dict(r) for r in exists if r['name']==newname.lower() and r['guild']==ctx.guild.id), None)
        old_exists = next((dict(r) for r in exists if r['name']==name.lower() and r['guild']==ctx.guild.id), None)
        if not new_exists and old_exists:
            old_exists.update({'name': newname})
            result = await self.helpers.sql_update_record('titanlord', old_exists)
            asyncio.ensure_future(ctx.send(f'Renamed group `{name}` to `{newname}`!'))
        elif new_exists:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{newname}` already exists on `{ctx.guild.name}`.'))
        elif not old_exists:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{name}` does not exist on `{ctx.guild.name}`.'))


    @is_gm_or_master()
    @tt_group.command(name='get')
    async def tt_group_get(self, ctx, name='default'):
        g = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        g = next((dict(r) for r in g if r['name']==name.lower() and r['guild']==ctx.guild.id), None)
        s = await self.helpers.sql_query_db(
            'SELECT * FROM server'
        )
        s = next((dict(r) for r in s if r['id']==ctx.guild.id), None)
        if g and s:
            short_code = g.get('shortcode') or 'Clan'
            clan_name = g.get('clanname') or '`No clan name set`'
            cq_no = g.get('cq_number') or 1
            fields = {}
            roles = {'Grandmaster': "<@&{}>".format(s['roles'].get('grandmaster', '0'))}
            roles.update({k.title(): f"<@&{s['tt'].get(k, '0')}>" for k in ['master', 'captain', 'knight', 'recruit']})
            fields.update({'channels':
                '\n'.join('{}: {}'.format(
                    k.replace('_channel','').replace('channel', 'titanlord'), g[k] and f'<#{g[k]}>' or '`not set`'
                ) for k in g if k.endswith('channel'))
            })
            fields.update({f'{short_code} Roles': '\n'.join(f'{k}: {v}' for k,v in roles.items())})
            fields.update({f'{short_code} Ping intervals': ', '.join(f'`{x}`' for x in g.get('ping_at')) or '`not set`'})
            fields.update({f'{short_code} {k.title()} text': (g.get(k) or "None").format(
                TIME="**04:32:22**", CQ=cq_no, ROUND=1, SPAWN="12:23:32 UTC+10", GROUP=clan_name
            ) for k in ['timer', 'ping', 'now', 'round', 'after']})
            embed = await self.helpers.full_embed(
                f'TL Group: {short_code} - {clan_name}',
                fields=fields,
                inline=False)
            await ctx.send('',embed=embed)

    @tt.group(name='set', invoke_without_command=False)
    async def tt_set(self, ctx):
        pass

    @is_gm_or_master()
    @tt_set.command(name='channel')
    async def tt_set_channel(self, ctx, kind, channel, group="-default"):
        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]
        kinds = 'tl when paste report masters loa'.split()
        if kind not in kinds:
            asyncio.ensure_future(ctx.send('Channel type must be one of: `{}`'.format(
                '`, `'.join(k for k in kinds)
            )))
            return
        friendly_name=kind
        if kind in [k for k in kinds if k != 'tl']:
            friendly_name=kind
            kind = f'{kind}_channel'
        if kind == 'tl':
            kind = 'channel'
            friendly_name='tl'
        channel = await self.helpers.choose_channel(ctx, ctx.guild, channel)
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
        if exists:

            exists.update({kind: channel.id})
            result = await self.helpers.sql_update_record('titanlord', exists)
            asyncio.ensure_future(ctx.send(f'Set the `{friendly_name}` channel for `{group}` to {channel.mention}!'))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{name}` does not exist. Please create one first using `.tt group add`'))

    @is_gm_or_master()
    @tt_set.command(name='shortcode')
    async def tt_set_shortcode(self, ctx, shortcode, group="-default"):
        if not shortcode or not shortcode.isalnum() or not len(shortcode) < 6:
            asyncio.ensure_future(ctx.send(
                'Clan shortcodes must be letters or numbers and less than 6 characters. e.g. `T2RC`'
            ))
            return
        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        short_code_exists = next((dict(r) for r in exists if r['shortcode']==shortcode.upper()), None)
        if short_code_exists:
            asyncio.ensure_future(ctx.send('A clan has already claimed that shortcode. Try another. If this is your clan shortcode and somebody has falsely claimed it, join the support server: `.support`'))
        else:
            valid = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
            if valid:
                valid.update({'shortcode': shortcode.upper()})
                result = await self.helpers.sql_update_record('titanlord', valid)
                asyncio.ensure_future(ctx.send(f'Set the `shortcode` for `{group}` to `{shortcode.upper()}`!'))
            else:
                asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @is_gm_or_master()
    @tt_set.command(name='name')
    async def tt_set_name(self, ctx, *name, group="-default"):
        clanname = ' '.join(name)
        if name[-1].startswith('-'):
            clanname=' '.join(name[:-1])
        group = name[-1].startswith('-') and name[-1] or group
        if not clanname or len(clanname) > 20:
            asyncio.ensure_future(ctx.send(
                'Clan names must be less than 20 characters in length.'
            ))
            return
        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        clanname_exists = next((dict(r) for r in exists if r['clanname']==clanname), None)
        if clanname_exists:
            asyncio.ensure_future(ctx.send('A clan has already claimed that name. Try another. If this is your clan name and somebody has falsely claimed it, join the support server: `.support`'))
        else:
            valid = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
            if valid:
                valid.update({'clanname': clanname})
                result = await self.helpers.sql_update_record('titanlord', valid)
                asyncio.ensure_future(ctx.send(f'Set the `clan name` for `{group}` to `{clanname}`!'))
            else:
                asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @is_gm_or_master()
    @tt_set.command(name='timezone', aliases=['tz'])
    async def tt_set_timezone(self, ctx, timezone, group="-default"):
        if not re.match(r'^[0-9-+]+$', timezone):
            asyncio.ensure_future(ctx.send("Timezone must be a whole number (no decimals) between -12 and 15."))
            return
        elif not 16 > int(timezone) > -13:
            asyncio.ensure_future(ctx.send("Timezone must be a whole number (no decimals) between -12 and 15."))
            return
        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
        if exists:
            exists.update({'timezone': int(timezone)})
            if int(timezone) > -1:
                timezone = f'+{int(timezone)}'
            result = await self.helpers.sql_update_record('titanlord', exists)
            asyncio.ensure_future(ctx.send(f'Set the `timezone` for `{group}` to `{timezone}`!'))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @is_gm_or_master()
    @tt_set.command(name='cq')
    async def tt_set_cq(self, ctx, cq, group="-default"):
        if not cq.isnumeric() and not 0 < int(cq):
            asyncio.ensure_future(ctx.send(
                'You must supply a valid numerical value for the cq number.'))
            return
        
        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
        if exists:
            exists.update({'cq_number': int(cq)})
            result = await self.helpers.sql_update_record('titanlord', exists)
            asyncio.ensure_future(ctx.send(f'Set the `cq` for `{group}` to `{int(cq):,}`!'))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @is_gm_or_master()
    @tt_set.command(name='text', aliases=['message'])
    async def tt_set_text(self, ctx, kind, *text, group="-default"):
        msg_text = ' '.join(text)
        if text[-1].startswith('-'):
            msg_text=' '.join(text[:-1])
        group = text[-1].startswith('-') and text[-1] or group

        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]

        kinds = 'ping now timer round after'.split()
        if kind not in kinds:
            asyncio.ensure_future(ctx.send('Text type must be one of: `{}`'.format(
                '`, `'.join(k for k in kinds)
            )))
            return
        for unit in ['time', 'cq', 'round', 'spawn', 'timer', 'group']:
            msg_text = msg_text.replace(f'%{unit}%', '{'+unit.upper()+'}')
            msg_text = msg_text.replace(f'%{unit.upper()}%', '{'+unit.upper()+'}')
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
        if exists:
            exists.update({kind: msg_text})
            result = await self.helpers.sql_update_record('titanlord', exists)

            e = await self.helpers.build_embed(msg_text.format(
                TIME="**04:32:22**", CQ=822, ROUND=1, SPAWN="12:23:32 UTC+10", GROUP='Full Metal Titan'
            ), 0xffffff)
            asyncio.ensure_future(ctx.send(
                f'Set the `{kind.lower()}` text for `{group}` to:', embed=e
            ))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @is_gm_or_master()
    @tt_set.command(name='pings', aliases=['intervals'])
    async def setinterval(self, ctx, *pings, group="-default"):

        group = pings[-1].startswith('-') and pings[-1] or group
        if pings[-1].startswith('-'):
            pings=pings[:-1]

        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]

        if not all([x.isnumeric() for x in pings]):
            asyncio.ensure_future(ctx.send('You must supply space-sparated whole numbers. e.g. `15 5 1`'))
            return
        pings = [int(p) for p in pings]
        
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
        if exists:
            exists.update({'ping_at': pings})
            result = await self.helpers.sql_update_record('titanlord', exists)
            pings = '`, `'.join(map(str, pings))
            asyncio.ensure_future(ctx.send(f'Ping intervals for `{group}` set to: `{pings}`'))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))


    @is_gm_or_admin()
    @tt_set.command(name='rank', no_pm=True)
    async def _setrank(self, ctx, rank, role):
        ranks = 'master knight captain recruit guest vip alumni applicant timer vip'.split()
        if rank not in ranks:
            asyncio.ensure_future(ctx.send('The rank must be a valid name of an in-game role'
                ' or a tt2 related rank. You can choose from: `{}`'.format(
                    '`, `'.join(r for r in ranks)
                )
            ))
            return
        guild = ctx.guild
        if role:
            if role.startswith('#'):
                role = role[1:]
            g = await self.helpers.get_record('server', ctx.guild.id)
            result =await self.helpers.choose_role(ctx, ctx.guild, role)
            if result:
                g['tt'][rank] = result.id
                asyncio.ensure_future(self.helpers.try_mention(ctx, f'{rank} role', result))

    @is_gm_or_master()
    @commands.command(name='loas', aliases=['absences'])
    async def _loas(self, ctx):
        m = ctx.message
        g = await self.helpers.get_record('server', m.guild.id)
        if not g['tt'].get('loa'):
            return
        result = []
        now = datetime.utcnow()

        for user, loa in sorted(g['tt'].get('loa').items(), key=lambda k: k[1]):

            expires = datetime.utcfromtimestamp(loa)
            if loa-now.timestamp()>3600:
                user = f'<@{user}>'
                result.append('{} - {}'.format(user,
                    expires.strftime('%a, %d %B at %I:%M%p UTC')))
        e = await self.helpers.build_embed('Currently active LOAs:\n\n{}'.format(
            '\n'.join(result)
        ), 0xffffff)
        asyncio.ensure_future(ctx.send(embed=e))

    # @has_any_clan_role()
    @commands.command(name='loa', aliases=['absent'])
    async def _loa(self, ctx, timeframe, group="-default"):
        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
        msg = None
        if not exists:
            msg = f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'
        elif not await self.helpers.tl_has_settings(exists, c=('when_channel')):
            msg = f'The TL group `{group}` does not have a `when_channel` set up. Ask a master to do `.tt set channel when`'
        if msg:
            asyncio.ensure_future(ctx.send(msg))
            return
        m = ctx.message
        a = m.author
        g = await self.helpers.get_record('server', m.guild.id)
        if not g['tt'].get('loa'):
            g['tt']['loa']={}
        _next, _units = await process_time(timeframe)
        if not _next or timeframe in 'clearstop':
            g['tt']['loa'][str(a.id)] = datetime.utcnow().timestamp()
            asyncio.ensure_future(ctx.send(':ideograph_advantage: LoA cleared.'))
            return
        g['tt']['loa'][str(a.id)] = (datetime.utcnow()+_next).timestamp()
        units = ', '.join(f'{v} {k}' for k, v in _units.items())
        asyncio.ensure_future(ctx.send(
            f':ideograph_advantage: Leave of Absence filed for **{units}**'))
        if g['tt'].get('masters_channel'):
            asyncio.ensure_future(m.guild.get_channel(
                g['tt']['masters_channel']
            ).send(f':ideograph_advantage: {a.mention} just filed a leave of absence for {units}'))

    @commands.command(name='titancount', aliases=['ip'])
    async def _titancount(self, ctx, stage='5000', ip='0'):
        if stage.isnumeric() and ip.isnumeric():
            count = int(stage)//500*2+8-int(ip)
            e = await self.helpers.full_embed(
                f"Titancount at stage **{stage}** (IP level {ip}) would be: **{count}**",
                colour=0x8ad24f,
                author=dict(name='TT2 Titancount',
                            image="https://i.imgur.com/MY8x9aY.png")
            )
            asyncio.ensure_future(ctx.send(embed=e))

    @commands.group(name='tl', aliases=['boss', 'titanlord'], no_pm=True)
    async def tl(self, ctx):
        pass

    @is_gm_or_master()
    @tl.command(name='clear')
    async def tl_clear(self, ctx, group="-default"):
        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
        if not exists:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))
            return
        exists.update({'next': None, 'message': 0, 'when_message': 0})
        await self.helpers.sql_update_record('titanlord', exists)
        asyncio.ensure_future(ctx.send(f'Successfully cleared the `{group}` boss timer!'))

    @tl.command(name='when')
    async def tl_when(self, ctx, group="-default"):
        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
        msg = None
        when_channel, clan = exists.get('when_channel'), exists.get('clanname') or 'Clan'
        boss_message = exists.get('message') or 0
        if not exists:
            msg = f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'
        elif not when_channel or None:
            msg = f'The TL group `{group}` does not have a `when_channel` set up. Ask a master to do `.tt set channel when`'
        elif ctx.channel.id != when_channel:
            msg = f'The `{clan}` `when` channel is: <#{when_channel}>'
        elif not boss_message:
            msg = f'There does not seem to be a {clan} boss active right now. :/'
        if msg:
            asyncio.ensure_future(ctx.send(msg))
            return

        timer = await self.helpers.get_tl_time_string(exists)
        mx = await self.bot.get_channel(exists['when_channel']).send(timer)
        exists.update({'when_message': mx.id})
        result = await self.helpers.sql_update_record('titanlord', exists)


    @is_gm_or_master()
    @tl.command(name='in')
    async def tl_in(self, ctx, *time, group="-default"):
        time_text = ' '.join(time)
        if time[-1].startswith('-'):
            time_text=' '.join(time[:-1])
        group = time[-1].startswith('-') and time[-1] or group

        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        else:
            group = group[1:]
        
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = next((dict(r) for r in exists if r['name']==group.lower() and r['guild']==ctx.guild.id), None)
        msg = None
        if not exists:
            msg = f'A TL group with name `{name}` does not exist. Please create one first using `.tt group add`'
        elif not exists.get('channel'):
            msg = 'You need to set up a titanlord channel first! `.tt set channel tl`'
        elif not exists.get('cq_number'):
            msg = 'You need to set the CQ number first. `.tt set cq`'
        elif not exists.get('clanname'):
            msg = 'You need to set the clan name. `.tt set name`'
        elif not exists.get('ping_at'):
            msg = 'You should set ping intervals with `.tt set pings`'
        elif not exists.get('now'):
            msg = 'You should set now text with `.tt set text now`'
        elif not exists.get('ping'):
            msg = 'You should set ping text with `.tt set text ping`'
        elif not exists.get('timer'):
            msg = 'You should set a generic (non-ping) timer message with `.tt set text timer`'
        if msg:
            asyncio.ensure_future(ctx.send(msg))
            return

        time = ''.join(time_text)

        _next, _units = await self.helpers.process_time(time)
        now = datetime.utcnow()
        mx = await self.bot.get_channel(exists['channel']).send('Loading timer. If this takes a very long time, let <@!305879281580638228> know!')
        modded_ = await self.helpers.mod_timedelta(_next)
        mapped_ = await self.helpers.map_timedelta(modded_)

        exists.update({'next': now+_next, 'message': mx.id, 'pinged_at': 3600})
        result = await self.helpers.sql_update_record('titanlord', exists)

        asyncio.ensure_future(ctx.send('Timer set for: `{}`'.format(
            '`, `'.join([f'{x} {y}' for x, y in mapped_[1:]])
        )))
    
    @is_gm_or_master()
    @tt.command(name='report')
    async def _report(self, ctx):
        TD = dt.date.today()
        TD = datetime(TD.year, TD.month, TD.day, 0, 0)
        this_monday = TD + timedelta(days=-TD.weekday())
        last_monday = TD + timedelta(days=-TD.weekday(), weeks=-1)
        g = await self.helpers.get_record('server', ctx.message.guild.id)
        c = g.tt.get('paste_channel')
        print(c)
        if c:
            c = ctx.message.guild.get_channel(c)
            messages = await c.history(limit=100).flatten()
            result = [m for m in messages]
            cqs = [int(re.match(r'```CQ (\d+)', r.content).group(1))
                   for r in result
                   if re.match(r'```CQ \d+', r.content)
                   and r.created_at > last_monday
                   and r.created_at < this_monday]
            result = [r.content.split('\n')
                      for r in result
                      if r.content.startswith('```')
                      and r.created_at > last_monday
                      and r.created_at < this_monday]
            result = [[
                s.replace('```','').split(',') for s in r
                if len(s.split(','))==4
                and not s.startswith('```')
                and s.split(',')[0].isnumeric()
            ] for r in result]

            headers = ['rank', 'name', 'id', 'damage']
            started, ended, total = min(cqs), max(cqs), len(result)
            missed = ended - started - total
            all_hits = list(chain.from_iterable(result))
            #pprint(all_hits)
            result = defaultdict(lambda: dict(
                id='', name='', hit=0, dmg=0, atd=0
            ))
            for hit in all_hits:
                id = hit[2]
                if not result[id]['id']:
                    result[id]['id']=id
                if int(hit[3])>30000000:
                    result[id]['hit'] += 1
                    result[id]['dmg'] += int(hit[3])
                if not result[id]['name']:
                    u = next((x.id for x in self.bot._users
                              if x.tt.get('code')==hit[2]), hit[1])
                    
                    if str(u).isnumeric():
                        u = ctx.guild.get_member(int(u))
                        if u:
                            u = u.mention
                        result[id]['name']=u
                    else:
                        result[id]['name']=hit[1]
            final = []
            for id, data in result.items():
                result[id]['atd'] = round((result[id]['hit']+missed)/total*100)
                final.append(result[id])
            final = sorted(final, key=lambda x: x['atd'], reverse=True)

            colours = [0x146B3A, 0xF8B229, 0xEA4630, 0xBB2528]
            started_at = 0
            report_to = c = g.tt.get('report_channel')
            if report_to:
                report_to = ctx.message.guild.get_channel(report_to)
                for chunk in self.helpers.chunker(final, 21):
                    result = []
                    for i,r in enumerate(chunk):
                        name = f'`#{started_at*18+i+1:02}`: `{r["atd"]:02}%` (`{self.helpers.human_format(r["dmg"]): <7}`)'
                        # e3.add_field(
                            # name=f'{name:<24}',
                            # value=r['name'], inline=True)
                        result.append(f'{name} - {r["name"]}')
                    e3 = await self.helpers.build_embed(
                        'Attendance report part {}.\n\n{}'.format(
                            started_at+1, "\n".join(result)
                        ), colours[started_at]
                    )
                    asyncio.ensure_future(report_to.send(embed=e3))
                    started_at+=1


    


    # @is_gm_or_master()
    # @tl_checks()
    # @tl.command(name='clear', aliases=['wipe'])
    # async def _clear(self, ctx):
    #     g = await self.helpers.get_record('server', ctx.message.guild.id)
    #     g.tt['next_boss'] = 0
    #     g.tt['boss_message'] = 0
    #     g.tt['when_message'] = 0
    #     asyncio.ensure_future(ctx.send(
    #         ':ideograph_advantage: Cleared the boss timer!'))

    @commands.command(name='ttconvert', alias=["ttnotation"])
    async def _convert(self, ctx, val: str='1e+5000'):
        result = None
        f, t = 'scientific', 'letter'
        mode = await self.helpers.choose_conversion(val)
        if mode == 0:
            result = await self.helpers.from_scientific(val)
        elif mode == 1:
            result = await self.helpers.to_scientific(val)
            f, t = 'letter', 'scientific'
        e = await self.helpers.full_embed(
            f'Conversion of **{val}** from **{f}** to **{t}** is: **{result}**'
        )
        asyncio.ensure_future(ctx.send(embed=e))
def setup(bot):
    cog = TapTitans(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(cog.timer_check())
    bot.add_cog(cog)
