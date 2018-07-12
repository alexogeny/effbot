import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice

def is_admin_or_owner():
    async def _is_admin_or_owner(ctx):
        msg = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        print([a.id for a in msg.author.roles])
        if g['config'].role_admin in [a.id for a in msg.author.roles]:
            return True
        elif msg.author.id == msg.guild.owner_id:
            return True
        elif g['config'].role_admin not in [a.id for a in msg.author.roles]:
            await ctx.send('You need to be a server admin in order to do that.')
            return False
    return commands.check(_is_admin_or_owner)

class SettingsCog():
    """Set up server roles, configure logging, welcome messages, and so on."""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.cogs['Helpers']

    @commands.group(pass_context=True, name="settings")
    async def settings(self, ctx):
        pass

    @settings.command(pass_context=True)
    @is_admin_or_owner()
    async def set(self, ctx, setting: str=None, value: str=None):
        guild_id = ctx.message.guild.id
        key = setting.lower().strip()
        msg = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        
        if key == 'adminrole' and not msg.author.id == msg.guild.owner_id:
            await ctx.send('You must be server owner to set the adminrole.')
            return
        elif key == 'adminrole' and msg.author.id == msg.guild.owner_id:
            result = await self.helpers.get_obj(msg.guild, 'role', 'name', value)
            if result:
                g['config'].role_admin = result
                await ctx.send('Successfully updated the admin role!')
            else:
                await ctx.send('Sorry, I could not find a role with that name.')
            return

        if key == 'modrole':
            result = await self.helpers.get_obj(msg.guild, 'role', 'name', value)
            if result:
                g['config'].role_moderator = result
                await ctx.send(f'Set the {key}!')

        if key.startswith('log') and key[3:] in 'leaves,joins,messages,moderations':
            result = await self.helpers.get_obj(msg.guild, 'channel', 'name', value)
            if result:
                setattr(g['config'], f'log_{key[3:-1]}', result)
                await ctx.send(f'Set the {key} setting to <#{result}>')

        if key == 'curated':
            result = await self.helpers.get_obj(msg.guild, 'channel', 'name', value)
            c=g['config'].chan_curated
            if result and result not in c:
                c.append(result)
                await ctx.send(f'Added <#{result}> to curated channels')
            elif result and result in c:
                c = [ch for ch in c if ch!=c]
                await ctx.send(f'Removed <#{result}> from curated channels')

        if key == 'quoteschannel':
            result = await self.helpers.get_obj(msg.guild, 'channel', 'name', value)
            if result:
                g['config'].chan_quotes = result
                await ctx.send(f'Set the {key} setting to <#{result}>')

def setup(bot):
    cog = SettingsCog(bot)
    bot.add_cog(cog)
