import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice

class CurationCog():
    """docstring for CurationCog"""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.cogs['Helpers']

    @commands.group(pass_context=True, name="curation")
    async def curation(self, ctx):
        pass

    async def curate_channels(self, message):
        if hasattr(message, 'guild'):
            m = message
            c, guild, a = m.channel, m.guild, m.author
            g = await self.helpers.get_record('server', guild.id)
            if g and c.id in g['config'].chan_curated:
                print(m.embeds)
                print(m.attachments)
                if not m.embeds and not m.attachments:
                    await m.delete()
                    await self.bot.get_user(a.id).send(
                        (f'Hey {a.name}, <#{c.id}> is a curated channel,'
                          ' meaning you can only send links or pictures.')
                    )

def setup(bot):
    cog = CurationCog(bot)
    bot.add_listener(cog.curate_channels, "on_message")
    bot.add_cog(cog)
