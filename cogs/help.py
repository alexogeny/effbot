import discord
import random
import re
import time
from discord.ext import commands
from random import choice

SPACE = re.compile(r'  +')

class Help():
    """A good start to get help from."""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
    
    @commands.command(name='help', no_pm=True, aliases=['helpme'])
    async def _help(self, ctx, command: str=None):
        cogs = [c for c in self.bot.cogs if c not in 'LogCog,TitanLord,Owner,Helpers,RandomStatus']
        if not command:
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
                    value=f'{c.__doc__}\n```\n{cxs}\n```',
                    inline=False
                )
            
            await ctx.send(embed=e)
        else:
            e = await self.helpers.build_embed(
                f'Help for command `{command}`', 0xffffff
            )
            c = self.bot.get_command(command.strip().lower())
            if c:
                # print(c.help)
                e.add_field(name='Name', value=c.name, inline=False)
                e.add_field(name='Help text', value=SPACE.sub(' ', c.help))
                await ctx.send(embed=e)

    @commands.command(name="support", no_pm=True, aliases=["server"])
    async def _support(self, ctx):
        embed = await self.helpers.build_embed('Get effbot support!', 0x36ce31)
        g = self.bot.get_guild(440785686438871040)
        embed.set_thumbnail(url=g.icon_url_as(format='jpeg'))
        #embed.set_author(name=f'Rank: {u.name}#{u.discriminator}', icon_url=u.avatar_url_as(format='jpeg'))
        #embed.add_field(name=m.guild.name, value=f'{rank_local+1}. **{xp_local}**xp')
        embed.add_field(name="Server Invite", value='[Click here](https://discord.gg/WvcryZW)')
        await ctx.send(embed=embed)
def setup(bot):
    cog = Help(bot)
    bot.add_cog(cog)
