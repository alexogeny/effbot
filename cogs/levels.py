import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice
from datetime import datetime
import re

class LevelsCog():
    """Check your global and local rankins, as well as leaderboards."""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        self.xp_unit = 11
        self.is_command = re.compile(r'^[A-z]{0,1}[^A-z0-9\s]{1,2}[A-z0-9]+')

    async def _lb_get_global_rank(self, userid, idlist):
        rank = [idlist.index(user)
                for user in idlist
                if user.id == userid][0]
        return rank
    async def _lb_get_local_rank(self, userid, idlist):
        rank = [idlist.index(user)
                for user in idlist
                if user['id'] == userid][0]
        return rank

    @commands.command(name="leaderboard", aliases=['lb'], no_pm=True)
    async def _leaderboard(self, ctx, location: str='all'):
        if location=='all':
            location = 'Global'
            top10 = sorted(self.bot._users,
                           key=lambda u: u.xp.get('amount', 0), reverse=True)
            myrank = await self._lb_get_global_rank(ctx.author.id, top10)
            myxp = top10[myrank].xp['amount']
            ids = [(u.id, u.xp['amount']) for u in top10[0:10]]

        elif location == 'here':
            
            m = ctx.message
            g = await self.helpers.get_record('server', m.guild.id)
            location = m.guild.name
            top10 = sorted(g.users, key=lambda u: u['xp'], reverse=True)
            myrank = await self._lb_get_local_rank(ctx.author.id, top10)
            myxp = top10[myrank]['xp']
            ids = [(u['id'], u['xp']) for u in top10[0:10]]
        all_users = {m.id: m for m
                     in self.bot.get_all_members()
                     if m.id in [i[0] for i in ids]}
        
        top10n = all_users
        top10 = '\n'.join(['{}. {}{}: **{}xp**'.format(
            i+1, getattr(top10n.get(u[0], {}), 'name', 'Unknown'),
            '#'+getattr(top10n.get(u[0], {}), 'discriminator', '0000'), ids[i][1]
        ) for i,u in enumerate(ids)])
        e = await self.helpers.build_embed(top10, 0xffffff)
        if location == 'Global':
            e.set_author(name=f'Leaderboard: {location}',
                         icon_url='https://i.imgur.com/q2I08K7.png')

        else:
            e.set_author(name=f'Leaderboard: {location}',
                         icon_url=m.guild.icon_url_as(format='jpeg'))
        e.add_field(name="Me", value=f"{myrank+1}.  **{myxp}xp**.")
        asyncio.ensure_future(ctx.send(embed=e))

    @commands.command(name="rank", no_pm=True)
    async def _rank(self, ctx, member: str=None):
        m = ctx.message
        a = m.author
        if not member:
            u = a
        elif member and not member.isnumeric():
            u = await self.helpers.choose_member(ctx, m.guild, member)
        
        g = await self.helpers.get_record('server', m.guild.id)
        u_global = sorted(self.bot._users,
                           key=lambda u: u.xp['amount'], reverse=True)
        u_local = sorted(g.users, key=lambda u: u['xp'], reverse=True)
        rank_global = await self._lb_get_global_rank(u.id, u_global)
        xp_global = u_global[rank_global].xp['amount']
        rank_local = await self._lb_get_local_rank(u.id, u_local)
        xp_local = u_local[rank_local]['xp']
        embed = await self.helpers.build_embed(None, 0x36ce31)
        embed.set_thumbnail(url=u.avatar_url_as(format='jpeg'))
        embed.set_author(name=f'Rank: {u.name}#{u.discriminator}', icon_url=u.avatar_url_as(format='jpeg'))
        embed.add_field(name=m.guild.name, value=f'{rank_local+1}. **{xp_local}**xp')
        embed.add_field(name="Global", value=f'{rank_global+1}. **{xp_global}**xp')
        asyncio.ensure_future(ctx.send(embed=embed))



    async def add_xp(self, message):
        m = message
        a = m.author
        if not isinstance(message.channel, discord.abc.PrivateChannel) and len(message.content) >= 10 and not a.bot:
            if not self.is_command.match(message.content):
                u = await self.helpers.get_record('user', m.author.id)
                now = datetime.utcnow().timestamp()
                
                last_xp = u.timers.get('last_xp')
                if not last_xp or now - last_xp >= 25:
                    xp = self.xp_unit + rndchoice([1,2,2,2,2,2,3,3,4,3,2,2,4,15])
                    g = await self.helpers.get_record('server', m.guild.id)
                    u.timers['last_xp'] = now
                    u.xp['amount'] = u.xp.get('amount', 0) + xp
                    if not g.users:
                        g.users = []
                    if not [x for x in g.users if x['id']==m.author.id]:
                        g.users.append({'id': m.author.id, 'xp': 0})
                    u = [x for x in g.users if x['id']==m.author.id][0]
                    u['xp'] = u['xp'] + xp



def setup(bot):
    cog = LevelsCog(bot)
    bot.add_listener(cog.add_xp, "on_message")
    bot.add_cog(cog)
