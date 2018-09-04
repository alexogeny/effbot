import discord
import random
import time
import asyncio
from discord.ext import commands
from discord.errors import Forbidden
from random import choice, random
from datetime import datetime
import re

emoji_exp = re.compile(r'<:[A-z0-9_]+:([0-9]+)>')
aemoji_exp = re.compile(r'<a:[A-z0-9_]+:([0-9]+)>')

class Fun():
    """Because who doesn't like to have fun?"""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        

    @commands.group(pass_context=True, invoke_without_command=False)
    async def fun(self, ctx):
        pass

    @commands.command(name='drjesus')
    async def _drjesus(self, ctx):
        choice_ = choice([
            "I'll give you a hint, it's not hard coded :)",
            'Praise the bear people!',
            'May the Dark Lord perish and all rejoice.',
            'We type with our eyes closed and then set the office on fire before we deploy.',
            'I mean this is programming, anything is possible',
            'I\'m flattered that there\'s a meme from me sir',
            'You could literally die mid tournament and would not be able to get to 3500.'

        ])
        asyncio.ensure_future(ctx.send(choice_))

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

    @commands.command(name='insert', hidden=True, visible=False)
    async def sttget(self, ctx, arg):
        if arg != 'coin':
            return
        try:
            guild = self.bot.get_guild(440785686438871040)
            member = guild.get_member(ctx.author.id)
        except:
            return
        else:
            res = [r for r in member.roles if r.id == 485057531102756876]
            if not res:
                role = [r for r in guild.roles if r.id == 485057531102756876][0]
                await member.add_roles(role)
                asyncio.ensure_future(ctx.send('I wonder what this does? Maybe check https://patreon.com/effrill3'))

    @commands.command(name='triforce')
    async def _triforce(self, ctx):
        if ctx.message.author.id == 283441304749342720:
            asyncio.ensure_future(ctx.send(
                'The legendary **triforce#8511** represents wisdom, courage, and power. Behold, the might!'
            ))
        else:
            import random
            choice = random.Random(int(ctx.author.id)).choice([1,2,3])
            choice = ['courage', 'power', 'wisdom'][choice-1]
            asyncio.ensure_future(ctx.send(
                f'The **triforce#8511** has spoken. Your affinity is: **{choice}**!'
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


    @commands.command(name='blame')
    async def _blame(self, ctx, user=None):
        if not user:
            return
        user = await self.helpers.choose_member(ctx, ctx.guild, user)
        if not user:
            await ctx.send('Err, who are you trying to blame? I could not find the user you asked for.')
            return
        if user.id == ctx.author.id and user.id != 259451392630980610:
            asyncio.ensure_future(ctx.send('I cannot let you blame yourself. Whatever it was, it wasn\'t your fault. :pensive:'))
            return
        
        author = await self.helpers.get_record('user', ctx.author.id)
        user = await self.helpers.get_record('user', user.id)

        now = datetime.utcnow().timestamp()
        last_blame = author['fun'].get('last_blame', 0)
        if now - last_blame >= 60:
            author['fun']['last_blame'] = now
        else:
            asyncio.ensure_future(ctx.send('You must wait an hour between casting blames! Shame on you!'))
            return

        if not user['fun'].get('blamed'):
            user['fun']['blamed']=0
        user['fun']['blamed']+=1
        await self.helpers.sql_update_record('user', user)
        mention = await self.bot.get_user_info(user['id'])
        msg = f'**{mention}** has been blamed **{user["fun"].get("blamed",0)}** time{user["fun"].get("blamed",0) > 1 and "s" or ""}!'
        if user['id'] != 259451392630980610:
            immo = await self.helpers.get_record('user', 259451392630980610)
            if not immo['fun'].get('blamed'):
                immo['fun']['blamed']=0
            immo['fun']['blamed']+=1
            user = immo
            await self.helpers.sql_update_record('user', user)

        asyncio.ensure_future(ctx.send(msg))
        await self.helpers.sql_update_record('user', author)

    @commands.command(name='blames')
    async def _blames(self, ctx, user=None):
        if not user:
            user = ctx.author
        else:
            user = await self.helpers.choose_member(ctx, ctx.guild, user)

        record = await self.helpers.get_record('user', user.id)
        msg = f'**{user}** has been blamed **{record["fun"].get("blamed",0)}** time{record["fun"].get("blamed", 0) > 1 and "s" or ""}!'

        asyncio.ensure_future(ctx.send(msg))




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
