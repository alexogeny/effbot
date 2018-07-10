import discord
import random
import time
from discord.ext import commands
from random import choice

class Help():
    """A good start to get help from."""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
    
    @commands.command(name='help', no_pm=True, aliases=['helpme'])
    async def _help(self, ctx, module: str=None, command: str=None):
        cogs = [c for c in self.bot.cogs if c not in 'LogCog,TitanLord,Owner,Helpers,RandomStatus']
        if not module and not command:
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
                # print([x.name for x in self.bot.get_cog_commands(cog)])
            # embed.set_thumbnail(url='https://i.imgur.com/1aAsAvW.png')
            # e.set_author(name='effbot help')
            
            await ctx.send(embed=e)

            # await ctx.send(cogs[0].commands)
            # await ctx.send(', '.join([c.name.lower() for c in cogs]))

def setup(bot):
    cog = Help(bot)
    bot.add_cog(cog)
