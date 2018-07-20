import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice

class LogCog():
    """docstring for LogCog"""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')

    async def log_join(self, member):
        gid = member.guild.id
        guild = await self.helpers.get_record('server', gid)
        if guild.logs.get('join'):
            a = member
            
            await asyncio.sleep(5)
            embed = await self.helpers.build_embed(f'Joined the server', 0x36ce31)
            embed.set_thumbnail(url=a.avatar_url_as(format='jpeg'))
            embed.set_author(name=f'{a.name}#{a.discriminator} ({a.id})', icon_url='https://i.imgur.com/FSWLAco.png')
            asyncio.ensure_future(self.bot.get_channel(guild.logs['join']).send(embed=embed))


    async def log_leave(self, member):
        gid = member.guild.id
        guild = await self.helpers.get_record('server', gid)
        if guild.logs.get('leave'):
            a = member
            embed = await self.helpers.build_embed(f'Left the server', 0xff0000)
            embed.set_thumbnail(url=a.avatar_url_as(format='jpeg'))
            embed.set_author(name=f'{a.name}#{a.discriminator} ({a.id})', icon_url='https://i.imgur.com/1aAsAvW.png')
            asyncio.ensure_future(self.bot.get_channel(guild.logs['leave']).send(embed=embed))

    async def log_delete(self, message):
        guild = await self.helpers.get_record('server', message.guild.id)
        m, c, a = message, message.channel, message.author
        if guild.logs.get('message') and not a.bot:
            embed = await self.helpers.build_embed(f'Message deleted in {c.mention}', 0xff0000)
            embed.set_thumbnail(url=a.avatar_url_as(format='jpeg'))
            embed.set_author(name=f'{a.name}#{a.discriminator} ({a.id})', icon_url='https://i.imgur.com/nOIAqUH.png')
            embed.add_field(name="Content", value=f'```\n{m.content}\n```')
            asyncio.ensure_future(self.bot.get_channel(guild.logs['message']).send(embed=embed))
    
    async def log_edit(self, before, after):
        guild = await self.helpers.get_record('server', before.guild.id)
        m1, c, a = before, before.channel, before.author
        m2 = after
        if m1.content == m2.content:
            return
        if guild.logs.get('message') and not a.bot:
            embed = await self.helpers.build_embed(f'Message edited in {c.mention}', 0x5e26b7)
            embed.set_thumbnail(url=a.avatar_url_as(format='jpeg'))
            embed.set_author(name=f'{a.name}#{a.discriminator} ({a.id})',
                             icon_url='https://i.imgur.com/8VYSu5I.png')
            embed.add_field(name="Content before",
                            value=f'```\n{m1.content[0:800]}\n```', inline=False)
            embed.add_field(name="Content after", value=f'```\n{m2.content[0:800]}\n```')
            embed.add_field(name='Jumplink', value=f'{m2.jump_url}', inline=False)
            asyncio.ensure_future(self.bot.get_channel(guild.logs['message']).send(embed=embed))

    async def log_pin(self, channel, last_pin):
        guild = await self.helpers.get_record('server', channel.guild.id)
        c = channel
        if guild.logs.get('message'):
            embed = await self.helpers.build_embed(None, 0x36ce31)
            embed.set_thumbnail(url='https://i.imgur.com/yNlWCen.png')
            embed.add_field(name="Action", value='Pin/unpin', inline=False)
            embed.add_field(name="In", value=f'<#{c.id}> ({c.id})', inline=False)
            
            asyncio.ensure_future(self.bot.get_channel(guild.logs['message']).send(embed=embed))

def setup(bot):
    cog = LogCog(bot)
    bot.add_listener(cog.log_join, "on_member_join")
    bot.add_listener(cog.log_leave, "on_member_remove")
    bot.add_listener(cog.log_delete, "on_message_delete")
    bot.add_listener(cog.log_edit, "on_message_edit")
    bot.add_listener(cog.log_pin, "on_guild_channel_pins_update")
    bot.add_cog(cog)
