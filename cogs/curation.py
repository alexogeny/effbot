import os, time
import discord
import asyncio
import re
from discord.ext import commands
from random import choice as rndchoice
from urllib.parse import urlparse
from discord.ext.commands import DisabledCommand



def is_curator_or_higher():
    async def _is_moderator_or_higher(ctx):
        msg = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        u_roles = [a.id for a in msg.author.roles]
        a,b,c=g.roles.get('admin'),g.roles.get('moderator'),g.roles.get('curator')
        is_admin = a in u_roles
        is_mod = b in u_roles
        is_cur = c in u_roles
        if any([is_admin, is_mod, is_cur]):
            return True
        else:
            asyncio.ensure_future(ctx.send('You need to be curator+ in order to use this command.'))
            return False

    return commands.check(_is_moderator_or_higher)

def has_update():
    async def _has_update(ctx):
        msg = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        if not g.roles.get('updates'):
            asyncio.ensure_future(ctx.send(
                'This server needs to have an `update` role setup.\n'
                '`.settings set updatesrole rolename`'))
            return False
        return True
    return commands.check(_has_update)

def has_dj():
    async def _has_dj(ctx):
        msg = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        if not g.roles.get('dj'):
            asyncio.ensure_future(ctx.send(
                'This server needs to have a `DJ` role setup.\n'
                '`.settings set djrole rolename`'))
            return False
        return True
    return commands.check(_has_dj)

class Curation():
    """
    Manage who can run commands and where, quote users, disable commands."""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')

    @has_update()
    @is_curator_or_higher()
    @commands.command(name='update')
    async def update(self, ctx, channel):
        """Posts an update to the updates channel and mentions the updates role."""
        m = ctx.message
        g = await self.helpers.get_record('server', m.guild.id)
        a = m.author
        if not a.bot:
            if channel.startswith('#'):
                channel = channel[1:]
            elif channel.startswith('<#') and len(m.channel_mentions)>0:
                channel = m.channel_mentions[0].name
            channel = await self.helpers.choose_channel(ctx, m.guild, channel)
            if not channel:
                asyncio.ensure_future(ctx.send('Sorry, I could not find a channel with that name.'))
                return
            role = next((r for r in a.guild.roles if r.id == g.roles.get('updates')), None)
            was_false = False
            try:
                if role.mentionable == False:
                    was_false = True
                    await role.edit(mentionable=True)
                    pfx = await self.bot.get_prefix(m)
                    mc = m.content
                    passed = 0
                    while not passed:
                        for p in pfx:
                            if mc.startswith(p):
                                mc = mc[len(p):]
                                passed = 1
                    mc = re.sub(r'^([^\s]+)','',mc).strip()
                    mc = re.sub(r'^([^\s]+)','',mc.strip()).strip()
                    mc = f'{mc}\n\n{role.mention}'
                    send_to = await channel.send(mc)
                elif role.mentionable == True:
                    await ctx.send('Oops, looks like the role can be abused.'
                        '\nSet mentionable to off before doing an update command.')
                if was_false:
                    await role.edit(mentionable=False)
                    asyncio.ensure_future(ctx.send('Successfully posted the update!'))
            except discord.Forbidden:
                asyncio.ensure_future(ctx.send(f'I cannot toggle the updates role to be mentioned.'
                    '\nI would suggest placing my role above `{role.name}`'))
            

    @has_update()
    @commands.command(name='updates')
    async def _updates(self, ctx, state):
        m = ctx.message
        a = m.author
        if not a.bot and state.lower() in ['on','off']:
            print('Changing setting for user')
            g = await self.helpers.get_record('server', a.guild.id)
            if g and g.roles.get('updates'):
                role = next((r for r in a.guild.roles if r.id == g.roles.get('updates')), None)
                if role and state.lower() == 'on':
                    await a.add_roles(role)
                    await ctx.send(f'Successfully added the updates role'
                        f' to {a.name}#{a.discriminator}!')
                elif role and state.lower() == 'off':
                    await a.remove_roles(role)
                    await ctx.send(f'Successfully removed the updates role'
                        f' from {a.name}#{a.discriminator}!')

    @is_curator_or_higher()
    @commands.command(pass_context=True, name="whitelist", aliases=["wl"])
    async def whitelist(self, ctx, command: str, channels: str=''):
        chans = channels.split(',')
        m = ctx.message
        g = await self.helpers.get_record('server', m.guild.id)
        if command.strip().lower() in self.bot.all_commands:
            chans = [await self.helpers.get_obj(
                m.guild, 'channel', 'name', c
            ) for c in chans if not c.isdigit()] + [
                int(c) for c in chans if c.isdigit()
            ]
        
            command = self.bot.all_commands[command.strip().lower()].name
            if not g.restrictions.get(command):
                g.restrictions[command] = dict(wl=[], bl=[], disable=False,
                                               restrict=[])
            if chans:
                for c in chans:
                    if c not in g.restrictions[command]['wl']:
                        g.restrictions[command]['wl'].append(c)
            else:
                g.restrictions[command]['wl']=[]

    @is_curator_or_higher()
    @commands.command(pass_context=True, name="blacklist", aliases=["bl"])
    async def blacklist(self, ctx, command: str, channels: str=''):
        chans = channels.split(',')
        m = ctx.message
        g = await self.helpers.get_record('server', m.guild.id)
        if command.strip().lower() in self.bot.all_commands:
            chans = [await self.helpers.get_obj(
                m.guild, 'channel', 'name', c
            ) for c in chans if not c.isdigit()] + [
                int(c) for c in chans if c.isdigit()
            ]
        
            command = self.bot.all_commands[command.strip().lower()].name
            if command not in g.restrictions:
                g.restrictions[command] = dict(wl=[], bl=[], disable=False,
                                               restrict=[])
            if chans:
                for c in chans:
                    if c not in g.restrictions[command]['bl']:
                        g.restrictions[command]['bl'].append(c)
            else:
                g.restrictions[command]['bl']=[]

    @is_curator_or_higher()
    @commands.command(pass_context=True, name="disable", aliases=["enable"], no_pm=True)
    async def disable(self, ctx, command: str):
        m = ctx.message
        g = await self.helpers.get_record('server', m.guild.id)
        if command.strip().lower() in self.bot.all_commands:
            command = self.bot.all_commands[command.strip().lower()].name
            if command == 'disable':
                return
            if command not in g.restrictions:
                g.restrictions[command] = dict(wl=[], bl=[], disable=False,
                                               restrict=[])
            if not g.restrictions[command]['disable']:
                g.restrictions[command]['disable']=True
                await ctx.send(f'Command `{command}` was disabled.')
            else:
                g.restrictions[command]['disable']=False
                await ctx.send(f'Command `{command}` was enabled.')

    @is_curator_or_higher()
    @commands.command(name='restrict', aliases=["unrestrict"], no_pm=True)
    async def restrict(self, ctx, command: str, role: str):
        m = ctx.message
        a = m.author
        g = await self.helpers.get_record('server', m.guild.id)
        if command.strip().lower() in self.bot.all_commands:
            c = self.bot.all_commands[command.strip().lower()].name
            roles = [r for r in m.guild.roles]
            if not role.isnumeric():
                role = await self.helpers.choose_role(ctx, m.guild, role)
                if not role:
                    return
                if c not in g.restrictions:
                    g.restrictions[c] = dict(wl=[], bl=[], disable=False,
                                             restrict=[])
                if role.id not in g.restrictions[c]['restrict']:
                    g.restrictions[c]['restrict'].append(role.id)
                    await ctx.send(f'`{c}` was restricted to `{role.name}`')
                else:
                    g.restrictions[c]['restrict']=[
                        x for x in g.restrictions[c]['restrict'] if not x == role.id
                    ]
                    await ctx.send(f'`{role.name}` removed from `{c}` restrictions')

    @is_curator_or_higher()
    @has_dj()
    @commands.command(name='dj', aliases=['djadd'], no_pm=True)
    async def dj(self, ctx, user: str=None):
        if not user:
            user = ctx.message.author
        else:
            user = await self.helpers.choose_member(ctx, ctx.message.guild, user)
        if not user:
            return
        g = await self.helpers.get_record('server', ctx.message.guild.id)
        dj = g.roles.get('dj')
        role = next((r for r in user.guild.roles if r.id == dj), None)
        if role not in [r for r in user.roles]:
            await user.add_roles(role)
            asyncio.ensure_future(ctx.send('Successfully added `DJ` role to '
                                           f'{user.name}#{user.discriminator}.'))
        else:
            await user.remove_roles(role)
            asyncio.ensure_future(ctx.send('Successfully removed `DJ` role from '
                                           f'{user.name}#{user.discriminator}.'))


    @is_curator_or_higher()
    @commands.command(pass_context=True, name="quote")
    async def quote(self, ctx, channel: str, message_id: str):
        m = ctx.message
        a = m.author
        g = await self.helpers.get_record('server', m.guild.id)
        q = g.channels.get('quotes')
        if not q:
            asyncio.ensure_future(ctx.send('Oops, ask an admin to set up a quotes channel'))
            return
        result = await self.helpers.choose_channel(ctx, m.guild, channel)
        if result and message_id.isdigit():
            if not g.extra.get('quotes'):
                g.extra['quotes']=[]
            c = result
            message = await c.get_message(message_id)
            if message and message.id not in g.extra.get('quotes'):
                a = message.author
                g.extra['quotes'].append(message.id)
                embed = await self.helpers.build_embed(message.content, a.color)
                embed.set_author(name=f'{a.name}#{a.discriminator}', icon_url=a.avatar_url_as(format='jpeg'))
                embed.add_field(name=f'Quote #{len(g.extra["quotes"])}', value=f'in {c.mention}')
                embed.add_field(name=f'Quoted by {a.name}#{a.discriminator}',
                            value=f'{m.jump_url}')
                await self.bot.get_channel(q).send(embed=embed)
                await ctx.send('Quote added successfully!')
            elif message.id in g.extra['quotes']:
                await ctx.send('Oops, it seems that has already been quoted.')
            else:
                await ctx.send('Did not find that message, sorry!')
        else:
            await ctx.send('Check you supplied a valid channel name+message id')

    async def curate_channels(self, message):
        if not isinstance(message.channel, discord.abc.PrivateChannel):
            m = message
            c, guild, a = m.channel, m.guild, m.author
            g = await self.helpers.get_record('server', guild.id)
            if g and c.id in g.channels.get('curated', []):
                try:
                    r=urlparse(m.content)
                except:
                    r=None
                finally:
                    if not m.embeds and not m.attachments and not getattr(r, 'netloc', None):
                        await m.delete()
                        await self.bot.get_user(a.id).send(
                            (f'Hey {a.name}, <#{c.id}> is a curated channel,'
                              ' meaning you can only send links or pictures.')
                        )

    async def quote_react(self, reaction, user):
        m = reaction.message
        if not isinstance(reaction.message.channel, discord.abc.PrivateChannel) and reaction.emoji == "⭐":
            g = await self.helpers.get_record('server', m.guild.id)
            u = user
            q = g.channels.get('quotes')
            # print(q)
            if not q:
                return
            if m.id in g.extra.get('quotes',[]):
                return
            u_roles = [a.id for a in u.roles]
            is_admin = g.roles.get('admin') in u_roles
            is_mod = g.roles.get('moderator') in u_roles
            is_cur = g.roles.get('curator') in u_roles
            if not any([is_admin, is_mod, is_cur]):
                return
            a = m.author
            c = m.channel
            if not g.extra.get('quotes'):
                g.extra['quotes']=[]
            g.extra['quotes'].append(m.id)
            # print(m.content)
            e = await self.helpers.build_embed(m.content, a.color)
            e.set_author(name=f'{a.name}#{a.discriminator}', icon_url=a.avatar_url_as(format='jpeg'))
            e.add_field(name=f'Quote #{len(g.extra["quotes"])}', value=f'in {c.mention}')
            e.add_field(name=f'Quoted by {user.name}#{user.discriminator}',
                        value=f'{m.jump_url}')
            asyncio.ensure_future(self.bot.get_channel(q).send(embed=e))

    
    async def check_restrictions(self, ctx):
        if not isinstance(ctx.message.channel, discord.abc.PrivateChannel):
            c = ctx.command
            m = ctx.message
            g = await self.helpers.get_record('server', m.guild.id)
            chan = ctx.channel
            # print(chan)
            c = self.bot.all_commands[c.name].name
            if g.restrictions.get(c):
                r = g.restrictions[c]
                # print(r)
                # print([i for i in m.author.roles])
                if r['disable']==True:
                    msg = 'That command is disabled in this server.'
                elif bool(r['restrict']) and not set([i.id for i in m.author.roles]).intersection(r['restrict']):
                    msg = ('You do not have the required roles to'
                           ' use this command.')
                elif bool(r['wl']) and chan.id not in r['wl']:
                    msg = 'That command can only be used in: {}'.format(
                        ', '.join([f'<#{c}>' for c in r['wl']])
                    )
                elif bool(r['bl']) and chan in r['bl']:
                    msg = 'That command is disabled in this channel.'
                else:
                    return True
                asyncio.ensure_future(ctx.send(msg))
                return False
            return True

def setup(bot):
    cog = Curation(bot)
    # bot.add_listener(cog.curate_channels, "on_message")
    # bot.add_check(cog.check_restrictions, call_once=True)
    # bot.add_listener(cog.quote_react, "on_reaction_add")
    bot.add_cog(cog)
