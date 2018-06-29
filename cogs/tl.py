import discord
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

    @commands.group(pass_context=True, invoke_without_command=True)
    async def tl(self, ctx):
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

    @tl.command(pass_context=True)
    async def now(self, ctx, *, clan: str=0):
        await ctx.send('placeholder')

    # @tl.command(pass_context=True, alias=["in"])
    # async def at(self, ctx, * clan: str=0):
    #     await ctx.send('placeholder')

    # @tl.command(pass_context=True)
    # async def set(self, ctx, *, setting: str=None, value: str=None):
    #     if setting not in ''
    #     await ctx.send('placeholder')

    #set export {cq} {data}
    #set ttk {cq} {data}
    #set reminders
    #

def setup(bot):
    cog = TitanLord(bot)
    # loop = asyncio.get_event_loop()
    # loop.create_task(cog.check_tl_timers())
    bot.add_cog(cog)
