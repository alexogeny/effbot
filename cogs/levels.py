import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice
from datetime import datetime

class LevelsCog():
    """docstring for LevelsCog"""
    def __init__(self, bot):
        
        self.bot = bot
        #self.helpers = self.bot.cogs['Helpers']

    @commands.group(name="leaderboard", aliases=['lb'], invoke_without_command=True)
    async def _leaderboard(self, ctx):
        print('triggered lb')
        top10 = sorted(self.bot._users, key=lambda u: u['config'].xp)[::-1][0:10]
        print(top10)
        top10n = [ctx.guild.get_member(n['id']) for n in top10]
        print(top10n)

        top10 = '\n'.join([f'{i+1}. {top10n[i].name}#{top10n[i].discriminator}: **{u["config"].xp}xp**'
                           for i,u in enumerate(top10)])
        e = await self.bot.cogs['Helpers'].build_embed(top10, 0xffffff)
        e.set_author(name='Global all-time leaderboard')
        await ctx.send(embed=e)

    async def add_xp(self, message):
        m = message
        a = m.author
        if hasattr(m, 'guild') and len(message.content) >= 10 and not a.bot:
            u = await self.bot.cogs['Helpers'].get_record('user', m.author.id)
            c = u['config']
            now = datetime.utcnow().timestamp()
            if not c.last_xp or now - c.last_xp >= 10:
                c.last_xp = now
                c.xp += 1

def setup(bot):
    cog = LevelsCog(bot)
    bot.add_listener(cog.add_xp, "on_message")
    bot.add_cog(cog)
# def setup(bot):
#     cog = LevelsCog(bot)
#     bot.add_listener(cog.curate_channels, "on_message")
#     bot.add_listener(cog.quote_react, "on_reaction_add")
#     bot.add_cog(cog)
# await self.bot.cogs['Helpers'].get_obj(
#                     ctx.guild, 'channel', 'name', value
#                 )