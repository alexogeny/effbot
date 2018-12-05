import discord
from datetime import datetime, timedelta
from discord.ext import commands
from string import ascii_lowercase
from itertools import chain, zip_longest
from random import choice
from math import log, log10, floor, ceil
from collections import defaultdict
from csv import DictReader
import functools
import asyncio
import re
import datetime as dt
import time
from .helpers import has_any_role, tournament_forecast
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

async def advance_start(level: int) -> float:
    return await round_to_x(min(.003 * pow(log(level+4),2.741), .9)*100, 4)

async def clan_damage(level: int) -> float:
    return await round_to_x(pow(1.0233, level) + pow(level, 1.05), 2)


async def base_relics_amount(stage: int) -> int:
    return (
        3 * pow(1.21, pow(stage, .48))
    ) + (
        1.5 * (stage-110)
    ) + (
        pow(1.002, pow(stage, min(
            (1.005*(pow(stage, 1.1*.0000005+1))), 1.0155
        )))
)

async def artifact_boost(level: int, per_level: int, cost_exponent: float,
                         growth_rate, growth_max, growth_exponent) -> int:
    return round(1 + per_level * pow(level, pow(
        (1 + (cost_exponent - 1) * min(growth_rate * level, growth_max)),
        growth_exponent
        )
    ) + .5)

async def primary_craft_boost(level: int) -> float:
    return pow(1.02, level - 1)
async def round_to_x(x, n):
    return round(x, -int(floor(log10(x))) + (n - 1))
async def secondary_craft_boost(level: int) -> float:
    return pow(1.1, level - 1)

async def bonus_relics_amount(stage, bos, sets, craftpower) -> int:
    return await round_to_x(await base_relics_amount(stage) * await artifact_boost(
        bos, .05, 2.5, .0001, .12, .5
    ) * pow(1.5 * await primary_craft_boost(craftpower), max(sets, 0)), 3)

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


def has_clan_roles(*roles):
    async def _has_clan_roles(ctx):
        m, a, g = ctx.message, ctx.author, await ctx.bot.get_cog('Helpers').get_record('server',ctx.guild.id)
        a_roles = [r.id for r in a.roles]
        _roles = [r.split('.') for r in roles]
        for key, role in _roles:
            if g[key].get(role) or None in a_roles:
                return True
        asyncio.ensure_future(ctx.send('Sorry, you do not have permission.'))
        return False
    return commands.check(_has_clan_roles)

class TapTitans():
    """docstring for TapTitans"""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        self.last_check = int(time.time())
        self.tl_icons = '2Zep8pE Y8OWqXd r7i7rlR VLjcRBe TBZAL4A eYtmbjg Y6jfEhM'.split()
        self.load_txt = 'Loading... If this takes ages, let **effrill3#0001** know!'
        self.error_map = {
            'channel': 'No titanlord channel set. `.tt set channel tl <channel>`',
            'cq_number': 'No CQ number set. `.tt set cq <cq>`',
            'clanname': 'No clan-name set. `.tt set name <name...>`',
            'ping_at': 'No ping intervals set. `.tt set pings <pings...>`',
            'now': 'No boss-up text set. `.tt set text now <text...>`',
            'ping': 'No ping text set. `.tt set text ping <text...>`',
            'timer': 'No timer text set. `.tt set text timer <text...>`'
        }



    async def timer_check(self):
        while self is self.bot.get_cog('TapTitans'):
            if int(time.time()) - self.last_check >= 9.999998:
                asyncio.ensure_future(self.helpers.update_tls())
            await asyncio.sleep(9.999999)

    @commands.command(name='clanstats', aliases=['tt2clan'])
    async def _clanstats(self, ctx, level=None):
        if not level:
            await ctx.send('Derp, don\'t forget the CQ level!')
            return
        try:
            int(level)
        except:
            await ctx.send('You need to supply a whole number between **1** and **5000**')
            return

        if not 0 < int(level) <= 5000:
            asyncio.ensure_future(ctx.send('CQ level must be between **1** and **5000**'))
            return
        level = int(level)
        dmg_bns = await self.helpers.humanize_decimal(await clan_damage(level))
        as_ = await advance_start(level)
        e = await self.helpers.full_embed(
            f'\nBoss HP - **{self.helpers.human_format(boss_hitpoints(level))}**'
            f'\nDamage Bonus - **{dmg_bns}**'
            f'\nAdvanced Start - **{as_}%**'
        )
        asyncio.ensure_future(ctx.send(
            f'Clan stats for a level **{level}** clan:', embed=e
        ))

    @commands.command(name='tournament', aliases=['tournaments', 'tourney', 'tourneys'], no_pm=True)
    async def _tourney(self, ctx):
        upcoming = await tournament_forecast(last=3)
        #asyncio.ensure_future(ctx.send(await self.helpers.tournament_time_remains()))
        e = '\n\n'.join(upcoming)
        asyncio.ensure_future(ctx.send('Upcoming TT2 tournaments:\n\n{}'.format(e)))

    @commands.group(pass_context=True, invoke_without_command=False, name="tt")
    async def tt(self, ctx):
        pass

    @tt.group(name='group', invoke_without_command=False)
    async def tt_group(self, ctx):
        pass

    @tt_group.command(name='list')
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_group_list(self, ctx):
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = [dict(r) for r in exists if r['guild']==ctx.guild.id]

        if not exists:
            asyncio.ensure_future(ctx.send('Could not find any groups. :<'))
            return
        exists = ', '.join([f'`{r["name"]}`' for r in exists])
        asyncio.ensure_future(ctx.send(f'The following TL groups exist in this server: {exists}'))

    @tt_group.command(name='add')
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_group_add(self, ctx, name='default'):
        if not name:
            asyncio.ensure_future(ctx.send('You need to supply a name when creating a group.'))
        exists = await self.get_tl_from_db(ctx, name)
        if not exists:
            result = await self.helpers.sql_query_db(
                """INSERT INTO titanlord (id, "create", guild, name) VALUES (DEFAULT, $1, $2, $3)""",
                (datetime.utcnow(), ctx.guild.id, name.lower(),)
            )
            asyncio.ensure_future(ctx.send(f'Added new group with name: `{name}`!'))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{name}` already exists on `{ctx.guild.name}`.'))

    @tt_group.command(name='delete')
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_group_delete(self, ctx, name=None):
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = [dict(r)['name'] for r in exists if r['guild']==ctx.guild.id]

        if not exists:
            asyncio.ensure_future(ctx.send('Could not find any groups on this server. :<'))
            return
        exists_f = ', '.join([f'`{r}`' for r in exists])
        if not name:
            asyncio.ensure_future(ctx.send('You need to tell me which group to delete! Available groups: {}'.format(exists_f)))
            return
        elif name.lower() not in exists:
            asyncio.ensure_future(ctx.send('You need to specify an existing group. Available groups: {}'.format(exists_f)))
            return
        await ctx.send(f'The group `{name.lower()}` WILL BE DELETED. Please confirm!')
        result = await self.helpers.choose_from(ctx, ['confirm'],
            'Type `1` to confirm or `c` to cancel.')
        if not result:
            return
        if len(exists)==1:
            await ctx.send('This is the ONLY group. Are you sure?')
            result = await self.helpers.choose_from(ctx, ['confirm'],
            'Type `1` to confirm or `c` to cancel.')
            if not result:
                return

        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.execute(
                    "DELETE FROM Titanlord WHERE Titanlord.guild = $1 AND Titanlord.name = $2", ctx.guild.id, name
                )
        if result:
            asyncio.ensure_future(ctx.send(f'Successfully deleted the group: `{name}`'))
        else:
            asyncio.ensure_future(ctx.send('Did not have anything to delete.'))


    @tt_group.command(name='rename')
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_group_rename(self, ctx, name='default', newname='notdefault'):
        if not name or not newname:
            asyncio.ensure_future(ctx.send('You need to supply the old name and new name, in that order.'))
        exists = await self.helpers.sql_query_db('SELECT * FROM titanlord')
        new_exists = next((dict(r) for r in exists if (r['name'] or '').lower()==newname.lower() and r['guild']==ctx.guild.id), None)
        old_exists = next((dict(r) for r in exists if (r['name'] or '').lower()==name.lower() and r['guild']==ctx.guild.id), None)
        if not new_exists and old_exists:
            old_exists.update({'name': newname.lower()})
            result = await self.helpers.sql_update_record('titanlord', old_exists)
            asyncio.ensure_future(ctx.send(f'Renamed group `{name}` to `{newname}`!'))
        elif new_exists:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{newname}` already exists on `{ctx.guild.name}`.'))
        elif not old_exists:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{name}` does not exist on `{ctx.guild.name}`.'))

    @commands.command(name='sttget', aliases=['super tt get'])
    async def sttget(self, ctx, name='default'):
        try:
            guild = self.bot.get_guild(440785686438871040)
            member = guild.get_member(ctx.author.id)
            res = [r for r in member.roles if r.id == 478831581142974464]
        except:
            return
        else:
            if not res:
                return
            g = await self.helpers.sql_query_db(
                'SELECT * FROM titanlord'
            )
            g = next((dict(r) for r in g if (r['name'] or '').lower()==name.lower() and r['guild']==ctx.guild.id), None)
            s = await self.helpers.sql_query_db(
                'SELECT * FROM server'
            )
            s = next((dict(r) for r in s if r['id']==ctx.guild.id), None)
            if not g:
                asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))
                return
            if g and s:
                short_code = g.get('shortcode') or 'Clan'
                clan_name = g.get('clanname') or '`No clan name set`'
                cq_no = g.get('cq_number') or 0
                fields = {}
                roles = {'Grandmaster': "<@&{}>".format(s['roles'].get('grandmaster', '0'))}
                roles.update({k.title(): f"<@&{s['tt'].get(k, '0')}>" for k in ['master', 'captain', 'knight', 'recruit', 'timer', 'mercenary', 'applicant', 'alumni']})
                rmap = dict(ms='Max Stage', tcq='Total Clan Quests',
                            prestige='Prestige Count', tpcq='Taps Per Clan Quest',
                            hpcq='Hits Per Clan Quest')
                reqs = {rmap[r]: g[f'{r}_requirement'] or 0 for r in 'ms tcq prestige tpcq hpcq'.split()}
                fields.update({'requirements':
                    '\n'.join('{}: {:,}'.format(k, int(v)) for k, v in reqs.items())
                })

                fields.update({'channels':
                    '\n'.join('{}: {}'.format(
                        k.replace('_channel','').replace('channel', 'titanlord'), g[k] and f'<#{g[k]}>' or '`not set`'
                    ) for k in g if k.endswith('channel'))
                })
                fields.update({f'{short_code} CQ:': f'{cq_no or "`not set`"}'})
                fields.update({f'{short_code} Ranks': '\n'.join(f'{k}: {v}' for k,v in roles.items())})
                fields.update({f'{short_code} Ping intervals': ', '.join(f'`{x}`' for x in g.get('ping_at')) or '`not set`'})
                fields.update({f'{short_code} {k.title()} text': (g.get(k) or "None").format(
                    TIME="**04:32:22**", CQ=cq_no, ROUND=1, SPAWN="12:23:32 UTC+10", GROUP=clan_name
                ) for k in ['timer', 'ping', 'now', 'round', 'after']})
                fields.update({'Notes':
                    ('There are a few template tags available when setting text:'
                     '\n`%time%` time until the boss spawns'
                     '\n`%cq%` the cq number of the boss'
                     '\n`%spawn%` the time when the boss spawns'
                     '\n`%round%` the round number of the boss'
                     '\n`%group%` the group the titanlord belongs to'
                     '\n`%everyone%` set an everyone ping without pinging everyone setting it up'
                     '\n`%br%` adds a line break to the text'
                     #'\n`%user%` mentions the user who set up the timer'
                     )
                })
                embed = await self.helpers.full_embed(
                    f'TL Group: {short_code} - {clan_name}',
                    fields=fields,
                    inline=False)
                await ctx.send('',embed=embed)

    @tt.command(name='requirements', aliases=['reqs'])
    async def tt_requirements(self, ctx, name='default'):
        g = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        g = next((dict(r) for r in g if (r['name'] or '').lower()==name.lower() and r['guild']==ctx.guild.id), None)
        if not g:
            asyncio.ensure_future(ctx.send('Oops, could not find a group with that name.'))
            return
        short_code = g.get('shortcode') or 'Clan'
        cname = g.get('clanname') or 'Clan'
        if short_code == cname:
            cname = short_code
        else:
            cname = f'{cname} ({short_code})'
        rmap = dict(ms='Max Stage', tcq='Total Clan Quests',
                    prestige='Prestige Count', tpcq='Taps Per Clan Quest',
                    hpcq='Hits Per Clan Quest')
        reqs = {rmap[r]: g[f'{r}_requirement'] or 0 for r in 'ms tcq prestige tpcq hpcq'.split()}
        result = '\n'.join('{} - **{:,}**'.format(k, int(v)) for k, v in reqs.items())
        if g.get('text_requirement'):
            result = '{}\n\nNote: {}'.format(result, g.get('text_requirement').replace('%br%', '\n').replace('%BR%', '\n'))
        asyncio.ensure_future(ctx.send(
            "The requirements to join **{}** are as follows:\n{}".format(
                cname, result
            )
        ))

    @tt_group.command(name='get')
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_group_get(self, ctx, name='default', section='all'):
        g = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        g = next((dict(r) for r in g if (r['name'] or '').lower()==name.lower() and r['guild']==ctx.guild.id), None)
        s = await self.helpers.sql_query_db(
            'SELECT * FROM server'
        )
        s = next((dict(r) for r in s if r['id']==ctx.guild.id), None)
        if not g:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))
            return
        if g and s:
            short_code = g.get('shortcode') or 'Clan'
            clan_name = g.get('clanname') or '`No clan name set`'
            cq_no = g.get('cq_number') or 0
            fields = {}
            roles = {'Grandmaster': "<@&{}>".format(s['roles'].get('grandmaster', '0'))}
            roles.update({k.title(): f"<@&{s['tt'].get(k, '0')}>" for k in ['master', 'captain', 'knight', 'recruit', 'timer', 'mercenary', 'applicant', 'alumni']})
            rmap = dict(ms='Max Stage', tcq='Total Clan Quests',
                        prestige='Prestige Count', tpcq='Taps Per Clan Quest',
                        hpcq='Hits Per Clan Quest')
            reqs = {rmap[r]: g[f'{r}_requirement'] or 0 for r in 'ms tcq prestige tpcq hpcq'.split()}
            if section.lower() == 'all' or section.lower().startswith('req'):
                fields.update({'requirements':
                    '\n'.join('{}: {:,}'.format(k, int(v)) for k, v in reqs.items())
                })


            if section.lower() == 'all' or section.lower().startswith('chan'):
                fields.update({'channels':
                    '\n'.join('{}: {}'.format(
                        k.replace('_channel','').replace('channel', 'titanlord'), g[k] and f'<#{g[k]}>' or '`not set`'
                    ) for k in g if k.endswith('channel'))
                })

            if section.lower() == 'all' or section.lower().startswith('rank'):
                fields.update({f'{short_code} Ranks': '\n'.join(f'{k}: {v}' for k,v in roles.items())})
            if section.lower() == 'all':
                fields.update({f'{short_code} CQ:': f'{cq_no or "`not set`"}'})
                fields.update({f'{short_code} Ping intervals': ', '.join(f'`{x}`' for x in g.get('ping_at')) or '`not set`'})
            if section.lower() == 'all' or section.lower().startswith('tex'):
                fields.update({f'{short_code} {k.title()} text': (g.get(k) or "None").format(
                    TIME="**04:32:22**", CQ=cq_no, ROUND=1, SPAWN="12:23:32 UTC+10", GROUP=clan_name
                ) for k in ['timer', 'ping', 'now', 'round', 'after']})
            if section.lower() == 'all' or section.lower().startswith('tex'):
                fields.update({'Notes':
                    ('There are a few template tags available when setting text:'
                     '\n`%time%` time until the boss spawns'
                     '\n`%cq%` the cq number of the boss'
                     '\n`%spawn%` the time when the boss spawns'
                     '\n`%round%` the round number of the boss'
                     '\n`%group%` the group the titanlord belongs to'
                     '\n`%everyone%` set an everyone ping without pinging everyone setting it up'
                     '\n`%br%` adds a line break to the text'
                     #'\n`%user%` mentions the user who set up the timer'
                     )
                })
            embed = await self.helpers.full_embed(
                f'TL Group: {short_code} - {clan_name}',
                fields=fields,
                inline=False)
            await ctx.send('',embed=embed)

    # @tt_group.command(name='setup')
    # @has_any_role('roles.grandmaster', 'tt.master')
    # async def tt_group_setup

    @tt.group(name='set', invoke_without_command=False)
    #@has_clan_roles('roles.grandmaster', 'tt.master')
    async def tt_set(self, ctx):
        pass

    @tt_set.group(name='defaults')
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_set_defaults(self, ctx, group="-default"):
        group = await self.is_valid_groupname(group, ctx)
        if not group:
            return
        await ctx.send('This command does the following:\n- set default options (except for channels)\n- override any existing values.\nValues that will be set: `timer text`, `now text`, `ping text`, `round text`, `pings`.\nIt will not set up channels. You will still need to set up roles like `timer` and `recruit`.')
        result = await self.helpers.choose_from(ctx, ['confirm'],
            'Type `1` to confirm or `c` to cancel.')
        if not result:
            return
        exists = await self.get_tl_from_db(ctx, group)
        if not exists:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))
            return
        exists.update({
            'ping_at': [60, 5, 1],
            'timer': '{TIME} until the boss spawns!',
            'now': 'BOSS ALIVE @everyone! KILL IT!!!',
            'ping': '{TIME} until the boss spawns, @everyone! Get ready!!',
            'round': 'Round {ROUND} reading for the taking! Go slay, @everyone'
        })
        await self.helpers.sql_update_record('titanlord', exists)
        asyncio.ensure_future(ctx.send(
            f'Successfully updated defaults. To check them out, do `.tt group get {group}`'))

    @tt_set.command(name='channel')
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_set_channel(self, ctx, kind, channel, group="-default"):
        group = await self.is_valid_groupname(group, ctx)
        if not group:
            return
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
        if not channel:
            asyncio.ensure_future(ctx.send('Hmm, looks like that channel does not exist. Try a different search? You can also mention a channel.'))
            return
        try:
            perms = ctx.guild.get_member(self.bot.user.id).permissions_in(channel)
        except:
            asyncio.ensure_future(ctx.send('I do not have read access to {}'.format(channel.mention)))
            return
        if not perms.send_messages:
            asyncio.ensure_future(ctx.send('I cannot send messages to {}'.format(channel.mention)))
            return
        elif not perms.manage_messages:
            asyncio.ensure_future(ctx.send('I cannot manage messages in {}'.format(channel.mention)))
            return
        elif not perms.embed_links and not perms.attach_files:
            asyncio.ensure_future(ctx.send('I cannot attach links or files in {}'.format(channel.mention)))
            return
        elif not perms.mention_everyone:
            asyncio.ensure_future(ctx.send('I cannot mention **everyone** in {}'.format(channel.mention)))
            return
        exists = await self.get_tl_from_db(ctx, group)
        if exists:

            exists.update({kind: channel.id})
            result = await self.helpers.sql_update_record('titanlord', exists)
            asyncio.ensure_future(ctx.send(f'Set the `{friendly_name}` channel for `{group}` to {channel.mention}!'))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @tt_set.command(name='shortcode')
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_set_shortcode(self, ctx, shortcode, group="-default"):
        if not shortcode or not shortcode.isalnum() or not len(shortcode) < 6:
            asyncio.ensure_future(ctx.send(
                'Clan shortcodes must be letters or numbers and less than 6 characters. e.g. `AM`'
            ))
            return
        group = await self.is_valid_groupname(group, ctx)
        if not group:
            return
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        short_code_exists = next((dict(r) for r in exists if r['shortcode']==shortcode.upper()), None)
        if short_code_exists:
            asyncio.ensure_future(ctx.send('A clan has already claimed that shortcode. Try another. If this is your clan shortcode and somebody has falsely claimed it, join the support server: `.support`'))
        else:
            valid = next((dict(r) for r in exists if (r['name'] or '').lower()==group.lower() and r['guild']==ctx.guild.id), None)
            if valid:
                valid.update({'shortcode': shortcode.upper()})
                result = await self.helpers.sql_update_record('titanlord', valid)
                asyncio.ensure_future(ctx.send(f'Set the `shortcode` for `{group}` to `{shortcode.upper()}`!'))
            else:
                asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @tt_set.command(name='name')
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_set_name(self, ctx, *cname, group="-default"):
        clanname, group = await self.munge_group(cname, group)
        if not clanname:
            return

        if len(clanname) > 20:
            asyncio.ensure_future(ctx.send(
                'Clan names must be less than 20 characters in length.'
            ))
            return
        if not group:
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
        )
        exists = [dict(r) for r in exists]
        clanname_exists = next((r for r in exists if (r['clanname'] or '').lower().strip().replace(' ', '').replace('_','')==clanname.lower().strip().replace(' ', '').replace('_','')), None)
        if clanname_exists is not None:
            asyncio.ensure_future(ctx.send('A clan has already claimed that name. Try another. If this is your clan name and somebody has falsely claimed it, join the support server: `.support`'))
            return
        valid = next((r for r in exists if (r['name'] or '').lower()==group.lower() and r['guild']==ctx.guild.id), None)
        if valid:
            valid.update({'clanname': clanname})
            result = await self.helpers.sql_update_record('titanlord', valid)
            asyncio.ensure_future(ctx.send(f'Set the `clan name` for `{group}` to `{clanname}`!'))
            return
        asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @tt_set.command(name='timezone', aliases=['tz'])
    @has_any_role('roles.grandmaster', 'tt.master')
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
        exists = await self.get_tl_from_db(ctx, group)
        if exists:
            exists.update({'timezone': int(timezone)})
            if int(timezone) > -1:
                timezone = f'+{int(timezone)}'
            result = await self.helpers.sql_update_record('titanlord', exists)
            asyncio.ensure_future(ctx.send(f'Set the `timezone` for `{group}` to `{timezone}`!'))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @tt_set.command(name='cq')
    @has_any_role('roles.grandmaster', 'tt.master')
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
        exists = await self.get_tl_from_db(ctx, group)
        if exists:
            exists.update({'cq_number': int(cq)})
            result = await self.helpers.sql_update_record('titanlord', exists)
            asyncio.ensure_future(ctx.send(f'Set the `cq` for `{group}` to `{int(cq):,}`!'))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @tt_set.command(name='text', aliases=['message'])
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_set_text(self, ctx, kind, *text, group="-default"):
        if not kind or not text:
            asyncio.ensure_future(ctx.send('Oops, did you supply the right arguments? `tt set text <type> <message> <-group>'))
            return
        msg_text, group = await self.munge_group(text, group)

        if not group:
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return

        kinds = 'ping now timer round after'.split()
        if kind not in kinds:
            asyncio.ensure_future(ctx.send('Text type must be one of: `{}`'.format(
                '`, `'.join(k for k in kinds)
            )))
            return

        if kind in ['timer', 'ping'] and '%time%' not in msg_text.lower() and '{time}' not in msg_text.lower():
            asyncio.ensure_future(ctx.send(
                'Oops, did you drop this: `%time%`? This needs to be in the text, otherwise you won\'t know when the boss spawns!'
            ))
            return

        for unit in ['time', 'cq', 'round', 'spawn', 'timer', 'group']:
            msg_text = msg_text.replace(f'{{unit}}', '{'+unit.upper()+'}')
            msg_text = msg_text.replace(f'%{unit}%', '{'+unit.upper()+'}')
            msg_text = msg_text.replace(f'%{unit.upper()}%', '{'+unit.upper()+'}')
        msg_text = msg_text.replace('%everyone%', '@everyone')
        msg_text = msg_text.replace('{everyone}', '@everyone')
        msg_text = msg_text.replace('%br%', '\n')
        msg_text = msg_text.replace('{br}', '\n')

        exists = await self.get_tl_from_db(ctx, group)
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

    @tt_set.command(name='requirement', aliases=['req'])
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tt_set_requirement(self, ctx, kind, *value, group="-default"):
        if not group.startswith('-'):
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        group = group[1:]

        kinds = 'ms tcq prestige tpcq hpcq text ttkfree'.split()

        if kind not in kinds:
            asyncio.ensure_future(ctx.send('Text type must be one of: `{}`'.format(
                '`, `'.join(k for k in kinds)
            )))
            return
        if kind not in ['text', 'ttkfree'] and not value[0].isnumeric():
            asyncio.ensure_future(ctx.send('You need to supply a whole number for `{kind} requirement`'))
            return
        else:
            if not value[-1].startswith('-') and not group:
                asyncio.ensure_future(ctx.send('You did not supply a group.'))
                return
            elif value[-1].startswith('-'):
                group, value = value[-1][1:], ' '.join(value[0:-1])
            else:
                value = ' '.join(value)

        exists = await self.get_tl_from_db(ctx, group)
        if exists:
            msg = ''
            if kind != 'text':
                exists.update({f'{kind}_requirement': int(value)})
                msg = f'Set the `{kind.lower()} requirement` for `{group}` to: `{int(value):,}`'
            else:
                exists.update({f'{kind}_requirement': value})
                msg = f'Set the `{kind.lower()} requirement` for `{group}` to: `{value}`'
            result = await self.helpers.sql_update_record('titanlord', exists)
            asyncio.ensure_future(ctx.send(
                msg
            ))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))

    @tt_set.command(name='pings', aliases=['intervals'])
    @has_any_role('roles.grandmaster', 'tt.master')
    async def setinterval(self, ctx, *pings, group="-default"):
        pings, group = await self.munge_group(pings, group)

        if not group:
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return
        pings = pings.replace(',','')
        if not all([x.isnumeric() for x in pings.split()]):
            asyncio.ensure_future(ctx.send('You must supply space-sparated whole numbers. e.g. `15 5 1`'))
            return
        pings = [int(p) for p in pings.split()]

        exists = await self.get_tl_from_db(ctx, group)
        if exists:
            exists.update({'ping_at': pings})
            result = await self.helpers.sql_update_record('titanlord', exists)
            pings = '`, `'.join(map(str, pings))
            asyncio.ensure_future(ctx.send(f'Ping intervals for `{group}` set to: `{pings}`'))
        else:
            asyncio.ensure_future(ctx.send(f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'))


    @tt_set.command(name='rank', no_pm=True)
    @has_any_role('roles.grandmaster', 'tt.master')
    async def _setrank(self, ctx, rank, role):
        ranks = 'master knight captain recruit guest vip alumni applicant timer vip probation mercenary'.split()
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
                await self.helpers.sql_update_record('server', g)
                asyncio.ensure_future(self.helpers.try_mention(ctx, f'{rank} role', result))

    @commands.command(name='loas', aliases=['absences'])
    @has_any_role('roles.grandmaster', 'tt.master')
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

    @commands.command(name='loa', aliases=['absent'])
    @has_any_role('tt.master', 'tt.captain', 'tt.knight', 'tt.recruit')
    async def _loa(self, ctx, timeframe, group="-default"):
        group = await self.is_valid_groupname(group, ctx)
        if not group:
            return
        exists = await self.get_tl_from_db(ctx, group)
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

    @commands.command(name='relics', aliases=['prestige', 'prestigerelics'])
    async def _relics(self, ctx, stage='0', bos='0', sets='0', craft='0'):
        a = ctx.author
        user = await self.helpers.get_record('user', a.id)
        args = {'ms': stage, 'bos': bos, 'sets': sets, 'cp': craft}
        for key, value in args.items():
            if value == '0':
                args[key] = user['tt'].get(key) or 0
            elif value.isnumeric():
                args[key] = int(value)
            else:
                try:
                    args[key] = Decimal(value)
                except:
                    asyncio.ensure_future(ctx.send('Only sci notation atm'))
                    return
        if args['ms'] > 42000:
            asyncio.ensure_future(ctx.send('The MS cap atm is 42k. Silly!'))
            return
        elif args['sets'] > 10:
            asyncio.ensure_future(ctx.send('There are only 7 mythic sets available rn'))
            return
        elif args['cp'] > 250:
            asyncio.ensure_future(ctx.send('What are you, some kind of god?'))
            return

        base = await round_to_x(await base_relics_amount(args['ms']), 3)
        bonus = await bonus_relics_amount(
            args['ms'], args['bos'], args['sets'], args['cp']
        )

        content = (
            "**{}** base + **{}** bonus\nat stage **{}** with:\n**{}** sets,\n"
            "**{}** craft power,\n**{}** Book of Shadows\n\nTips: to get a preci"
            "se BoS value, use SequenceTT2. If you don't want to specify"
            " these flags every time, use the `.my` commands:\n"
            "`.my bos`, `.my sets`, `.my craft`, `.my ms`"
        )

        content = content.format(
            base, bonus, args['ms'], args['sets'], args['cp'],
            await self.helpers.humanize_decimal(args['bos'])
        )

        e = await self.helpers.full_embed(content, author={
            'name': 'Prestige Relics', 'image': 'https://cdn.discordapp.com/emojis/325072418701967375.png?v=1'}
        )

        asyncio.ensure_future(ctx.send(embed=e))

    # @commands.command(name='artifact', aliases=['arts','artifacts'])
    # async def _artifacts(self, ctx, name, level, level_to):
    #     # pull list of artifacts
    #     # search on name
    #     # get boost(s) at level
    #     # show embed + prestige number if specified

    @commands.group(name='tl', aliases=['boss', 'titanlord'], no_pm=True)
    @has_any_role('roles.grandmaster', 'tt.master', 'tt.captain', 'tt.knight', 'tt.recruit', 'tt.mercenary', 'tt.timer')
    async def tl(self, ctx):
        pfx = await self.bot.get_prefix(ctx.message)
        mc = ctx.message.clean_content
        passed = 0
        while not passed:
            for p in pfx:
                if mc.startswith(p):
                    mc = mc[len(p):]
                    passed = 1
        if mc.strip() in ['tl', 'boss', 'titanlord']:
            exists = await self.helpers.sql_query_db('SELECT * FROM titanlord')
            exists = [dict(r) for r in exists if r['guild'] == ctx.guild.id]
            if not exists:
                asyncio.ensure_future(ctx.send('No groups on this server. :<'))
                return
            fields = {}
            now = datetime.utcnow()
            for e in exists:
                n = e.get('clanname') or 'Clan #{}'.format(exists.index(e))
                fields[n] = '**{}**'.format(e.get('next') and str(e.get('next') - now)[0:-7] or 'Spawned!')
            embed = await self.helpers.full_embed(
                f'List of TLs for server: `{ctx.guild.name}`',
                fields=fields
            )
            asyncio.ensure_future(ctx.send(embed=embed))

    @tl.command(name='list', aliases=['timelord'])
    @has_any_role('roles.grandmaster', 'tt.master')
    async def tl_timelord(self, ctx):
        exists = await self.helpers.sql_query_db('SELECT * FROM titanlord')
        exists = [dict(r) for r in exists if r['guild'] == ctx.guild.id]
        if not exists:
            asyncio.ensure_future(ctx.send('No groups on this server. :<'))
            return
        fields = {}
        now = datetime.utcnow()
        for e in exists:
            n = e.get('clanname') or 'Clan #{}'.format(exists.index(e))
            fields[n] = '**{}** until boss'.format((e.get('next') or now) - now)
        embed = await self.helpers.full_embed(
            f'List of TLs for server: `{ctx.guild.name}`',
            fields=fields
        )
        asyncio.ensure_future(ctx.send(embed=embed))

    @tl.command(name='clear', aliases=['stop', 'halt', 'erase', 'cancel', 'abort'])
    @has_any_role('roles.grandmaster', 'tt.master', 'tt.timer')
    async def tl_clear(self, ctx, group="-default"):
        group = await self.is_valid_groupname(group, ctx)
        if not group:
            return
        exists = await self.get_tl_from_db(ctx, group)
        if not exists:
            await self.tl_error_message(exists, ctx)
            return
        exists.update({'next': None, 'message': 0, 'when_message': 0})
        await self.helpers.sql_update_record('titanlord', exists)
        asyncio.ensure_future(ctx.send(f'Successfully cleared the `{group}` boss timer!'))

    @tl.command(name='when')
    @has_any_role('roles.grandmaster', 'tt.master', 'tt.captain', 'tt.knight', 'tt.recruit', 'tt.mercenary')
    async def tl_when(self, ctx, group="-default"):
        group = await self.is_valid_groupname(group, ctx)
        if not group:
            return
        exists = await self.get_tl_from_db(ctx, group)
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

    async def is_valid_groupname(self, group, ctx):
        valid_group = group.startswith('-')
        if not valid_group:
            asyncio.ensure_future(ctx.send('Supply a group with a dash. e.g. `-FMT`'))
        group = valid_group and group[1:] or None
        return group

    async def tl_error_message(self, record, ctx):
        if not record:
            exists = await self.helpers.sql_query_db(
            'SELECT * FROM titanlord'
            )
            exists = [dict(r) for r in exists if r['guild']==ctx.guild.id]

            if not exists:
                asyncio.ensure_future(ctx.send('Could not find any groups. Do `.tt group add` to create one.'))
                return
            exists = ', '.join([f'`{r["name"]}`' for r in exists])
            asyncio.ensure_future(ctx.send(f'No default group set, or group not found. The following TL groups exist in this server: {exists}'))

    async def tl_embed_builder(self, record, ttk):
        cq_no = int(record.get('cq_number') or 1)
        icon = 'https://i.imgur.com/{}.png'.format(choice(self.tl_icons))
        c_dmg = await self.helpers.humanize_decimal(await clan_damage(cq_no)*100)
        c_adv = await advance_start(cq_no)
        c_hp = boss_hitpoints(cq_no)
        field1 = f'Advanced start - **{c_adv}%**\nDamage bonus - **{c_dmg}%**'
        field2 = f'Spawns with **{c_hp:,}** hitpoints.'
        e = await self.helpers.full_embed(
            "Killed in: {}".format(ttk),
            thumbnail=icon,
            fields={'Bonuses':field1, 'Next Boss':field2},
            author=dict(name=f'Boss #{cq_no}', image=icon)
        )
        return e

    async def get_tl_from_db(self, ctx, name):
        exists = await self.helpers.sql_query_db('SELECT * FROM titanlord')
        exists = next((dict(r) for r in exists
                       if (r['name'] or '').lower() == name.lower()
                       and r['guild'] == ctx.guild.id),
                      None)
        return exists

    @staticmethod
    async def munge_group(*multi_arg):
        multi_arg, group = multi_arg
        multi_text = ' '.join(multi_arg)
        try:
            if multi_arg[-1].startswith('-'):
                multi_text = ' '.join(multi_arg[:-1])
        except IndexError:
            pass
        group = multi_arg[-1].startswith('-') and multi_arg[-1] or group
        group = group.startswith('-') and group[1:] or None
        return multi_text, group

    # @tl.comamnd(name='dead')
    # @has_any_role('roles.grandmaster', 'tt.master', 'tt.timer')


    @tl.command(name='in')
    @has_any_role('roles.grandmaster', 'tt.master', 'tt.timer')
    async def tl_in(self, ctx, *time, group="-default"):
        delay = datetime.utcnow()
        try:
            time_text, group = await self.munge_group(time, group)
        except IndexError:
            asyncio.ensure_future(ctx.send('No time was supplied. Should be in the format `5h55m55s`'))
            return

        if not group:
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return

        exists = await self.get_tl_from_db(ctx, group)
        if not exists:
            asyncio.ensure_future(ctx.send(await self.tl_error_message(exists, ctx)))
            return
        elif not exists.get('cq_number'):
            asyncio.ensure_future(ctx.send('There is no CQ number set.'))
            return
        elif not all([exists.get(x) or False for x in ['now','timer','ping']]):
            missing=[f'`{x}`' for x in ['now','timer','ping'] if not exists.get(x)]
            asyncio.ensure_future(ctx.send('The following texts are missing: {}'.format(', '.join(missing))))
            return

        time = ''.join(time_text.split())
        if '.' in time:
            asyncio.ensure_future(ctx.send('Error: unsupported character in time **.** (period).'))
            return
        if time.strip().lower() == 'dead':
            time = '6h'

        _next, _units = await self.helpers.process_time(time.strip().lower())
        now = datetime.utcnow()
        next_spawn = now+_next

        if exists.get('next') and exists.get('next') < delay:
            spawned_at = exists.get('next')
            timer_remaining = timedelta(hours=6)-_next
            timer_delay = now - spawned_at
            time_to_kill = timer_delay-timer_remaining
            modded_ = await self.helpers.mod_timedelta(time_to_kill)
            mapped_ = await self.helpers.map_timedelta(modded_)
            cq_no = int(exists.get('cq_number') or 0)
            ttk = ', '.join([f'{x} {y}' for x, y in mapped_])

            e = await self.tl_embed_builder(exists, ttk)

            asyncio.ensure_future(self.bot.get_channel(exists['channel']).send(embed=e))
            exists.update({'cq_number': exists['cq_number']+1})
        modded_ = await self.helpers.mod_timedelta(_next)
        mapped_ = await self.helpers.map_timedelta(modded_)
        await asyncio.sleep(1)
        asyncio.ensure_future(ctx.send('Timer set for: `{}`'.format(
            '`, `'.join([f'{x} {y}' for x, y in mapped_])
        )))
        mx = await self.bot.get_channel(exists['channel']).send(self.load_txt)
        full_delay = datetime.utcnow()-delay
        exists.update({'next': next_spawn-full_delay, 'message': mx.id, 'pinged_at': 3660, 'round_number': 2})
        result = await self.helpers.sql_update_record('titanlord', exists)

    @tl.command(name='ttk')
    @has_any_role('roles.grandmaster', 'tt.master', 'tt.timer')
    async def tl_ttk(self, ctx, *time, group="-default"):
        delay = datetime.utcnow()
        time_text, group = await self.munge_group(time, group)
        if not group:
            asyncio.ensure_future(ctx.send('You should supply a group with a dash. e.g. `-AC`'))
            return

        exists = await self.get_tl_from_db(ctx, group)
        msg = await self.tl_error_message(exists, ctx)
        if msg:
            asyncio.ensure_future(ctx.send(msg))
            return

        time = ''.join(time_text.split())
        _ttk, _units = await self.helpers.process_time(time.strip().lower())

        try:
            if exists.get('next')+_ttk > delay:
                asyncio.ensure_future(ctx.send(
                    'What are you, \'arry? Some kind of wizzerd? Time travel is not supported. Wait until the boss dies!'
                ))
                return
        except TypeError:
            asyncio.ensure_future(ctx.send(
                'You cannot set by TTK until a previous boss has spawned.'
            ))

        modded_ = await self.helpers.mod_timedelta(_ttk)
        mapped_ = await self.helpers.map_timedelta(modded_)

        if not exists.get('next') or exists.get('next') > delay:
            asyncio.ensure_future(ctx.send('You cannot set boss by TTK until a previous boss has spawned.'))
            return

        ttk_str = ', '.join([f'{x} {y}' for x, y in mapped_])

        e = await self.tl_embed_builder(exists, ttk_str)
        asyncio.ensure_future(self.bot.get_channel(exists['channel']).send(embed=e))
        exists.update({'cq_number': exists['cq_number']+1})
        await asyncio.sleep(1)
        asyncio.ensure_future(ctx.send('Timer set for TTK: `{}`'.format(
            '`, `'.join([f'{x} {y}' for x, y in mapped_])
        )))
        mx = await self.bot.get_channel(exists['channel']).send(self.load_txt)
        full_delay = datetime.utcnow()-delay
        next_at = exists.get('next')+timedelta(hours=6, seconds=1.5)+_ttk-full_delay
        exists.update({'next': next_at, 'message': mx.id, 'pinged_at': 3660, 'round_number': 2})
        result = await self.helpers.sql_update_record('titanlord', exists)

    async def map_hits_to_damage(self, ms, taps, hits):
        return sum(b*ms*taps for b in [1,1.1,1.25,1.5,1.75,2,2.5,3][0:hits])

    async def map_hits_to_diamonds(self, hits):
        return sum(d*5 for d in [0,1,5,10,15,20,25,50][0:hits])

    @tt.command(name='report')
    @has_any_role('roles.grandmaster', 'tt.master')
    async def _report(self, ctx, start, end, group="-default"):
        group = await self.is_valid_groupname(group, ctx)
        if not group:
            return

        exists = await self.get_tl_from_db(ctx, group)
        msg = None
        if not exists:
            msg = f'A TL group with name `{group}` does not exist. Please create one first using `.tt group add`'
        elif not exists.get('paste_channel'):
            msg = 'You need to set up a paste channel first (the channel you paste your CQ exports in)! `.tt set channel paste`'
        elif not exists.get('report_channel'):
            msg = 'You need to set the report output channel first. `.tt set channel report`'
        if msg:
            asyncio.ensure_future(ctx.send(msg))
            return
        start, end = int(start), int(end)
        total = end+1-start
        c = exists['paste_channel']
        c = ctx.guild.get_channel(c)
        cq_no = int(exists['cq_number'] or 0)
        messages = await c.history(limit=total+(cq_no-end)).flatten()
        result = [m for m in messages]
        cqs = {}
        for r in result:
            cq_header, cq_data = (x for x in r.content.replace('```\n','```').replace('\n```','```').split('```') if x.strip())
            cq_number = int(re.match(r'[^\d]+(\d+)', cq_header).group(1))
            try:
                hours, mins, secs = re.match(r'[\d:]+$', cq_header).group(1).split(':')
            except:
                hours, mins, secs = 0,0,0
            finally:
                ttk = (int(hours), int(mins), int(secs))
            if start <= cq_number <= end+1:
                cq_rows = [{**dict(row), **{'ttk': ttk}} for row in DictReader(cq_data.splitlines(), delimiter=",", quotechar='"')]
                cqs[cq_number] = cq_rows

        s = await self.helpers.get_record('server', ctx.guild.id)
        roles = [
            s['roles'].get('grandmaster', 0)
        ] + [
            s['tt'].get(k, 0) for k in ['probation', 'master', 'captain', 'knight', 'recruit']
        ]

        missed = total - len(cqs)
        hitter = defaultdict(lambda: dict(id='', name='', hit=0, dmg=0, atd=0, rank='-'))
        min_hits = int(exists.get('hpcq_requirement') or 1)
        min_taps = int(exists.get('tpcq_requirement') or 100)
        top10 = int(exists.get('top10_min') or 4000)
        ttkfree = tuple(map(int, (exists.get('ttkfree') or '0:1:30').split(':')))
        ms = int(exists.get('ms_requirement') or 4000)
        min_helper_dmg = await self.map_hits_to_damage(top10, 90, min_hits)
        players = await self.helpers.sql_query_db('SELECT * FROM "user"')
        players = [p for p in players if ctx.guild.get_member(p['id'])]
        hit_tuples = [[x for x in v] for k, v in cqs.items()]
        for hit in list(chain.from_iterable(hit_tuples)):
            rank, name, id, damage, httk = hit.values()
            if not hitter[id]:
                hitter[id]['id'] = id
                hitter[id]['hit'] = 0
                hitter[id]['rank'] = '-'
            ms, d_id = 4000, 0
            player = next((dict(p) for p in players if p['tt'].get('code')==id), None)
            if player:
                ms = int(player['tt'].get('ms', 0) or ms)
                d_id = int(player['id'] or d_id)
                dgg = ctx.guild.get_member(d_id)
                if dgg and hitter[id]['rank']=='-':
                    rl = next((
                        ['G', 'P', 'M', 'C', 'K', 'R'][i]
                        for i, r
                        in enumerate(roles)
                        if r in [dggr.id for dggr in dgg.roles]), '-')
                    # print(rl)
                    hitter[id]['rank']=rl
            min_tap_dmg = await self.map_hits_to_damage(ms, min_taps, min_hits)
            if int(damage) >= min_tap_dmg+min_helper_dmg+min_helper_dmg and httk < ttkfree:
                hitter[id]['dmg'] += int(damage)
                hitter[id]['hit'] = hitter[id]['hit'] + 1
            elif int(damage)*0.6 >= (min_tap_dmg+min_helper_dmg+min_helper_dmg)*.5 and httk > ttkfree:
                hitter[id]['dmg'] += int(damage)
                hitter[id]['hit'] = hitter[id]['hit'] + 1
            if not hitter[id]['name']:
                hitter[id].update({
                    'name': d_id and f'<@!{d_id}>' or name
                })
        final = []
        for id, data in hitter.items():
            hitter[id]['atd'] = round((hitter[id]['hit']/total)*100)
            final.append(hitter[id])

        final = sorted(final, key=lambda x: x['atd'], reverse=True)
        colours = [0x146B3A, 0xF8B229, 0xEA4630, 0xBB2528]
        report_to = ctx.guild.get_channel(exists['report_channel'])
        if report_to:
            started_at = 0
            for chunk in self.helpers.chunker(final, 21):
                result = []
                for i, r in enumerate(chunk):
                    name = '`{} #{:02}`: `{:02}` (`{:<7}`)'.format(
                        r['rank'], started_at*21+i+1, floor((r["hit"]/total)*100), self.helpers.human_format(r["dmg"])
                    )
                    result.append(f'{name} - {r["name"]}')
                e = await self.helpers.build_embed(
                    'Attendance Report Part #{}:\n\n{}'.format(
                        started_at+1, "\n".join(result)
                    ), colours[started_at]
                )
                asyncio.ensure_future(report_to.send(embed=e))
                started_at += 1


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
