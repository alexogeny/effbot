import discord
import random
import re
import json
import time
import asyncio
from discord.ext import commands
from random import choice
from pathlib import Path
from importlib import import_module

SPACE = re.compile(r'  +')


class BaseLocale(object):
    def __init__(self, name, code, data):
        assert len(code.lower().strip()) == 3
        self.name = name
        self.code = code
        self.__dict__.update(data)

    def __repr__(self):
        return f'<Locale: {self.name} ({self.code})>'

class LocaleGetter(object):
    def __init__(self):
        self._cwd = Path('..')
        self._locales = [p for p in self._cwd.rglob('*.[a-z][a-z][a-z].json')]
        self.locales = {
            p.name.split('.')[1]: BaseLocale(
                p.name.split('.')[0],
                p.name.split('.')[1],
                json.load(p.open('r'))
            ) for p in self._locales
        }
        self.mtimes = {
            p.name.split('.')[1]: p.lstat().st_mtime
            for p in self._locales
        }
        self.posixes = {
            p.name.split('.')[1]: p.as_posix()
            for p in self._locales
        }
    
    def get_locale(self, locale):
        print(locale.upper())
        file = next((x for x in self.posixes if f'.{locale}.json' in self.posixes[x]), None)
        print(file)
        if file:
            # print(file)
            # print(self.mtimes)
            file = Path(self.posixes[file])
            if file.lstat().st_mtime > self.mtimes[locale]:
                self.locales[file.name.split('.')[1]] = BaseLocale(
                    file.name.split('.')[0],
                    file.name.split('.')[1],
                    json.load(file.open('r'))
                )
        return self.locales.get(locale)




class Help():
    """A good start to get help from."""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        self.locales = LocaleGetter()
        # print(self.locales.locales)
        # print(self.locales.posixes)
    
    @commands.command(name='help', no_pm=True, aliases=['helpme'])
    async def _help(self, ctx, module: str=None, command: str=None):
        # cogs = [c
        #         for c
        #         in self.bot.cogs
        #         if c not in 'LogCog,TitanLord,Owner,Helpers,RandomStatus']
        if not module and not command:
            text = getattr(self.locales.get_locale('eng'), "help")
        elif module and not command:
            text = getattr(self.locales.get_locale('eng'),
                           f"help {module}",
                           "No help text available.")
        elif module and command:
            text = getattr(self.locales.get_locale('eng'),
                           f"help {module} {command}",
                           "No help text available.")
        if text.startswith("refer to"):
            print(f"help {text[9:]}")
            text = getattr(self.locales.get_locale('eng'), f"help {text[9:]}",
                "No help text available.")
        e = await self.helpers.build_embed(
            text, 0xffffff
        )
            
        asyncio.ensure_future(ctx.send(embed=e))

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
