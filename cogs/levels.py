import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice
from datetime import datetime
import re

class LevelsCog():
    """docstring for LevelsCog"""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        self.xp_unit = 11
        self.is_command = re.compile(r'^[A-z]{0,1}\W{1,2}\w+')

    @commands.group(name="leaderboard", aliases=['lb'], no_pm=True,
                    invoke_without_command=True)
    async def _leaderboard(self, ctx, location: str='all'):
        if location=='all':
            location = 'Global'
            top10 = sorted(self.bot._users,
                           key=lambda u: u['config'].xp, reverse=True)
            myrank = [top10.index(x) for x in top10 if x['id']==ctx.author.id][0]
            myxp = [u['config'].xp for u in top10 if u['id']==ctx.author.id][0]
            ids = [(u['id'], u['config'].xp) for u in top10[0:10]]

        elif location == 'here':
            
            m = ctx.message
            g = await self.helpers.get_record('server', m.guild.id)
            location = m.guild.name
            top10 = sorted(g['config'].xp, key=lambda u: u['xp'], reverse=True)
            myrank = [top10.index(x) for x in top10 if x['id']==ctx.author.id][0]
            myxp = [u['xp'] for u in top10 if u['id']==ctx.author.id][0]
            ids = [(u['id'], u['xp']) for u in top10[0:10]]
        all_users = {m.id: m for m
                     in self.bot.get_all_members()
                     if m.id in [i[0] for i in ids]}
        
        top10n = all_users
        top10 = '\n'.join([f'{i+1}. {top10n[u[0]].name}#{top10n[u[0]].discriminator}: **{ids[i][1]}xp**'
                           for i,u in enumerate(ids)])
        e = await self.helpers.build_embed(top10, 0xffffff)
        if location == 'Global':
            e.set_author(name=f'Leaderboard: {location}',
                         icon_url='https://i.imgur.com/q2I08K7.png')

        else:
            e.set_author(name=f'Leaderboard: {location}',
                         icon_url=m.guild.icon_url_as(format='jpeg'))
        e.add_field(name="Me", value=f"{myrank+1}.  **{myxp}xp**.")
        await ctx.send(embed=e)

    async def add_xp(self, message):
        m = message
        a = m.author
        if hasattr(m, 'guild') and len(message.content) >= 10 and not a.bot:
            if not self.is_command.match(message.content):
                u = await self.helpers.get_record('user', m.author.id)
                c = u['config']
                now = datetime.utcnow().timestamp()
                if not c.last_xp or now - c.last_xp >= 25:
                    xp = self.xp_unit + rndchoice([1,2,2,2,2,2,3,3,4,3,2,2,4,15])
                    g = await self.helpers.get_record('server', m.guild.id)
                    g = g['config']
                    c.last_xp = now
                    c.xp += xp
                    if not hasattr(g, 'xp'):
                        setattr(g, 'xp', [])
                    if not [x for x in g.xp if x['id']==m.author.id]:
                        g.xp.append({'id': m.author.id, 'xp': 0})
                    u = [x for x in g.xp if x['id']==m.author.id][0]
                    # print(u)
                    u['xp'] = u['xp'] + xp



def setup(bot):
    cog = LevelsCog(bot)
    bot.add_listener(cog.add_xp, "on_message")
    bot.add_cog(cog)
# def setup(bot):
#     cog = LevelsCog(bot)
#     bot.add_listener(cog.curate_channels, "on_message")
#     bot.add_listener(cog.quote_react, "on_reaction_add")
#     bot.add_cog(cog)
# await self.helpers.get_obj(
#                     ctx.guild, 'channel', 'name', value
#                 )