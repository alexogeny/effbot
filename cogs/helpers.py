import discord
from discord.ext import commands
from datetime import datetime


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
            icon_url=self.bot.user.avatar_url_as(format='jpg')
        )
        return embed


def setup(bot):
    cog = Helpers(bot)
    bot.add_cog(cog)
