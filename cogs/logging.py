import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice

class LogCog():
    """docstring for LogCog"""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.cogs['Helpers']

    @commands.group(pass_context=True, name="log")
    async def log(self, ctx):
        pass

    @log.command(pass_context=True)
    async def set(self, ctx, setting: str=None, value: str=None):

        guild_id = ctx.message.guild.id
        key = setting.lower().strip()

        if not [x for x in self.bot._servers if x['id']==guild_id]:
            g = {'id': guild_id}
            conf = await self.helpers.spawn_config('server')
            g['config'] = conf
            self.bot._servers.append(g)
        else:
            g = [x for x in self.bot._servers if x['id']==guild_id][0]
        # print(g)
        if not g['config'].role_admin:
            await ctx.send('The server owner needs to set an admin role using `e.set adminrole <role>')
            return

    async def log_join(self, member):
        log = await self.helpers.get_record('server', member.guild.id)
        if log and log['config'].log_join:
            # await asyncio.sleep(2)
            a = self.bot.get_user(member.id)
            embed = await self.helpers.build_embed(None, 0x36ce31)
            embed.set_thumbnail(url=a.avatar_url_as(format='jpeg'))
            embed.set_author(name=f'{a.name}#{a.discriminator}', icon_url=a.avatar_url_as(format='jpeg'))
            embed.add_field(name="Action", value='Join', inline=False)
            embed.add_field(name="User", value=f'<@{a.id}> ({a.id})', inline=False)
            await self.bot.get_channel(log['config'].log_join).send(embed=embed)


    async def log_leave(self, member):
        log = await self.helpers.get_record('server', member.guild.id)
        if log and log['config'].log_leave:
            a = member
            embed = await self.helpers.build_embed(None, 0xff0000)
            embed.set_thumbnail(url=a.avatar_url_as(format='jpeg'))
            embed.set_author(name=f'{a.name}#{a.discriminator}', icon_url=a.avatar_url_as(format='jpeg'))
            embed.add_field(name="Action", value='Leave', inline=False)
            embed.add_field(name="User", value=f'<@{a.id}> ({a.id})', inline=False)
            await self.bot.get_channel(log['config'].log_leave).send(embed=embed)

    async def log_delete(self, message):
        log = await self.helpers.get_record('server', message.guild.id)
        m, c, a = message, message.channel, message.author
        if log and log['config'].log_message and not a.bot:
            embed = await self.helpers.build_embed(None, 0xff0000)
            embed.set_thumbnail(url='https://discordapp.com/assets/b1868d829b37f0a81533ededb9ffe5f4.svg')
            embed.set_author(name=f'{a.name}#{a.discriminator}', icon_url=a.avatar_url_as(format='jpeg'))
            embed.add_field(name="Action", value='Delete', inline=False)
            embed.add_field(name="In", value=f'<#{c.id}> ({c.id})', inline=False)
            embed.add_field(name="Author", value=f'<@{a.id}> ({a.id})', inline=False)
            embed.add_field(name="Content", value=f'```\n{m.content}\n```')
            await self.bot.get_channel(log['config'].log_message).send(embed=embed)
    async def log_edit(self, before, after):
        log = await self.helpers.get_record('server', before.guild.id)
        m1, c, a = before, before.channel, before.author
        m2 = after
        if m1.content == m2.content:
            return
        if log and log['config'].log_message and not a.bot:
            embed = await self.helpers.build_embed(None, 0x5e26b7)
            embed.set_thumbnail(url='https://discordapp.com/assets/b1868d829b37f0a81533ededb9ffe5f4.svg')
            embed.set_author(name=f'{a.name}#{a.discriminator}',
                             icon_url=a.avatar_url_as(format='jpeg'))
            embed.add_field(name="Action", value='Edit', inline=False)
            embed.add_field(name="In", value=f'<#{c.id}> ({c.id})',
                            inline=False)
            embed.add_field(name="Author",
                            value=f'<@{a.id}> ({a.id})', inline=False)
            embed.add_field(name="Content before",
                            value=f'```\n{m1.content[0:800]}\n```', inline=False)
            embed.add_field(name="Content after", value=f'```\n{m2.content[0:800]}\n```')
            embed.add_field(name='Jumplink', value=f'[Click here to go there]({m2.jump_url})', inline=False)
            await self.bot.get_channel(log['config'].log_message).send(embed=embed)

    async def log_pin(self, channel, last_pin):
        log = await self.helpers.get_record('server', channel.guild.id)
        c = channel
        if log and log['config'].log_message:
            embed = await self.helpers.build_embed(None, 0x36ce31)
            embed.set_thumbnail(url='https://discordapp.com/assets/b1868d829b37f0a81533ededb9ffe5f4.svg')
            embed.add_field(name="Action", value='Pin/unpin', inline=False)
            embed.add_field(name="In", value=f'<#{c.id}> ({c.id})', inline=False)
            
            await self.bot.get_channel(log['config'].log_message).send(embed=embed)

def setup(bot):
    cog = LogCog(bot)
    bot.add_listener(cog.log_join, "on_member_join")
    bot.add_listener(cog.log_leave, "on_member_remove")
    bot.add_listener(cog.log_delete, "on_message_delete")
    bot.add_listener(cog.log_edit, "on_message_edit")
    bot.add_listener(cog.log_pin, "on_guild_channel_pins_update")
    bot.add_cog(cog)
