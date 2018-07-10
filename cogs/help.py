import discord
import random
import time
from discord.ext import commands
from random import choice

class HelpCog():
    """docstring for HelpCog"""
    def __init__(self, bot):
        
        self.bot = bot
    
    @commands.command(name='help', no_pm=True, aliases=['helpme'])
    async def _help(self, ctx, module: str=None, command: str=None):
        if not module and not command:
            await ctx.send(', '.join([c.lower() for c in self.bot.cogs]))

def setup(bot):
    cog = HelpCog(bot)
    bot.add_cog(cog)
