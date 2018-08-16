import discord
import random
import time
import asyncio
from discord.ext import commands
from discord.errors import Forbidden
from random import choice, random
import re

emoji_exp = re.compile(r'<:[A-z0-9_]+:([0-9]+)>')
aemoji_exp = re.compile(r'<a:[A-z0-9_]+:([0-9]+)>')

class Fun():
    """Because who doesn't like to have fun?"""
    def __init__(self, bot):
        
        self.bot = bot
        

    @commands.group(pass_context=True, invoke_without_command=False)
    async def fun(self, ctx):
        pass

    @commands.command(name='mock')
    async def _mock(self, ctx, *, message):
        
        try:
            await ctx.message.delete()
        except Forbidden as e:
            asyncio.ensure_future(ctx.send('Oops, I cannot manage messages in this channel.'))
            return
        msgbuff = ""
        uppercount = 0
        lowercount = 0
        for c in message:
            if c.isalpha():
                if uppercount == 2:
                    uppercount = 0
                    upper = False
                    lowercount += 1
                elif lowercount == 2:
                    lowercount = 0
                    upper = True
                    uppercount += 1
                else:
                    upper = random() > 0.5
                    uppercount = uppercount + 1 if upper else 0
                    lowercount = lowercount + 1 if not upper else 0

                msgbuff += c.upper() if upper else c.lower()
            else:
                msgbuff += c

        asyncio.ensure_future(ctx.send(
            f'<:sponge_left:475979172372807680> {msgbuff} <:sponge_right:475979143964524544>'
        ))


    @commands.command(name='bae')
    async def _bae(self, ctx):
        if ctx.message.author.id != 321257293557792769:
            await ctx.send('Oh, you are not bae ...')
        else:
            await ctx.send('OMG, HI BAE!!')

    @commands.command(name='pleb')
    async def _pleb(self, ctx):
        if ctx.author.id != 254710997225308181:
            asyncio.ensure_future(ctx.send('You are not enough of a pleb to use this command :<'))
        else:
            asyncio.ensure_future(ctx.send('**Relajarse#0010** is the most pleb pleb I ever met, out of all the plebs >:D'))

    @commands.command(name='emote', aliases=['mote', 'e'])
    async def emote(self, ctx, emote: str):
        match = emoji_exp.search(emote.strip())

        if match:
            m = match.group()[1:-1].split(':')[2]
            m = f'{m}.png'
        else:
            match2 = aemoji_exp.search(emote.strip())
            m = match2.group()[2:-1].split(':')[2]
            m = f'{m}.gif?v=1'
        e= discord.Embed(description=None, colour=0xffffff)
        e.set_image(url=f'https://cdn.discordapp.com/emojis/{m}')
        e.image.width = 256
        e.image.height = 256
        await ctx.send(embed=e)

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
            'Not a chance, {}.',
            'Not on this earth, {}.',
            'When pigs fly, {}.',
            'When evo reaches MS cap, {}.',
            'When Bara finishes pumping his CoC, {}.'
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
