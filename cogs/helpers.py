import discord
from discord.ext import commands
from datetime import datetime
import gzip
from json import dumps, loads


class Struct:
    def __init__(self, data):
        if isinstance(data, bytes):
            data = loads(gzip.decompress(data).decode('utf-8'))
        for k, v in data.items():
            setattr(self, k, isinstance(v, dict) and self.__class__(v) or v)
    def __json__(self):
        output = {}
        for k, v in self.__dict__.items():
            output[k] = (isinstance(v, self.__class__) and v.__json__()) or v
        return output
    def as_string(self):
        return dumps(self.__json__(), separators=(',', ':'))
    def as_pretty(self):
        return '```json\n{}\n```'.format(dumps(self.__json__(), indent=4))
    def as_gzip(self):
        return gzip.compress(self.as_string().encode('utf-8'))


class Helpers():
    def __init__(self, bot):
        self.bot = bot

    async def build_embed(self, description, colour):
        embed = discord.Embed(
            description=description,
            colour=colour
        )
        embed.set_footer(
            text=f'{self.bot.user.name} - {datetime.utcnow()}',
            icon_url=self.bot.user.avatar_url_as(format='png')
        )
        return embed

    async def struct(self, data):
        return Struct(data)


def setup(bot):
    cog = Helpers(bot)
    bot.add_cog(cog)
