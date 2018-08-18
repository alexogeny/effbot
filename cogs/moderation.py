import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice
from .helpers import has_any_role, has_role, is_admin

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
class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f'{ctx.author} (ID: {ctx.author.id}): {argument}'

        if len(ret) > 512:
            reason_max = 512
            asyncio.ensure_future(ctx.send(f'❎ Reason is too long ({len(argument)}/{reason_max})'))
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret


class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            asyncio.ensure_future(ctx.send('❎ Member not in ban list.'))
            raise commands.BadArgument("Not a valid previously-banned member.")
        return entity

class ModerationCog():
    """Kick, ban, mute ... all the usual suspects."""
    def __init__(self, bot):
        
        self.bot = bot
        self.helpers = self.bot.cogs['Helpers']

    @commands.command(no_pm=True)
    @has_any_role('roles.admin', 'roles.moderator')
    async def kick(self, ctx, member, *, reason: ActionReason=None):
        g = await self.helpers.get_record('server', ctx.guild.id)
        if not g['roles'].get('moderator'):
            asyncio.ensure_future(ctx.send('❎ No moderator role set!'))
            return
        member = await self.helpers.choose_member(ctx, ctx.guild, member)
        print(ctx.guild.role_hierarchy.index(member.top_role))
        print(ctx.guild.role_hierarchy.index(ctx.author.top_role))
        if not member:
            asyncio.ensure_future(ctx.send('❎ Could not find member in guild.'))
            return
        elif member == ctx.author or member.id == ctx.author.id:
            asyncio.ensure_future(ctx.send('❎ I cannot let you kick yourself.'))
            return
        elif ctx.guild.role_hierarchy.index(member.top_role) <= ctx.guild.role_hierarchy.index(ctx.author.top_role):
            asyncio.ensure_future(ctx.send('❎ You can only kick people lower than yourself in the role list.'))
            return
        if reason is None:
            reason = 'not set'
        reason = reason.replace('|', '-')
        await member.kick(reason=f'{ctx.author.id}|kick|{reason}')
        
        if not g['channels'].get('staff'):
            deliver = ctx.send
        else:
            deliver = self.bot.get_channel(g['channels']['staff']).send

        asyncio.ensure_future(deliver(
            f'✅ **{member}** was **kicked** by **{ctx.author}**'
        ))

    @commands.command(no_pm=True)
    @has_any_role('roles.admin', 'roles.moderator')
    async def ban(self, ctx, member, *, reason: ActionReason=None):
        g = await self.helpers.get_record('server', ctx.guild.id)
        if not g['roles'].get('moderator'):
            asyncio.ensure_future(ctx.send('❎ No moderator role set!'))
            return
        # print(member.split('#')) and not (len(member.split('#'))==2 and member[-4:].isnumeric())
        if not member.isnumeric():
            member = await self.helpers.choose_member(ctx, ctx.guild, member)
        else:
            member = await self.bot.get_user_info(int(member))
        if not member:
            asyncio.ensure_future(ctx.send('❎ Could not find member in guild.'))
            return
        elif member == ctx.author or member.id == ctx.author.id:
            asyncio.ensure_future(ctx.send('❎ I cannot let you ban yourself.'))
            return
        elif hasattr(member, 'top_role') and ctx.guild.role_hierarchy.index(member.top_role) <= ctx.guild.role_hierarchy.index(ctx.author.top_role):
            asyncio.ensure_future(ctx.send('❎ You can only ban people lower than yourself in the role list.'))
            return
        if reason is None:
            reason = 'not set'
        reason = reason.replace('|', '-')
        await ctx.guild.ban(member, reason=f'{ctx.author.id}|ban|{reason}', delete_message_days=0)
        
        if not g['channels'].get('staff'):
            deliver = ctx.send
        else:
            deliver = self.bot.get_channel(g['channels']['staff']).send

        asyncio.ensure_future(deliver(
            f'✅ **{member}** was **banned** by **{ctx.author}**'
        ))

    @commands.command(no_pm=True)
    @has_any_role('roles.admin', 'roles.moderator')
    async def unban(self, ctx, member: BannedMember, *, reason: ActionReason=None):
        g = await self.helpers.get_record('server', ctx.guild.id)
        if not g['roles'].get('moderator'):
            asyncio.ensure_future(ctx.send('❎ No moderator role set!'))
            return
        if reason is None:
            reason = 'not set'
        reason = reason.replace('|', '-')
        await ctx.guild.unban(member.user, reason=f'{ctx.author}|unban|{reason}')

        if not g['channels'].get('staff'):
            deliver = ctx.send
        else:
            deliver = self.bot.get_channel(g['channels']['staff']).send

        asyncio.ensure_future(deliver(
            f'✅ **{member.user}** was **unbanned** by **{ctx.author}**'
        ))

    @commands.command(no_pm=True)
    @has_any_role('roles.admin', 'roles.moderator')
    async def nickname(self, ctx, member, nickname, *, reason: ActionReason=None):
        g = await self.helpers.get_record('server', ctx.guild.id)
        if not g['roles'].get('moderator'):
            asyncio.ensure_future(ctx.send('❎ No moderator role set!'))
            return
        if not member.isnumeric():
            member = await self.helpers.choose_member(ctx, ctx.guild, member)
        else:
            member = ctx.guild.get_member(int(member))
        if not member:
            asyncio.ensure_future(ctx.send('❎ Could not find member in guild.'))
            return
        elif member == ctx.author or member.id == ctx.author.id:
            asyncio.ensure_future(ctx.send('❎ I cannot let you rename yourself.'))
            return
        elif hasattr(member, 'top_role') and ctx.guild.role_hierarchy.index(member.top_role) <= ctx.guild.role_hierarchy.index(ctx.author.top_role):
            asyncio.ensure_future(ctx.send('❎ You can only rename people lower than yourself in the role list.'))
            return
        if reason is None:
            reason = 'no reason'
        if not g['channels'].get('staff'):
            deliver = ctx.send
        else:
            deliver = self.bot.get_channel(g['channels']['staff']).send

        asyncio.ensure_future(deliver(
            f'✅ **{member.display_name}** (**{member}**) was **renamed** to **{nickname[0:29]}** by **{ctx.author}**'
        ))

        await member.edit(nick = nickname[0:29])


def setup(bot):
    cog = ModerationCog(bot)
    bot.add_cog(cog)
