import discord
from datetime import datetime
from discord.ext import commands
from string import ascii_lowercase
import os
import asyncio
import re
import time
SCIFI = re.compile(r'^([^a-z]+)([A-Za-z]+)$')
LIFI = re.compile(r'^([0-9\.]+)[^0-9]+([0-9,]+)$')

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
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        if g['config'].tt_gm in [a.id for a in msg.author.roles]:
            return True
        elif g['config'].tt_master in [a.id for a in msg.author.roles]:
            return True
        elif not getattr(g['config'], 'tt_gm', None):
            await ctx.send('Ask your server admin to set the GM role')
            return False
        else:
            await ctx.send('Oof, you need to be a GM to do this.')
            return False

class TapTitans():
    """docstring for TapTitans"""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        # connect to reminders table
        # load reminders
        self.units = {"minute": 60, "hour": 3600}
        self.dead = 3600*6

    @commands.group(pass_context=True, invoke_without_command=True, name="tt")
    async def tt(self, ctx):
        await ctx.send('TT2 commands')

    @is_gm_or_admin()
    @tt.command(name='set')
    async def _masterrole(self, ctx, rank, role):
        if rank not in ['master', 'knight', 'captain', 'recruit', 'guest', 'vip', 'applicant', 'alumni', 'timer']:
            await ctx.send('The rank a valid name of an in-game role')
            return
        guild = ctx.message.guild
        if role.isnumeric():
            role = next((r.name for r in guild.roles if r.id == int(role)), None)
        if role:
            g = await ctx.bot.cogs['Helpers'].get_record('server', ctx.message.guild.id)
            result = await self.helpers.get_obj(ctx.message.guild, 'role', 'name', role)
            if result:
                print('yay')
                setattr(g['config'], f'tt_{rank}', result)
                result = next((r for r in guild.roles if r.id == int(result)), None)
                was_true = False
                if result.mentionable == True:
                    print('ayyy')
                    was_true = True
                    await result.edit(mentionable=False)
                await ctx.send(f'Set the {rank} role to {result.mention}!')
                if was_true:
                    print('ayyyayaya')
                    await result.edit(mentionable=True)

    @commands.command(name='claim')
    async def _claim(self, ctx, key, value):
        print(key)
        if not key in ['sc','supportcode','cc','clancode']:
            return
        a = ctx.message.author
        g = ctx.message.guild
        
        if key.startswith('s') and not a.bot:
            if not isinstance(ctx.message.channel, discord.abc.PrivateChannel):
                await ctx.message.delete()
            if a:
                g = await self.bot.cogs['Helpers'].get_record('user', a.id)
                if not g['config'].tt_code:
                    g['config'].tt_code = value.strip()
                    await ctx.send(f'Set the support code for the user {a.name}#'
                                   f'{a.discriminator}.')
                else:
                    await ctx.send('You have already claimed a code. Please use'
                                   '`verify` if you would like to change it.')

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
    # @tl.command(pass_context=True, alias=["in"])
    # async def at(self, ctx, * clan: str=0):
    #     await ctx.send('placeholder')

    # @tt.command(pass_context=True)
    # async def set(self, ctx, setting: str=None, value: str=None):

    #     guild_id = ctx.message.guild.id
    #     key = setting.lower().strip()

    #     g = [x for x in self.bot._servers if x['id']==guild_id][0]
    #     print(g)
    #     if key == 'cq' and not value.isdigit():
    #         await ctx.send('You have to choose a number for `cq` setting')
    #         return
    #     elif key == 'code' and not len(value)<10:
    #         await ctx.send('Clan code cannot be longer than 10 characters')
    #         return
    #     elif key in 'ms prestiges tcq' and not value.isdigit() and not len(value) < 10:
    #         await ctx.send(f'{key} requirement should be a whole number e.g. 1234')
    #         return
    #     elif key in 'timer,when':
    #         channel = None
    #         if value[2:-1].isdigit() and value.startswith('<#'):
    #             value = value[2:-1]
    #         if value.isdigit():
    #             channel = self.bot.get_channel(int(value))
    #         if not channel:
    #             channel = await self.bot.cogs['Helpers'].get_obj(
    #                 ctx.guild, 'channel', 'name', value
    #             )
    #         if not channel:
    #             await ctx.send('Sorry, you supplied a channel that does not exist')
    #             return
    #         value = channel
    #     elif key in 'gm,master,captain,knight,recruit,alumni,guest,applicant':
    #         if not value.isdigit() and value.startswith('<@&'):
    #             value = value[3:-1]
    #         if not value.isdigit():
    #             roles = [r for r in ctx.guild.roles if value.lower() in r.name.lower()]
    #             if len(roles) > 0:
    #                 value = str(roles[0].id)
    #         if not value.isdigit():
    #             await ctx.send('You need to mention a valid role or ID')
    #             return
    #         role = discord.utils.get(ctx.guild.roles, id=int(value))
    #         if not role:
    #             await ctx.send('Sorry, you supplied a role that does not exist')
    #             return

    #     key = f'tt_{key}'
    #     old_value = getattr(g['config'], key)
    #     if not value == old_value:
    #         setattr(g['config'], key, value)
    #         g['changed']=True
    #         # output = dict(update=datetime.utcnow())
    #         # output[key] = value
    #         # with ctx.bot.database.connection_context():
    #         #     qry=ctx.bot.models.ServerTT2.update(**output).where(
    #         #         ctx.bot.models.ServerTT2.id == guild_id
    #         #     )
    #         #     qry.execute()
    #     # await ctx.send(g['config'].as_pretty())
    #     print(g)
    #     embed = await self.bot.cogs['Helpers'].build_embed(ctx.message.guild.name,
    #                                         0xffffff)
    #     embed.add_field(name="Setting", value=key, inline=False)
    #     embed.add_field(name="Old", value=str(old_value))
    #     embed.add_field(name="New", value=str(value))
    #     await ctx.send(embed=embed)
        
    #set export {cq} {data}
    #set ttk {cq} {data}
    #set reminders
    #

def setup(bot):
    cog = TapTitans(bot)
    # loop = asyncio.get_event_loop()
    # loop.create_task(cog.check_tl_timers())
    bot.add_cog(cog)
