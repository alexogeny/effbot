import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice

def is_admin_or_owner():
    async def _is_admin_or_owner(ctx):
        msg = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        if g.roles.get('admin') in [a.id for a in msg.author.roles]:
            return True
        elif ctx.author.id == 305879281580638228:
            return True
        elif msg.author.id == msg.guild.owner_id:
            return True
        elif g.roles.get('admin') not in [a.id for a in msg.author.roles]:
            await ctx.send('You need to be a server admin to do that.')
            return False
    return commands.check(_is_admin_or_owner)

class SettingsCog():
    """Set up server roles, configure logging, welcome messages, and so on."""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')

    @commands.group(pass_context=True, name="settings")
    async def settings(self, ctx):
        pass

    @settings.command(pass_context=True)
    @is_admin_or_owner()
    async def set(self, ctx, setting: str=None, value: str=None):
        guild_id = ctx.message.guild.id
        key = setting.lower().strip()
        msg = ctx.message
        g = await self.helpers.get_record('server', msg.guild.id)
        
        if key.replace('role', '')=='admin' and msg.author.id in [msg.guild.owner_id, 305879281580638228]:
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            key = key.replace('role', '')
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            if not result:
                asyncio.ensure_future(ctx.send('No roles found!'))
                return
            g.roles[key]=result.id
            asyncio.ensure_future(self.helpers.try_mention(ctx, f'`{key}` role', result))
            
        elif key.replace('role','') in ['moderator', 'curator', 'grandmaster', 'updates', 'auto']:
            key = key.replace('role', '')
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            if not result:
                asyncio.ensure_future(ctx.send('No roles found!'))
                return
            g.roles[key]=result.id
            asyncio.ensure_future(self.helpers.try_mention(ctx, f'`{key}` role', result))
            return


        elif key.startswith('log') and key[3:] in 'leave,join,message,moderation':
            result = await self.helpers.choose_channel(ctx, msg.guild, value)
            if result:
                g.logs[key[3:]] = result.id
                print(g.logs)
                await ctx.send(f'Set the {key} setting to {result.mention}')


        elif key.replace('channel', '') in ['quotes', 'updates', 'curated']:
            result = await self.helpers.choose_channel(ctx, msg.guild, value)
            key = key.replace('channel', '')
            if not g.channels.get(key):
                g.channels[key] = []
            if result and key == 'curated' and result not in g.channels[key]:
                g.channels[key].append(result.id)
                asyncio.ensure_future(ctx.send(
                    f'Added {result.mention} to curated channels.'
                ))
            elif result and key == 'curated' and result in g.channels[key]:
                g.channels[key] = [c for c in g.channels[key] if c!=result.id]
                asyncio.ensure_future(ctx.send(
                    f'Removed {result.mention} from curated channels.'
                ))
            elif result:
                g.channels[key] = result.id
                asyncio.ensure_future(ctx.send(
                    f'Set the {key} setting to {result.mention}'
                ))

    async def auto_role(self, member):
        gid = member.guild.id
        g = await self.helpers.get_record('server', gid)
        if g.roles.get('auto'):
            role = next((r for r in member.guild.roles if r.id == g.roles['auto']), None)
            if role:
                asyncio.ensure_future(member.add_roles(role))

def setup(bot):
    cog = SettingsCog(bot)
    bot.add_listener(cog.auto_role, "on_member_join")
    bot.add_cog(cog)
