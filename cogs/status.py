# import os, time
import discord
from discord.http import Route
import asyncio
from datetime import datetime
from discord.ext import commands
import base64
from random import choice as rndchoice
from pathlib import Path

ACTIVITY_TYPES = ['playing', 'streaming', 'listening', 'watching']

# def is_owner():
    # async def predicate(ctx):
        # return ctx.author.id == 305879281580638228
    # return commands.check(predicate)

class RandomStatus():
    """docstring for RandomStatus"""
    def __init__(self, bot):
        
        self.bot = bot
        self._cwd = Path('..')
        self.last_status_change = None
        self.last_avatar_change = None
        self.last_avatar_name = None
        self.delay = 600
        self.statuses = [
            ('playing', 'in {guilds} guilds'),
            ('watching', 'over {users} users'),
            ('listening', 'the wind'),
            ('listening', 'the deep hum of mystical forces'),
            ('watching', 'footprints on the sands of time'),
            ('watching', 'grass grow'),
            ('watching', 'paint dry'),
            ('playing', 'God'),
            ('playing', 'the race card'),
            ('playing', 'with a full deck'),
            ('playing', 'with a loaded gun'),
            ('playing', 'Russian roulette'),
            ('playing', 'in the big leagues'),
            ('playing', 'effrill3 for a fool')
        ]
        self.avatars = {
            p.name: 'data:image/png;base64,'+base64.b64encode(p.open('rb').read()).decode('utf-8')
            for p
            in self._cwd.rglob('avatar ([1-9]).jpg')}
        # print(self.statuses)
    def edit_profile(self, avatar):
        payload = {
            'username': 'effbot',
            'avatar': avatar
        }
        return self.bot.http.request(Route('PATCH', '/users/@me'), json=payload)

    @commands.guild_only()
    async def rotate_avatar(self, m):
        now = datetime.utcnow()
        if not self.last_avatar_change or (now-self.last_avatar_change).total_seconds() >= self.delay*6:
            self.last_avatar_change = now
            self.last_avatar_name = rndchoice([p for p in self.avatars if self.last_avatar_name != p])
            # print(self.avatars[self.last_avatar_name])
            asyncio.ensure_future(self.edit_profile(avatar=self.avatars[self.last_avatar_name]))

    @commands.guild_only()
    async def rotate_status(self, m):
        me, now = m.guild.me, datetime.utcnow()
        activity, presence = me.activity, me.status
        # print(activity)
        # print(presence)
        if not self.last_status_change or (now - self.last_status_change).total_seconds() >= self.delay:
            self.last_status_change = now
            status, activity = await self.choose_status(activity)
            # print(status)
            # print(activity)
            asyncio.ensure_future(self.change_status(status, activity, presence))
    
    async def change_status(self, status, activity, presence):
        # print('changing status')
        act = discord.Activity(
            name=activity.format(guilds=len(self.bot.guilds), users=len(self.bot.users)),
            type='playing streaming listening watching'.split().index(status)
        )
        await self.bot.change_presence(activity=act, status=presence)
    
    async def choose_status(self, current):
        # while current == new:
        status, activity = rndchoice([(x,y) for x,y in self.statuses if y != current])
        return status, activity

        
def setup(bot):
    cog = RandomStatus(bot)
    bot.add_listener(cog.rotate_status, "on_message")
    bot.add_listener(cog.rotate_avatar, "on_message")
    bot.add_cog(cog)