import discord
import random
import time
from discord.ext import commands
from random import choice
from datetime import datetime
import re

class Reporting():
    """Send me plenty of bug reports and suggestions."""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')

    @commands.command(name='bug', pass_context=True, no_pm=True)
    async def _bug(self, ctx):
        m = ctx.message
        a = m.author
        if not len(m.content) >= 30:
            await ctx.send('Please be more descriptive (more than 30 characters).')
            return
        if a.bot:
            return
        u = await self.helpers.get_record('user', m.author.id)
        c = u['config']
        now = datetime.utcnow().timestamp()
        if not hasattr(c, 'last_bug') or now - c.last_bug >= 3600:
            setattr(c, 'last_bug', now)
            pfx = await self.bot.get_prefix(ctx.message)
            mc = m.clean_content
            passed = 0
            while not passed:
                for p in pfx:
                    if mc.startswith(p):
                        mc = mc[len(p):]
                        passed = 1

            e = await self.helpers.build_embed('Bug Report', 0xffffff)
            e.set_thumbnail(url='https://i.imgur.com/uoAST0b.png')
            e.set_author(name=f'{a.name}#{a.discriminator}', icon_url=a.avatar_url_as(format='jpeg'))
            e.add_field(name='User', value=f'{a.mention} ({a.id})')
            e.add_field(name='Content', value=mc[len(ctx.command.name):].strip())
            await self.bot.get_channel(466133068730597377).send(embed=e)
        else:
            await ctx.send('You must wait at least an hour between bug reports.')
            return
        await ctx.send(':ideograph_advantage: Thanks, you have successfully filed your bug.')


    @commands.command(name='suggestion', pass_context=True, no_pm=True, aliases=['suggest'])
    async def _suggest(self, ctx):
        m = ctx.message
        a = m.author
        if not len(m.content) >= 30:
            await ctx.send('Please be more descriptive (more than 30 characters).')
            return
        if a.bot:
            return
        u = await self.helpers.get_record('user', m.author.id)
        c = u['config']
        now = datetime.utcnow().timestamp()
        if not hasattr(c, 'last_suggest') or now - c.last_suggest >= 3600:
            setattr(c, 'last_suggest', now)
            pfx = await self.bot.get_prefix(ctx.message)
            mc = m.clean_content
            passed = 0
            while not passed:
                for p in pfx:
                    if mc.startswith(p):
                        mc = mc[len(p):]
                        passed = 1
            mc = re.sub(r'^\w+','',mc)

            e = await self.helpers.build_embed('Suggestion', 0xffffff)
            e.set_thumbnail(url='https://i.imgur.com/6y7oNyd.png')
            e.set_author(name=f'{a.name}#{a.discriminator}', icon_url=a.avatar_url_as(format='jpeg'))
            e.add_field(name='User', value=f'{a.mention} ({a.id})')
            e.add_field(name='Content', value=mc.strip())
            await self.bot.get_channel(462474193779294218).send(embed=e)
        else:
            await ctx.send('You must wait at least an hour between suggestions.')
            return
        await ctx.send(':ideograph_advantage: Thanks, you have successfully filed your suggestion.')


def setup(bot):
    cog = Reporting(bot)
    bot.add_cog(cog)
