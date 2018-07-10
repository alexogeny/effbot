import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice
from discord.ext.commands import DisabledCommand
class RestrictedWhiteListError(Exception):
    pass
class RestrictedBlackListError(Exception):
    pass
class RestrictedDisabledError(Exception):
    pass
class RestrictedRestrictError(Exception):
    pass

def is_curator_or_higher():
    async def _is_moderator_or_higher(ctx):
        msg = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        u_roles = [a.id for a in msg.author.roles]
        a,b,c=g['config'].role_admin,g['config'].role_moderator,g['config'].role_curator
        is_admin = a and a in u_roles
        is_mod = b and b in u_roles
        is_cur = c and c in u_roles
        if any([is_admin, is_mod, is_cur]):
            return True
        else:
            await ctx.send('You need to be curator+ in order to use this command.')
            return False

    return commands.check(_is_moderator_or_higher)


class Curation():
    """
    Manage who can run commands and where, quote users, disable commands."""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')

    # @commands.group(pass_context=True, name="curation")
    # async def curation(self, ctx):
    #     pass

    @is_curator_or_higher()
    @commands.command(pass_context=True, name="whitelist", aliases=["wl"])
    async def whitelist(self, ctx, command: str, channels: str=''):
        chans = channels.split(',')
        m = ctx.message
        g = await self.helpers.get_record('server', m.guild.id)
        if not hasattr(g['config'], 'restrictions'):
            setattr(g['config'], 'restrictions', [])
        if command.strip().lower() in self.bot.all_commands:
            chans = [await self.helpers.get_obj(
                m.guild, 'channel', 'name', c
            ) for c in chans if not c.isdigit()] + [
                int(c) for c in chans if c.isdigit()
            ]
        
            command = self.bot.all_commands[command.strip().lower()].name
            g['config'].restrictions = [r for r in g['config'].restrictions
                              if not r['command'] == command]
            g['config'].restrictions.append({'kind': 'wl', 'command': command,
                                   'channels': [c for c in chans]})

    @is_curator_or_higher()
    @commands.command(pass_context=True, name="blacklist", aliases=["bl"])
    async def blacklist(self, ctx, command: str, channels: str=''):
        chans = channels.split(',')
        m = ctx.message
        g = await self.helpers.get_record('server', m.guild.id)
        if not hasattr(g['config'], 'restrictions'):
            setattr(g['config'], 'restrictions', [])
        if command.strip().lower() in self.bot.all_commands:
            chans = [await self.helpers.get_obj(
                m.guild, 'channel', 'name', c
            ) for c in chans if not c.isdigit()] + [
                int(c) for c in chans if c.isdigit()
            ]
        
            command = self.bot.all_commands[command.strip().lower()].name
            g['config'].restrictions = [r for r in g['config'].restrictions
                              if not r['command'] == command]
            g['config'].restrictions.append({'kind': 'bl', 'command': command,
                                   'channels': [c for c in chans]})

    @is_curator_or_higher()
    @commands.command(pass_context=True, name="disable", aliases=["enable"], no_pm=True)
    async def disable(self, ctx, command: str):
        m = ctx.message
        g = await self.helpers.get_record('server', m.guild.id)
        if not hasattr(g['config'], 'restrictions'):
            setattr(g['config'], 'restrictions', [])
        if command.strip().lower() in self.bot.all_commands:
            command = self.bot.all_commands[command.strip().lower()].name
            if len([r for r in g['config'].restrictions
                   if r['command'] == command]) == 0:
                g['config'].restrictions.append({'kind': 'disable', 'channels':[],
                                                 'command': command})
                await ctx.send(f'Command `{command}` was disabled.')
            else:
                g['config'].restrictions = [r for r in g['config'].restrictions
                                            if not r['command'] == command]
                await ctx.send(f'Command `{command}` was enabled.')

    @is_curator_or_higher()
    @commands.command(name='restrict', no_pm=True)
    async def restrict(self, ctx, command: str, role: str):
        m = ctx.message
        a = m.author
        g = await self.helpers.get_record('server', m.guild.id)
        if not hasattr(g['config'], 'restrictions'):
            setattr(g['config'], 'restrictions', [])
        if command.strip().lower() in self.bot.all_commands:
            c = self.bot.all_commands[command.strip().lower()].name
            roles = [r for r in m.guild.roles]
            if not role.isnumeric():
                role = await self.helpers.get_obj(m.guild, 'role', 'name', role)
            if not role:
                await ctx.send(f'Could not find role `{role}`')
                return
            elif int(role) not in [r.id for r in roles]:
                await ctx.send(f'`{role}` is not a valid role id')
                return
            role = [r for r in roles if r.id == role][0]
        
            _r = [r for r in g['config'].restrictions if r['command'] == c]
            if len(_r) == 0:
                g['config'].restrictions.append({'kind': 'restrict', 'channels':[role.id],
                                             'command': c})
                await ctx.send(f'`{c}` was restricted to `{role.name}`')

    @is_curator_or_higher()
    @commands.command(name='unrestrict', no_pm=True)
    async def unrestrict(self, ctx, command: str):
        m = ctx.message
        a = m.author
        g = await self.helpers.get_record('server', m.guild.id)
        if not hasattr(g['config'], 'restrictions'):
            setattr(g['config'], 'restrictions', [])
        if command.strip().lower() in self.bot.all_commands:
            g['config'].restrictions = [r for r in g['config'].restrictions
                                        if not r['command'] == command]
            await ctx.send(f'`{command}` no longer restricted')

    @is_curator_or_higher()
    @commands.command(pass_context=True, name="quote")
    async def quote(self, ctx, channel: str, message_id: str):
        m = ctx.message
        g = await self.helpers.get_record('server', m.guild.id)
        q = g['config'].chan_quotes
        if not q:
            await ctx.send('Oops, ask an admin to set up a quotes channel')
            return
        result = await self.helpers.get_obj(m.guild, 'channel', 'name', channel)
        if result and message_id.isdigit():
            c = self.bot.get_channel(result)
            message = await c.get_message(message_id)
            if message:
                a = message.author
                embed = await self.helpers.build_embed(message.content, a.color)
                embed.set_author(name=f'{a.name}#{a.discriminator}', icon_url=a.avatar_url_as(format='jpeg'))
                embed.add_field(name="In", value=f'<#{c.id}>')
                embed.add_field(name="Author", value=f'<@{a.id}>')
                await self.bot.get_channel(q).send(embed=embed)
                await ctx.send('Quote added successfully!')
            else:
                await ctx.send('Did not find that message, sorry!')
        else:
            await ctx.send('Check you supplied a valid channel name+message id')

    async def curate_channels(self, message):
        if hasattr(message, 'guild'):
            m = message
            c, guild, a = m.channel, m.guild, m.author
            g = await self.helpers.get_record('server', guild.id)
            if g and c.id in g['config'].chan_curated:
                if not m.embeds and not m.attachments:
                    await m.delete()
                    await self.bot.get_user(a.id).send(
                        (f'Hey {a.name}, <#{c.id}> is a curated channel,'
                          ' meaning you can only send links or pictures.')
                    )

    async def quote_react(self, reaction, user):
        m = reaction.message
        if hasattr(m, 'guild') and reaction.emoji == "⭐":
            g = await self.helpers.get_record('server', m.guild.id)
            u = user
            q = g['config'].chan_quotes
            u_roles = [a.id for a in u.roles]
            is_admin = g['config'].role_admin in u_roles
            is_mod = g['config'].role_moderator in u_roles
            is_cur = g['config'].role_curator in u_roles
            if is_admin or is_mod or is_curator:
                a = m.author
                c = m.channel
                e = await self.helpers.build_embed(m.content, a.color)
                e.set_author(name=f'{a.name}#{a.discriminator}', icon_url=a.avatar_url_as(format='jpeg'))
                e.add_field(name="In", value=f'<#{c.id}>')
                e.add_field(name="Author", value=f'<@{a.id}>')
                await self.bot.get_channel(q).send(embed=e)


    def check_restricted(self, kind, channel, channels):
        if kind == 'wl' and channel not in channels:
            raise RestrictedWhiteListError
        elif kind == 'bl' and channel in channels:
            raise RestrictedBlackListError
        elif kind == 'disable':
            raise RestrictedDisabledError
        elif kind == 'restrict' and not [c for c in channel if c.id in channels]:
            raise RestrictedRestrictError
    
    async def check_restrictions(self, ctx):
        if hasattr(ctx.message, 'guild'):
            c = ctx.command
            m = ctx.message
            g = await self.helpers.get_record('server', m.guild.id)
            chan = ctx.channel
            if hasattr(g['config'], 'restrictions'):
                restricted = [r for r in g['config'].restrictions
                              if r['command']==c.name]
                if len(restricted) > 0:
                    chan = chan.id
                    r = restricted[0]
                    if r['kind'] == 'restrict':
                        chan = m.author.roles
                    try:
                        self.check_restricted(r['kind'], chan, r['channels'])
                    except RestrictedBlackListError:
                        await ctx.send('Sorry, that command is restricted and '
                                       'cannot be used here.')
                        setattr(ctx, 'was_limited', True)
                        return False
                    except RestrictedWhiteListError:
                        await ctx.send('Sorry, that command is restricted and '
                                       'can only be used in: {}.'.format(
                                        ', '.join([f'<#{c}>' for c in r['channels']])
                                       ))
                        setattr(ctx, 'was_limited', True)
                        return False
                    except RestrictedDisabledError:
                        await ctx.send(f'Sorry, `{c.name}` is disabled here.')
                        setattr(ctx, 'was_limited', True)
                        return False
                    except RestrictedRestrictError:
                        role = [_r for _r in m.guild.roles if _r.id == r["channels"][0]][0]
                        await ctx.send(f'`{c.name}` is restricted to `{role.name}`')
                        setattr(ctx, 'was_limited', True)
                        return False
            return True

def setup(bot):
    cog = Curation(bot)
    bot.add_listener(cog.curate_channels, "on_message")
    bot.add_check(cog.check_restrictions, call_once=True)
    bot.add_listener(cog.quote_react, "on_reaction_add")
    bot.add_cog(cog)
