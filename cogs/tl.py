import discord
import datetime
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
        await ctx.send('placeholder')

    # @tl.command(pass_context=True, alias=["in"])
    # async def at(self, ctx, * clan: str=0):
    #     await ctx.send('placeholder')

    @tt.command(pass_context=True)
    async def set(self, ctx, *, setting: str=None, value: str=None):
        if setting not in 'code name pass quest'.split():
            await ctx.send('Check out `.help tt set`')
            return
        guild_id = ctx.message.guild.id
        key = setting.lower().strip()
        with self.db.connection_context():
            if not self.models.ServerTT2.get_by_id(guild_id):
                self.models.ServerTT2.create(
                    id=guild_id,
                    clan_name=ctx.message.guild.name,
                    timer_inxtext="Cq {} in {} minutes, @everyone! Get ready!",
                    timer_nowtext="Cq {} is UP! Kill it now!! @everyone"
                )
            await ctx.send('New guild added. Congrats!')
            old_value = getattr(self.models.ServerTT2.get_by_id(guild_id), key)        
        
        if key == 'cq' and value.isdigit():
            with self.db.connection_context():
                self.models.ServerTT2
                    .update(clan_quest=cq, update=datetime.utcnow())
                    .where(self.models.ServerTT2.id == guild_id)
        
        embed = discord.Embed(description=ctx.message.guild.name)
        embed.add_field(name="Setting", value=setting, inline=False)
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
