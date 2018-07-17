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
        
        if key == 'adminrole' and msg.author.id in [msg.guild.owner_id, 305879281580638228]:
            result = await self.helpers.get_obj(msg.guild, 'role', 'name', value)
            if result:
                g.roles['admin'] = result
                await ctx.send('Successfully updated the admin role!')
            else:
                await ctx.send('Sorry, I could not find a role with that name.')
            return

        elif key == 'modrole':
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            if result:
                g.roles['moderator'] = result
                await ctx.send(f'Set the {key}!')
        elif key == 'curator':
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            if result:
                g.roles['curator'] = result
                await ctx.send(f'Set the {key}!')

        elif key in ['grandmaster', 'ttgm', 'gm']:
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            if result:
                g.tt['role_gm'] = result
                await ctx.send(f'Set the grandmaster role!')

        elif key.startswith('log') and key[3:] in 'leave,join,message,moderation':
            result = await self.helpers.choose_channel(ctx, msg.guild, value)
            if result:
                g.roles[key[3:]] = result.id
                await ctx.send(f'Set the {key} setting to {result.mention}')

        elif key == 'curated':
            result = await self.helpers.choose_channel(ctx, msg.guild, value)
            # c=g['config'].chan_curated
            if not g.channels.get('curated'):
                g.channels['curated'] = []
            if result and result not in g.channels['curated']:
                g.channels['curated'].append(result)
                await ctx.send(f'Added <#{result}> to curated channels')
            elif result and result in g.channels['curated']:
                g.channels['curated'] = [ch for ch in g.channels['curated'] if ch!=c]
                await ctx.send(f'Removed {result.mention} from curated channels')

        elif key == 'quoteschannel':
            result = await self.helpers.choose_channel(ctx, msg.guild, value)
            if result:
                g.channels['quotes'] = result.id
                await ctx.send(f'Set the {key} setting to {result.mention}')

        elif key == 'updateschannel':
            result = await self.helpers.choose_channel(ctx, msg.guild, value)
            if result:
                g.channels['updates'] = result.id
                await ctx.send(f'Set the {key} setting to {result.mention}')
        elif key == 'updatesrole':
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            if result:
                g.roles['updates'] = result.id
                was_true = False
                try:
                    if result.mentionable == True:
                        was_true = True
                        await result.edit(mentionable=False)
                        await ctx.send(f'Set the {key} role to {result.mention}!')
                    if was_true:
                        asyncio.ensure_future(result.edit(mentionable=True))
                except discord.Forbidden:
                    asyncio.ensure_future(ctx.send(f'Set the `{key}` role to `{result.name}`!'))
                # await ctx.send(f'Set the `{key}` to `{result.name}`!')

        elif key == 'autorole':
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            if result:
                g.roles['auto'] = result.id
                was_true = False
                try:
                    if result.mentionable == True:
                        was_true = True
                        await result.edit(mentionable=False)
                        await ctx.send(f'Set the {key} role to {result.mention}!')
                    if was_true:
                        asyncio.ensure_future(result.edit(mentionable=True))
                except discord.Forbidden:
                    asyncio.ensure_future(ctx.send(f'Set the `{key}` role to `{result.name}`!'))

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
