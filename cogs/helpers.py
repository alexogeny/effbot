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

    async def spawn_config(self, kind):
        if kind == 'server':
            data = dict(
                log_moderation=0,
                log_messages=0,
                log_misc=0,
                log_join=0,
                log_leave=0,
                role_admin=0,
                bl_channels=[],
                bl_commands=[],
                role_moderator=0,
                role_curator=0,
                chan_quotes=0,
                chan_curated=[],
                chan_welcome=0,
                tt_timer=0,
                tt_when=0,
                chan_depart=0,
                chan_staff=0,
                tt_ms=0,
                tt_prestiges=0,
                tt_tcq=0,
                tt_code='',
                tt_pass=0,
                tt_gm=0,
                tt_master=0,
                tt_captain=0,
                tt_knight=0,
                tt_recruit=0,
                tt_applicant=0,
                tt_guest=0,
                tt_alumni=0,
                tt_inxtext='CQ {cq.number} in {cq.time}! Be ready!',
                tt_nowtext='CQ {cq.number} has spawned! Kill it!!!',
                tt_intervals=[60,5],
                welcome_text='Welcome **{{user.name}}** to **{guild.name}**!',
                depart_text='So long, **{{user.name}}**, and safe travels!',
                tt_timerperms=0,
                tt_recruitperms=0
            )
        elif kind == 'user':
            data = dict(
                tt_code='',
                tt_ms=0,
                tt_tcq=0,
                tt_prestiges=0,
                tt_taps=0,
                tt_playtime='',
                xp=0,
                level=0,
                weekly=0,
                last_reset='',
                currency=100,
                last_daily='',
                tree=0
            )
        st = await self.struct(data)
        return st


def setup(bot):
    cog = Helpers(bot)
    bot.add_cog(cog)
