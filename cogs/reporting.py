import discord
import random
import time
import asyncio
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
        u = await self.helpers.get_record('user', m.author.id)
        now = datetime.utcnow().timestamp()
        last_bug = u['timers'].get('last_bug', 0)
        if now - last_bug >= 3600:
            u['timers']['last_bug'] = now
            pfx = await self.bot.get_prefix(ctx.message)
            mc = m.clean_content
            passed = 0
            while not passed:
                for p in pfx:
                    if mc.startswith(p):
                        mc = mc[len(p):]
                        passed = 1
            mc = re.sub(r'^\w+','',mc)

            e = await self.helpers.build_embed(f'Bug: {mc.strip()}', 0xffffff)
            e.set_thumbnail(url=a.avatar_url_as(format='jpeg'))
            e.set_author(name=f'{a.name}#{a.discriminator} ({a.id})',
                         icon_url='https://i.imgur.com/uoAST0b.png')
            asyncio.ensure_future(self.bot.get_channel(466133068730597377).send(embed=e))
            await self.helpers.sql_update_record('user', u)
        else:
            asyncio.ensure_future(ctx.send('You must wait at least an hour between bug reports.'))
            return

        asyncio.ensure_future(ctx.send(':ideograph_advantage: Thanks, you have successfully filed your bug.'))


    @commands.command(name='suggestion', aliases=['suggest'])
    async def _suggest(self, ctx):
        m = ctx.message
        a = m.author
        if not len(m.content) >= 30:
            await ctx.send('Please be more descriptive (more than 30 characters).')
            return
        u = await self.helpers.get_record('user', m.author.id)
        now = datetime.utcnow().timestamp()
        last_suggest = u['timers'].get('last_suggest', 0)
        if now - last_suggest >= 3600:
            u['timers']['last_suggest'] = now
            pfx = await self.bot.get_prefix(ctx.message)
            mc = m.clean_content
            passed = 0
            while not passed:
                for p in pfx:
                    if mc.startswith(p):
                        mc = mc[len(p):]
                        passed = 1
            mc = re.sub(r'^\w+','',mc)

            e = await self.helpers.build_embed(f'Suggested: {mc.strip()}', 0xffffff)
            e.set_thumbnail(url=a.avatar_url_as(format='jpeg'))
            e.set_author(name=f'{a.name}#{a.discriminator} ({a.id})',
                           icon_url='https://i.imgur.com/6y7oNyd.png')
            asyncio.ensure_future(self.bot.get_channel(462474193779294218).send(embed=e))
            await self.helpers.sql_update_record('user', u)
        else:
            asyncio.ensure_future(ctx.send('You must wait at least an hour between suggestions.'))
            return
        asyncio.ensure_future(ctx.send(':ideograph_advantage: Thanks, you have successfully filed your suggestion.'))


def setup(bot):
    cog = Reporting(bot)
    bot.add_cog(cog)
