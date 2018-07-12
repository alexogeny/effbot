import discord
import random
import time
from discord.ext import commands
from random import choice

class Information():
    """Get information about a user, the server, the bot, etc."""
    def __init__(self, bot):
        
        self.bot = bot
        

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
        await ctx.send(f"I've been online for `{int(w)}w : {int(d)}d : {int(h)}h : {int(m)}m : {int(s)}s`")

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
        await ping_msg.edit(content=f"***{ping:.0f}ms***")

    @info.command(name='bot', pass_context=True, no_pm=True)
    async def _bot(self, ctx):
        embed = discord.Embed(title='Effbot', description='A pretty useful bot, hopefully.')
        embed.add_field(name='Author', value='effrill3#0001')
        embed.add_field(name='User Count', value=f'{len(self.bot.users)}')
        embed.add_field(name='Server Count', value=f'{len(self.bot.guilds)}')
        embed.add_field(name='Invite', value='[Bot Invite Link](https://discordapp.com/api/oauth2/authorize?client_id=466854404965007360&permissions=2146954487&scope=bot)')
        await ctx.send(embed=embed)


    @info.command(name='user', pass_context=True, no_pm=True)
    async def _user(self, ctx, *, user: str=None):
        """Shows users's informations"""
        author = ctx.message.author
        server = ctx.message.guild

        if not user:
            user = author
        elif not hasattr(user, 'roles'):
            try:
                user = server.get_member(int(user[2:-1]))
            except:
                user = [n for n in server.members
                    if user.lower() in str(n.name).lower()
                    or user.lower() in str(n.nick).lower()]
            if isinstance(user, list) and len(user) >= 1:
                user = user[0]
                print(user)
            elif isinstance(user, list) and len(user) == 0:
                await ctx.send('I could not find that user. Try a different name or variation?')
                return
        roles = [x.name for x in user.roles if x.name != "@everyone"]

        joined_at = user.joined_at
        since_created = (ctx.message.created_at - user.created_at).days
        since_joined = (ctx.message.created_at - user.joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(server.members,
                               key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

        game = "Chilling in {} status".format(user.status)

        if user.activity is None:
            pass
        elif not hasattr(user.activity, 'url'):
            game = "{}".format(user.activity)
        else:
            game = "Streaming: [{}]({})".format(user.activity, user.activity.url)

        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                       if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"

        data = discord.Embed(description=game, colour=user.colour)
        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Joined this server on", value=joined_on)
        data.add_field(name="Roles", value=roles, inline=False)
        data.set_footer(text="Member #{} | User ID:{}"
                             "".format(member_number, user.id))

        name = str(user)
        name = " ~ ".join((name, user.nick)) if user.nick else name

        if user.avatar_url:
            data.set_author(name=name, url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name=name)

        try:
            await ctx.send(embed=data)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission to send this")

    @commands.command(pass_context=True, no_pm=True)
    async def avatar(self, ctx, *, user: str=None):
        author = ctx.message.author
        server = ctx.message.guild

        if not user:
            user = author
        elif not hasattr(user, 'roles'):
            try:
                user = server.get_member(int(user[2:-1]))
            except:
                user = [n for n in server.members
                    if user.lower() in str(n.name).lower()
                    or user.lower() in str(n.nick).lower()]
            if isinstance(user, list) and len(user) >= 1:
                user = user[0]
                print(user)
            elif isinstance(user, list) and len(user) == 0:
                await ctx.send('I could not find that user. Try a different name or variation?')
                return

        avatar = await self.bot.cogs['Helpers'].build_embed(f"{user.name}'s avatar", user.colour)
        #avatar = discord.Embed(description=f"{user.name}'s avatar", colour=user.colour,
        #                       url=user.avatar_url)
        avatar.set_image(url=str(user.avatar_url_as(format='jpeg')))

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
