import discord
from datetime import datetime
from discord.ext import commands
import os
import asyncio
import time

class TitanLord():
    """docstring for TitanLord"""
    def __init__(self, bot):
        
        self.bot = bot
        
        # connect to reminders table
        # load reminders
        self.units = {"minute": 60, "hour": 3600}
        self.dead = 3600*6

    @commands.group(pass_context=True, invoke_without_command=True, alias=["tl"])
    async def tt(self, ctx):
        await ctx.send('TT2 TL timers')

    # @tl.command(pass_context=True, alias=["in"])
    # async def at(self, ctx, *, time: str=None, clan: str="0"):
    #     try:
    #         timer = self.tl_timers.get(ctx.message.guild)
    #     except:
    #         await ctx.send('Set me up first, ffs. `.help tl`')
    #     else:
    #         if clan.isdigit():
    #             clan = timer.get_clan(int(clan))
    #         else:
    #             clan = timer.get_clan(timer.find_clan(clan))
    #         if clan.spawn-time.time() > 21000:
    #             # display ttk and increment cq value
    #             # build ttk embed here
    #             # clan.increment_cq()
    #         # set new spawm time and append old times to data store
    #         clan.old.append(dict(spawn=clan.spawn, dead=ctx.message.timestamp))
    #         clan.spawn = time.from_string(time)
    #     finally:
    #         return

    @tt.command(pass_context=True)
    async def now(self, ctx, *, clan: str=0):

        # (Titanlord
        #  .select()
        #  .where(Titanlord.id = ctx.guild.id)
        #  .order_by(Titanlord.create.desc())
        #  .get())
        await ctx.send('placeholder')

    # @tl.command(pass_context=True, alias=["in"])
    # async def at(self, ctx, * clan: str=0):
    #     await ctx.send('placeholder')

    @tt.command(pass_context=True)
    async def set(self, ctx, setting: str=None, value: str=None):

        guild_id = ctx.message.guild.id
        key = setting.lower().strip()
        with ctx.bot.database.connection_context():
            if not ctx.bot.models.ServerTT2.get_or_none(ctx.bot.models.ServerTT2.id==guild_id):

                res = ctx.bot.models.ServerTT2.create(
                    id=guild_id,
                    code="0",
                    name=ctx.message.guild.name,
                    inxtext="Cq {} in {} minutes, @everyone! Get ready!",
                    nowtext="Cq {} is UP! Kill it now!! @everyone"
                )

                await ctx.send('New guild added. Congrats!')
            old_value = getattr(ctx.bot.models.ServerTT2.get_by_id(guild_id), key)

            if not old_value:
                old_value = "n/a"        
        
        if key == 'cq' and not value.isdigit():
            await ctx.send('You have to choose a number for `cq` setting')
            return
        elif key == 'code' and not len(value)<10:
            await ctx.send('Clan code cannot be longer than 10 characters')
            return
        elif key in 'ms prestiges tcq' and not value.isdigit() and not len(value) < 10:
            await ctx.send(f'{key} requirement should be a whole number e.g. 1234')
            return
        elif key in 'timerchannel,whenchannel,hofchannel,loachannel':
            if value[2:-1].isdigit() and value.startswith('<#'):
                value = value[2:-1]
            if not value.isdigit():
                await ctx.send('You need to mention a valid channel or ID')
                return
            channel = self.bot.get_channel(int(value))
            if not channel:
                await ctx.send('Sorry, you supplied a channel that does not exist')
                return
        elif key in 'gm,master,captain,knight,recruit,alumni,guest,applicant':
            if not value.isdigit() and value.startswith('<@&'):
                value = value[3:-1]
            if not value.isdigit():
                roles = [r for r in ctx.guild.roles if value.lower() in r.name.lower()]
                if len(roles) > 0:
                    value = str(roles[0].id)
            if not value.isdigit():
                await ctx.send('You need to mention a valid role or ID')
                return
            role = discord.utils.get(ctx.guild.roles, id=int(value))
            if not role:
                await ctx.send('Sorry, you supplied a role that does not exist')
                return

        if not value == old_value:
            output = dict(update=datetime.utcnow())
            output[key] = value
            with ctx.bot.database.connection_context():
                qry=ctx.bot.models.ServerTT2.update(**output).where(
                    ctx.bot.models.ServerTT2.id == guild_id
                )
                qry.execute()
        
        embed = await self.bot.cogs['Helpers'].build_embed(ctx.message.guild.name,
                                            0xffffff)
        embed.add_field(name="Setting", value=key, inline=False)
        embed.add_field(name="Old", value=str(old_value))
        embed.add_field(name="New", value=str(value))
        await ctx.send(embed=embed)
        
    #set export {cq} {data}
    #set ttk {cq} {data}
    #set reminders
    #

def setup(bot):
    cog = TitanLord(bot)
    # loop = asyncio.get_event_loop()
    # loop.create_task(cog.check_tl_timers())
    bot.add_cog(cog)
