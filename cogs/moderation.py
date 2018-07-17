import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice

#REWRITE THIS
# def is_moderator_or_higher():
#     async def _is_moderator_or_higher(ctx):
#         msg = ctx.message
#         g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
#         #print([a.id for a in msg.author.roles])
#         u_roles = [a.id for a in msg.author.roles]
#         is_mod = g['config'].role_moderator in u_roles
#         is_admin = g['config'].role_admin in u_roles
#         if is_mod or is_admin:
#             return True
#         else:
#             await ctx.send('You need to be moderator+ to use this command.')
#             return False
#     return commands.check(_is_moderator_or_higher)


class ModerationCog():
    """Kick, ban, mute ... all the usual suspects."""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.cogs['Helpers']

    #REWRITE THIS
    # @is_moderator_or_higher()
    # @commands.command(no_pm=True, pass_context=True)
    # async def _kick(self, ctx, user: str, *, reason: str = None):
    #     """Kicks user."""
    #     author = ctx.message.author
    #     server = ctx.message.guild

    #     if not user:
    #         user = author
    #     elif not hasattr(user, 'roles'):
    #         try:
    #             user = server.get_member(int(user[2:-1]))
    #         except:
    #             user = [n for n in server.members
    #                 if user.lower() in str(n.name).lower()
    #                 or user.lower() in str(n.nick).lower()]
    #         if isinstance(user, list) and len(user) >= 1:
    #             user = user[0]
    #             print(user)
    #         elif isinstance(user, list) and len(user) == 0:
    #             await ctx.send('I could not find that user. Try a different name or variation?')
    #             return

    #     if author == user:
    #         await ctx.send("I cannot let you do that. Self-harm is "
    #                            "bad :pensive:")
    #         return

    #     try:
    #         await self.bot.kick(user)
    #         await ctx.send(":boot: User was kicked.")
    #     except discord.errors.Forbidden:
    #         await ctx.send("I'm not allowed to do that. Have a word to whomever"
    #                        "manages my ass.")

    

def setup(bot):
    cog = ModerationCog(bot)
    bot.add_cog(cog)
