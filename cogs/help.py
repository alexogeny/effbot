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
                json.load(p.open('r', encoding='utf-8'))
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
        # print(locale.upper())
        file = next((x for x in self.posixes if f'.{locale}.json' in self.posixes[x]), None)
        # print(file)
        if file:
            # print(file)
            # print(self.mtimes)
            file = Path(self.posixes[file])
            if file.lstat().st_mtime > self.mtimes[locale]:
                self.locales[file.name.split('.')[1]] = BaseLocale(
                    file.name.split('.')[0],
                    file.name.split('.')[1],
                    json.load(file.open('r', encoding='utf-8'))
                )
        return self.locales.get(locale)




class Help():
    """A good start to get help from."""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        self.locales = LocaleGetter()
    
    @commands.command(name='help', no_pm=True, aliases=['helpme'])
    async def _help(self, ctx, module: str=None, command: str=None):
        g = await self.helpers.get_record('user', ctx.author.id)
        ulc = g.tt.get('locale', 'eng')
        lc = self.locales.get_locale(ulc)
        keys_, help_ = getattr(lc, "keys"), getattr(lc, "help")
        error_ = getattr(lc, "error")
        fields = {}
        if not module and not command:
            text = help_.get('help')
            name = 'help'
        elif module and not command and ulc=='eng':
            text = help_.get(module.lower().strip(), "No help text available.")
            name = f'{module}'
        elif module and command and ulc=='eng':
            text = help_.get(
                f"{module.lower().strip()} {command.lower().strip()}",
                "No help text available.")
            name = f'{module} {command}'
        elif module and not command and ulc!='eng':
            text = help_.get(module.lower().strip(), getattr(lc, "error"))
            name = f'{module}'
            if not help_.get(module.lower().strip()):
                lc = self.locales.get_locale('eng')
                help_ = getattr(lc, "help")
                fields.update({keys_['error']: text})
                text = help_.get(module.lower().strip())
        elif module and command and ulc!='eng':
            text = help_.get(
                f"{module.lower().strip()} {command.lower().strip()}",
                getattr(lc, "error"))
            name = f'{module} {command}'
            if not help_.get(module.lower().strip()):
                lc = self.locales.get_locale('eng')
                help_ = getattr(lc, module.lower().strip())
                fields.update({keys_['error']: text})
                text = help_.get(f"{module.lower().strip()} {command.lower().strip()}")
        if isinstance(text, dict) and text.get('refer to'):
            text = help_.get(text['refer to'])
        ff = lambda x, y: x in ['usage', 'example'] and f'```{y}```' or y
        related = [h for h in help_ if h.startswith(name) and h != name]
        if isinstance(text, dict):
            fields.update({
                keys_[k]:ff(k, v) for k,v in text.items()
                if k in ['description', 'requires', 'usage', 'example']
                and v
            })
        else:
            fields.update({keys_['error']: error_})
        if related:
            fields[keys_['related commands']] = '`{}`'.format('`, `'.join(related))
        e = await self.helpers.full_embed(
            f'{keys_["help text"]}: {name}', fields=fields, inline=False
        )
            
        asyncio.ensure_future(ctx.send(embed=e))

    @commands.command(name="support", no_pm=True, aliases=["server"])
    async def _support(self, ctx):
        embed = await self.helpers.build_embed('Get effbot support!', 0x36ce31)
        g = self.bot.get_guild(440785686438871040)
        embed.set_thumbnail(url=g.icon_url_as(format='jpeg'))
        embed.add_field(name="Server Invite", value='[Click here](https://discord.gg/WvcryZW)')
        await ctx.send(embed=embed)
def setup(bot):
    cog = Help(bot)
    bot.add_cog(cog)
