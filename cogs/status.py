import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice

ACTIVITY_TYPES = ['playing', 'streaming', 'listening', 'watching']

def is_owner():
    async def predicate(ctx):
        return ctx.author.id == 305879281580638228
    return commands.check(predicate)

class RandomStatus():
    """docstring for RandomStatus"""
    def __init__(self, bot):
        
        self.bot = bot
        self.last_change = None
        self.delay = 300
        self.statuses = ['playing in {} guilds',
                         'watching over {} users',
                         'listening the sounds of nature',
                         'listening the wind',
                         'listening the deep hum of mystical forces',
                         'playing in the fields of yonder',
                         'playing the one single source of truth CD',
                         'playing with time']

    @commands.group(pass_context=True, invoke_without_command=True)
    @is_owner()
    async def status(self, ctx):
        await ctx.send("Um, you need to tell me what to do ...")

    @status.command(name='cycle', pass_context=True, no_pm=True)
    async def _set(self, ctx):
        current_status = ctx.message.guild.me.activity
        self.last_change = int(time.perf_counter())
        new_game, activity_type = self.random_status(ctx.message)
        await self.bot.change_presence(
           activity=(discord.Activity(name=new_game, type=activity_type)), status=current_status)
        await ctx.send("Ok, roger that, I've cycled my status. Nerd!")

    async def switch_status(self, message):
        if not isinstance(message.channel, discord.abc.PrivateChannel):
            current_game = str(message.guild.me.activity)
            current_status = message.guild.me.status

            if self.last_change == None: #first run
                self.last_change = int(time.perf_counter())
                if len(self.statuses) > 0 and (current_game in self.statuses or current_game == "None"):
                    new_game, activity_type = self.random_status(message)
                    await self.bot.change_presence(
                       activity=(discord.Activity(name=new_game, type=activity_type)), status=current_status)

            if message.author.id != self.bot.user.id:
                if abs(self.last_change - int(time.perf_counter())) >= self.delay:
                    self.last_change = int(time.perf_counter())
                    new_game, activity_type = self.random_status(message)
                    if new_game != None:
                        if current_game != new_game:
                            if current_game in self.statuses or current_game == "None":
                                await self.bot.change_presence(
                                    activity=(discord.Activity(name=new_game, type=activity_type)), status=current_status)
    def random_status(self, msg):
        current = str(msg.guild.me.activity)
        new = str(msg.guild.me.activity)
        if len(self.statuses) > 1:
            while current == new:
                new = rndchoice(self.statuses)
                if '{}' in new:
                    new = new.format(len(getattr(self.bot, new.split(' ')[-1])))
                
        else:
            new = None
        return ' '.join(new.split(' ')[1:]), ACTIVITY_TYPES.index(new.split(' ')[0])

def setup(bot):
    cog = RandomStatus(bot)
    bot.add_listener(cog.switch_status, "on_message")
    bot.add_cog(cog)
