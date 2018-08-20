import discord
import random
import time
import asyncio
from discord.ext import commands
from random import choice
from urllib.parse import urlparse

class Information():
    """Get information about a user, the server, the bot, etc."""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')

    @commands.group(pass_context=True, invoke_without_command=True)
    async def info(self, ctx):
        await ctx.send('placeholder')

    @info.command()
    async def uptime(self, ctx):
        """Gives the bot's uptime."""
        seconds = time.time() - self.bot.start_time
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        w, d = divmod(d, 7)
        asyncio.ensure_future(ctx.send(f"I've been online for `{int(w)}w : {int(d)}d : {int(h)}h : {int(m)}m : {int(s)}s`"))

    @commands.command()
    async def ping(self, ctx):
        """Pings the bot."""
        joke = random.choice(["not actually pinging server...", "hey bb", "what am I doing with my life",
                              "Some Dragon is a dank music bot tbh", "I'd like to thank the academy for this award",
                              "The NSA is watching 👀", "`<Insert clever joke here>`", "¯\\_(ツ)_/¯", "(づ｡◕‿‿◕｡)づ",
                              "I want to believe...", "Hypesquad is a joke", "EJH2#0330 is my daddy", "Robino pls",
                              "Seth got arrested again...", "Maxie y u do dis", "aaaaaaaaaaaAAAAAAAAAA", "owo",
                              "uwu", "meme team best team", "made with dicksword dot pee why", "I'm running out of "
                                                                                               "ideas here",
                              "am I *dank* enough for u?", "this is why we can't have nice things. come on",
                              "You'll understand when you're older...", "\"why\", you might ask? I do not know...",
                              "I'm a little tea pot, short and stout", "I'm not crying, my eyeballs "
                                                                       "are sweating!",
                              "When will the pain end?", "Partnership when?", "Hey Robino, rewrite when?"])
        before = time.monotonic()
        ping_msg = await ctx.send(joke)
        after = time.monotonic()
        ping = (after - before) * 1000
        asyncio.ensure_future(ping_msg.edit(content=f"***{ping:.0f}ms***"))

    @info.command(name='bot', aliases=['effbot', '<@466854404965007360>', '<@!466854404965007360>'], no_pm=True)
    async def _bot(self, ctx):
        embed = discord.Embed(title='Effbot', description='I am the mighty Effbot. Born a human, but raised by gods.')
        embed.add_field(name='Author', value='effrill3#0001')
        embed.add_field(name='User Count', value=f'{len(self.bot.users)}')
        embed.add_field(name='Server Count', value=f'{len(self.bot.guilds)}')
        embed.add_field(name='Invite', value='[Bot Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=466854404965007360&permissions=2146954487&scope=bot)')
        asyncio.ensure_future(ctx.send(embed=embed))

    @commands.command(name='patreon', aliases=['patron', 'donate', 'donations'])
    async def _patreon(self, ctx):
        asyncio.ensure_future(ctx.send((
            'Wow, I _love_ that you want to support me! You can support the bot on Patreon: <https://www.patreon.com/effrill3>'
        )))

    @commands.command(name='emoji', alises=['emojiexport'])
    async def _emoji(self, ctx, server: int):
        if ctx.author.id != 305879281580638228:
            return

        emojis = self.bot.get_guild(server).emojis
        for chunk in self.helpers.chunker(emojis, 30):
            asyncio.ensure_future(ctx.send(
                '```'+'\n'.join([str(e) for e in chunk])+'```'
            ))

    @info.command(name='commands')
    async def _commands(self, ctx):
        cogs = [c for c in self.bot.cogs if c not in 'LogCog,TitanLord,Owner,Helpers,RandomStatus']
        e = await self.helpers.build_embed(
            'Available modules of effbot', 0xffffff
        )
        
        for cog in cogs:
            c = self.bot.get_cog(cog)
            cxs = ', '.join(
                [x.name for x in self.bot.get_cog_commands(cog)]
            )

            e.add_field(
                name=f'{cog.replace("Cog","")}',
                value=f'```\n{cxs}\n```',
                inline=False
            )
        
        await ctx.send(embed=e)

    @info.command(name='user', no_pm=True)
    async def _user(self, ctx, *, user: str=None):
        """Shows users's informations"""
        a = ctx.author
        srv = ctx.guild

        author = ctx.message.author
        if not user:
            user = author
        elif not hasattr(user, 'roles') and not user.isnumeric():
            try:
                user = await self.helpers.choose_member(ctx, srv, user)
            except:
                user = await self.bot.get_user_info(int(user[2:-1]))
        elif user.isnumeric():
            try:
                user = await self.bot.get_user_info(int(user))
            except:
                pass
        if not user:
            return
        if not hasattr(user, 'roles'):
            roles = []
        else:
            roles = [x.name for x in user.roles if x.name != "@everyone"]

        since_created = (ctx.message.created_at - user.created_at).days
        try:
            joined_at = user.joined_at
            since_joined = (ctx.message.created_at - user.joined_at).days
            user_joined = joined_at.strftime("%d %b %Y %H:%M")
        except:
            user_joined = None
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        try:
            member_number = sorted(srv.members,
                               key=lambda m: m.joined_at).index(user) + 1
        except:
            member_number = None

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        if user_joined:
            joined_on = "{}\n({} days ago)".format(user_joined, since_joined)
        try:
            game = "Chilling in {} status".format(user.status)
        except:
            game = None

        if not hasattr(user, 'activity'):
            game = None
        elif not hasattr(user.activity, 'url'):
            game = "{}".format(user.activity)
        elif isinstance(user.activity, discord.activity.Activity):
            game = "Streaming: [{}]({})".format(user.activity.name, user.activity.url)
        else:
            game = "Streaming: [{}]({})".format(user.activity.name, user.activity.url)

        if roles:
            # roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                       # if x.name != "@everyone"].index)
            roles = ", ".join([r.mention
                               for r
                               in srv.role_hierarchy
                               if r.name != "@everyone"
                               and r in user.roles])
        else:
            roles = None
        color = 000000
        if hasattr(user, 'color'):
            color = user.color
        data = discord.Embed(description=game and game or 'Not in server', colour=color)
        data.add_field(name="Joined Discord on", value=created_on)
        if user_joined and joined_on:
            data.add_field(name="Joined this server on", value=joined_on)
        if roles:
            data.add_field(name="Roles", value=roles, inline=False)
        if member_number:
            data.set_footer(text="Member #{} | User ID:{}"
                             "".format(member_number, user.id))
        else:
            data.set_footer(text="User ID: {}".format(user.id))

        name = str(user)
        if getattr(user, 'nick', None):
            name = " ~ ".join((name, getattr(user, 'nick')))

        if user.avatar_url:
            avatar = await self.helpers.get_avatar(user)
            data.set_author(name=name, url=avatar)

            data.set_thumbnail(url=avatar)
        else:
            data.set_author(name=name)

        try:
            await ctx.send(embed=data)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission to send this")

    @info.command(name='roles', no_pm=True, aliases=['role'])
    async def _roles(self, ctx, role=None):

        if not role:
            roles = ', '.join([r.mention for r in ctx.guild.role_hierarchy])
            e = await self.helpers.full_embed(roles)
            await ctx.send(embed=e)
            return
        else:
            role = await self.helpers.choose_role(ctx, ctx.guild, role)
        if not role:
            return
        e = await self.helpers.full_embed(
            '\n'.join([
                f'**ID**: {role.id} (position {role.position + 1})',
                f'**Name**: {role.mention} ({role.mentionable and "" or "not "}mentionable)',
                f'**Hoisted**: {role.hoist and "" or "not "} hoisted',
                f'**Created**: {role.created_at}',
                f'**Integration**: {role.managed}'
            ])
        )
        await ctx.send(f'Information about role: **{role}**', embed=e)

    @commands.command(pass_context=True, no_pm=True)
    async def avatar(self, ctx, user: str=None):
        author = ctx.message.author
        if not user:
            user = author
        elif not getattr(user, 'roles', None) and not user.isnumeric():
            try:
                user = await self.helpers.choose_member(ctx, ctx.guild, user)
            except:
                user = await self.bot.get_user_info(int(user[2:-1]))
        elif user.isnumeric():
            try:
                user = await self.bot.get_user_info(int(user))
            except:
                pass
        if not user:
            return
        avatar = await self.helpers.build_embed(f"{user}'s avatar", getattr(user, 'color', 000000))
        if user.avatar_url:
            avatar.set_image(url=await self.helpers.get_avatar(user))
        try:
            await ctx.send(embed=avatar)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission to post avatars here.")

    @info.command(name='server', pass_context=True, no_pm=True)
    async def _server(self, ctx):
        """Shows server's informations"""
        server = ctx.message.guild
        online = len([m.status for m in server.members
                      if m.status != discord.Status.offline])
        total_users = len(server.members)
        text_channels = len(server.text_channels)
        voice_channels = len(server.voice_channels)
        passed = (ctx.message.created_at - server.created_at).days
        created_at = ("Since {}. That's over {} days ago!"
                      "".format(server.created_at.strftime("%d %b %Y %H:%M"),
                                passed))

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)

        data = discord.Embed(
            description=created_at,
            colour=discord.Colour(value=colour))
        data.add_field(name="Region", value=str(server.region))
        data.add_field(name="Users", value="{}/{}".format(online, total_users))
        data.add_field(name="Text Channels", value=text_channels)
        data.add_field(name="Voice Channels", value=voice_channels)
        data.add_field(name="Roles", value=len(server.roles))
        data.add_field(name="Owner", value=str(server.owner))
        data.set_footer(text=f"Server ID: {server.id}")

        if server.icon_url:
            data.set_author(name=server.name, url=server.icon_url)
            data.set_thumbnail(url=server.icon_url)
        else:
            data.set_author(name=server.name)

        try:
            await ctx.send(embed=data)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission "
                               "to send this")

def setup(bot):
    cog = Information(bot)
    bot.add_cog(cog)
