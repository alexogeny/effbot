import discord
import random
import time
from discord.ext import commands
from random import choice

class Reporting():
    """docstring for Reporting"""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')

    @commands.command(name='bug', pass_context=True, no_pm=True)
    async def _bot(self, ctx):
        pfx = await self.bot.get_prefix(ctx.message)
        print(pfx)
        # e = await self.helpers.build_embed(m.content, a.color)
        # e.set_author(name=f'{a.name}#{a.discriminator}', icon_url=a.avatar_url_as(format='jpeg'))
        # e.add_field(name="In", value=f'<#{c.id}>')
        # e.add_field(name="Author", value=f'<@{a.id}>')
        # await self.bot.get_channel().send(embed=embed)
        await ctx.send('placeholder')

def setup(bot):
    cog = Reporting(bot)
    bot.add_cog(cog)
