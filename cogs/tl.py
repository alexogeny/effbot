import discord
from datetime import datetime, timedelta
from discord.ext import commands
from string import ascii_lowercase
import os
import asyncio
import re
import time
SCIFI = re.compile(r'^([^a-z]+)([A-Za-z]+)$')
LIFI = re.compile(r'^([0-9\.]+)[^0-9]+([0-9,]+)$')
TIME_SUCKER = re.compile(r'([0-9]+)([^0-9]+)?')
LETTERS = re.compile(r'^[hms]')
MAP = dict(w='weeks', d='days', h='hours', m='minutes', s='seconds')

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
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        #print([a.id for a in msg.author.roles])
        if g['config'].role_admin in [a.id for a in msg.author.roles]:
            return True
        elif msg.author.id == msg.guild.owner_id:
            return True
        elif g['config'].tt_gm in [a.id for a in msg.author.roles]:
            return True
        elif not getattr(g['config'], 'tt_gm', None):
            await ctx.send('Ask your server admin to set the GM role')
            return False
        else:
            await ctx.send('Oof, you need to be a GM to do this.')
            return False
    return commands.check(_is_gm_or_admin)

def is_gm_or_master():
    async def _is_gm_or_master(ctx):
        m = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', m.guild.id)
        if g['config'].tt_gm in [a.id for a in m.author.roles]:
            return True
        elif g['config'].tt_master in [a.id for a in m.author.roles]:
            return True
        elif not getattr(g['config'], 'tt_gm', None):
            await ctx.send('Ask your server admin to set the GM role')
            return False
        else:
            await ctx.send('Oof, you need to be a GM to do this.')
            return False
    return commands.check(_is_gm_or_master)

def tl_checks():
    async def _tl_checks(ctx):
        m = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', m.guild.id)
        if not getattr(g['config'], 'tt_inxtext', None):
            await ctx.send('The Gm or a master needs to set up ping `inx` text.\n'
                           '`e.tt setping inx blah blah blah yo @everyone the \n'
                           'the TL is soon ya in {time} so be ready`')
            return False
        elif not getattr(g['config'], 'tt_nowtext', None):
            await ctx.send('The Gm or master needs to set ping `now` text.\n'
                           '`e.tt setping now BOSS UP @EVERYONE GO GETTEM`')
            return False
        elif not getattr(g['config'], 'chan_tl', None):
            await ctx.send('The Gm or a master needs to set up a TL channel.\n'
                           '`e.tt setchannel tl #abc123`')
            return False
        elif not getattr(g['config'], 'tt_cq', None):
            await ctx.send('The Gm or a master should set the CQ number.\n'
                           'This is the cq of the _next_ TL, not the one that\n'
                           'was just killed.\n'
                           '`e.tt setcq 1589`')
            return False
        return True
    return commands.check(_tl_checks)

class TapTitans():
    """docstring for TapTitans"""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        # connect to reminders table
        # load reminders
        self.units = {"minute": 60, "hour": 3600}
        self.dead = 3600*6
        self.last_check = int(time.time())

    async def timer_check(self):
        while self is self.bot.get_cog('TapTitans'):
            if int(time.time()) - self.last_check >= 4.99:
                await self.update_timers()
            await asyncio.sleep(10)
    async def update_timers(self):
        guilds = [s for s in self.bot._servers if getattr(s['config'], 'next_boss', None)]
        await asyncio.gather(*[self.update_timer(guild) for guild in guilds])
    async def update_timer(self, guild):
        #print(guild['config'].next_boss)
        if isinstance(guild['config'].next_boss, float):
            g = self.bot.get_guild(guild['id'])
            if g is not None:
                c = g.get_channel(guild['config'].chan_tl)
            if c is not None:
                _next = datetime.utcfromtimestamp(guild['config'].next_boss)
                _next = _next - datetime.utcnow()
                print(str(_next))
                m = await c.get_message(guild['config'].boss_msg)
                await m.edit(
                    content=f'Titanlord arrives in **{_next}**'
                )

    @commands.group(pass_context=True, invoke_without_command=True, name="tt")
    async def tt(self, ctx):
        await ctx.send('TT2 commands')

    @is_gm_or_master()
    @tt.command(name='setchannel')
    async def _setchannel(self, ctx, kind, channel):
        """
        Allows you to set up a clan related channel for the bot.
        - the bot must have permission to send+edit+delete+pin messages
        Examples:
        ```
        e.tt setchannel tl #boss-timers
        e.tt setchannel when #clan-lounge
        e.tt setchannel paste #cq-exports
        e.tt setchannel report #weekly-update
        ```
        """
        if kind not in ['tl', 'when', 'paste', 'report']:
            await ctx.send('Channel kind must be one of: tl, when, paste, report')
        guild = ctx.message.guild
        if channel.startswith('#'):
            channel = channel[1:]
        if channel.isnumeric():
            channel = next((c.name for c in guild.channels if c.id == int(channel)), None)
        if channel:
            g = await self.helpers.get_record('server', ctx.message.guild.id)
            result = await self.helpers.choose_channel(ctx, ctx.message.guild, channel)
            if result:
                setattr(g['config'], f'chan_{kind}', result.id)
                await ctx.send(f'Set the {kind} channel to {result.mention}!')

    @is_gm_or_admin()
    @tt.command(name='setrank')
    async def _setrank(self, ctx, rank, role):
        """
        Sets a discord role to an in-game clan rank.
        - you can specify a role by name or ID
        - emojis will be automatically converted to unicode
        Example:
        ```
        e.tt setrank timer :bell:
        ```
        """
        if rank not in ['master', 'knight', 'captain', 'recruit', 'guest', 'vip', 'applicant', 'alumni', 'timer']:
            await ctx.send('The rank a valid name of an in-game role')
            return
        guild = ctx.message.guild
        if role.isnumeric():
            role = next((r.name for r in guild.roles if r.id == int(role)), None)
        if role:
            g = await self.helpers.get_record('server', ctx.message.guild.id)
            result =await self.helpers.choose_role(ctx, ctx.message.guild, role)
            if result:
                setattr(g['config'], f'tt_{rank}', result.id)
                # result = next((r for r in guild.roles if r.id == int(result)), None)
                was_true = False
                try:
                    if result.mentionable == True:
                        was_true = True
                        await result.edit(mentionable=False)
                    await ctx.send(f'Set the {rank} role to {result.mention}!')
                    if was_true:
                        await result.edit(mentionable=True)
                except discord.Forbidden:
                    await ctx.send(f'Set the `{rank}` role to `{result.name}`!')

    @is_gm_or_master()
    @tl_checks()
    @commands.group(name='tl', aliases=['boss', 'titanlord'], invoke_without_command=True)
    async def tl(self, ctx, *time):
        """
        Sets a timer running until the next titanlord spawn.
        - accepts most timestam formats
        - requires
        Examples:
        ```
        e.tl dead
        e.tl 5h30m
        e.tl 3:22:20
        ```
        """
        if time[0] == 'in':
            time = ' '.join(time[1:]).strip()
        else:
            time = time[0]
        if time.lower() == 'dead':
            time = '6h'
        if time not in ['now', 'dead']:
            guild = ctx.message.guild
            _next, _units = await process_time(time)
            g = await self.helpers.get_record('server', ctx.message.guild.id)
            setattr(g['config'], 'next_boss', datetime.utcnow().timestamp()+_next.total_seconds())
            boss_msg = await guild.get_channel(g['config'].chan_tl).send(
                f'Titanlord arrives in **{_next}**'
            )
            print(g['config'].next_boss)
            setattr(g['config'], 'boss_msg', boss_msg.id)
            await ctx.send(':ideograph_advantage: Set a timer running for **{}**'.format(
                ', '.join(f'{v} {k}' for k, v in _units.items())
            ))

    @is_gm_or_master()
    @tt.command(name='setcq')
    async def setcq(self, ctx, cq):
        """
        Allows you to set the clan's current quest level _of the next boss_.
        Requires: GM or Master ranks
        Example:
        ```
        .tt setcq 1580
        ```
        """
        if not cq.isnumeric():
            await ctx.send('You must supply a valid numerical value for the cq number.')
            return
        g = await self.helpers.get_record('server', ctx.message.guild.id)
        setattr(g['config'], 'tt_cq', int(cq))
        await ctx.send(f':ideograph_advantage: Updated the CQ number to `{cq}`!')
            

    @is_gm_or_master()
    @tl_checks()
    @tl.command(name='clear', aliases=['wipe'])
    async def _clear(self, ctx):
        g = await self.helpers.get_record('server', ctx.message.guild.id)
        setattr(g['config'], 'next_boss', '')
        setattr(g['config'], 'boss_msg', '')
        await ctx.send(':ideograph_advantage: Cleared the boss timer!')

    @commands.command(name='claim')
    async def _claim(self, ctx, key, value):
        """
        Sets a support code tied to your discord ID.
        - does not currently support DMs
        - autodeletes when you do it
        Example:
        ```
        e.claim supportcode abc123
        ```
        """
        if not key in ['sc','supportcode','cc','clancode']:
            return
        a = ctx.message.author
        g = ctx.message.guild
        
        if key.startswith('s') and not a.bot:
            if not isinstance(ctx.message.channel, discord.abc.PrivateChannel):
                await ctx.message.delete()
            if a:
                used = next((x for x in self.bot._users
                             if x['config'].tt_code == value.strip()), None)
                print(used)
                if used:
                    await ctx.send(
                        'Sorry, somebody already used that code.\n'
                        'If it was not you, do the verify command.\n'
                        'Example: `e.verify supportcode abc123`')
                    return 
                g = await self.bot.cogs['Helpers'].get_record('user', a.id)
                if not g['config'].tt_code:
                    g['config'].tt_code = value.strip()
                    await ctx.send(f'Set the support code for the user {a.name}#'
                                   f'{a.discriminator}.')
                else:
                    await ctx.send('You have already claimed a code. Please use'
                                   ' `verify` if you would like to change it.\n'
                                   'Example: `e.verify supportcode abc123')

    @tt.command(name="my")
    async def _my(self, ctx, key: str=None, value: str=None):
        await ctx.send('placeholder')


    @tt.command(pass_context=True)
    async def now(self, ctx, *, clan: str=0):

        # (TapTitans
        #  .select()
        #  .where(TapTitans.id = ctx.guild.id)
        #  .order_by(TapTitans.create.desc())
        #  .get())
        await ctx.send('placeholder')

    @tt.command(pass_context=True, name='convert', alias=["notation"])
    async def _convert(self, ctx, kind: str='sci', val: str='1e+5000'):
        if kind.startswith('l'):
            
            number, letter = SCIFI.findall(val.strip())[0]
            map_to_alpha = [ascii_lowercase.index(x) for x in letter.lower()]
            a_to_one = [x+1 for x in map_to_alpha[:-2]]+map_to_alpha[-2:]
            dict_map = dict(enumerate(a_to_one))
            map_to_alpha = [pow(26, x) for x in  list(dict_map.keys())[::-1]]
            result = sum([x*a_to_one[i] for i, x in enumerate(map_to_alpha)])
            result = '{}e{:,}'.format(number, result*3)
        else:
            number, notation = LIFI.findall(val.strip())[0]
            notation = int(notation.replace(',',''))
            modulo = notation % 3
            exponent = notation / 3
            output = []
            while exponent > 26:
                result, remainder = divmod(exponent, 26)
                output.append(remainder)
                exponent = result
            output.append(exponent)
            multiple = pow(10, modulo)
            l = len(output)
            if l > 2:
                output = [x for x in output[:-(l-2)]]+[max(x-1, 0) for x in output[-(l-2):]]
            last_result = ''.join([ascii_lowercase[int(last)] for last in output[::-1]])
            result = '{}{}'.format(number*multiple, last_result)
        flip = {'s': 'letter', 'l': 'scientific'}
        await ctx.send(f'Conversion of {val} from {kind} to {flip[kind[0].lower()]} is **{result}**')
    
def setup(bot):
    cog = TapTitans(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(cog.timer_check())
    bot.add_cog(cog)
