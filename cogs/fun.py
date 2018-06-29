import discord
import random
import time
from discord.ext import commands
from random import choice

class Fun():
    """docstring for Fun"""
    def __init__(self, bot):
        
        self.bot = bot
        

    @commands.group(pass_context=True, invoke_without_command=False)
    async def fun(self, ctx):
        pass

    @commands.command(name='8ball', alias=['8', '8b'])
    async def ball(self, ctx):
        """Gives a prediction."""
        answers = [
            'It is certain, {}.',
            'It is decidedly so, {}.',
            'Without a doubt, {}.',
            'Yes, definitely, {}.',
            'You may rely on it, {}.',
            'As I see it, yes, {}.',
            'Most likely, {}.',
            'Outlook good, {}.',
            'Yes, {}.',
            'All signs point to yes, {}.',
            'Better not tell you now, {}.',
            'Cannot predict now, {}.',
            'Concentrate and ask me again, {}.',
            'Don\'t count on it, {}.',
            'Solid maybe, {}.',
            'My sources say no, {}.',
            'Outlook not so good, {}.',
            'Doubtful, {}.',
            'Not a chance, {}.'
        ]
        embed = discord.Embed(
            description=choice(answers).format(f"**{ctx.author.name}**"),
            colour=0x222222
        )
        embed.set_footer(text='The magic 8ball', icon_url='https://i.imgur.com/9xim9Jd.png')
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission "
                               "to send this")
        
def setup(bot):
    cog = Fun(bot)
    bot.add_cog(cog)
