import sys, traceback
import discord
import json
import time
import asyncio
from pathlib import Path
from discord.ext import commands
from os import listdir
from os.path import isfile, join
from models import Server, User, db
import re
from playhouse.shortcuts import dict_to_model

class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

if Path('./config.json').exists():
    with Path('./config.json').open('r') as fh:
        CONFIG = json.load(fh)
else:
    CONFIG = dict(PREFIXES=['e.', '.', 'effbot '],
                  COGS_DIR="cogs",
                  TOKEN=None)

def get_prefix(bot, message):
    prefixes = CONFIG['PREFIXES']
    if isinstance(message.channel, discord.abc.PrivateChannel):
        return ['e.','.','?']
    return commands.when_mentioned_or(*prefixes)(bot, message)

class Effribot(commands.Bot):
    """docstring for Effribot"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_command('help')
        self.config = CONFIG
        self.database = db
        self.start_time = time.time()
        self._last_exception = None
        self.description = "effrill3's custom bot"
        self.load_extensions()
        self.create_tables()
        self._models = {}
        self.cogs['Helpers'].load_records(dict(
            server=Server, user=User))

    def load_extensions(self):
        self.load_extension('cogs.helpers')
        for extension in [
            f.replace('.py', '') for f in listdir(self.config['COGS_DIR'])
            if isfile(join(self.config['COGS_DIR'], f))]:
            try:
                self.load_extension(f"{self.config['COGS_DIR']}.{extension}")
            except (discord.ClientException, ModuleNotFoundError) as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    def create_tables(self):
        with self.database:
            self.database.create_tables([Server, User])
        return


    async def on_ready(self):
        print(f'Logged in as {bot.user.name}')
        print('--------')

    async def on_command_error(self, ctx, error):
        channel = ctx.message.channel
        if isinstance(error, commands.CommandInvokeError):
            no_dms = "Cannot send messages to this user"
            # is_help_cmd = ctx.command.qualified_name == "help"
            # is_forbidden = isinstance(error.original, discord.Forbidden)
            message = (f"Error in command '{ctx.command.qualified_name}'.")
            self._last_exception = message
            a = ctx.message.author
            g = ctx.message.guild
            e = await self.cogs['Helpers'].build_embed('Exception raised', 0xff0000)
            e.set_author(name=f'{g.name}', icon_url=g.icon_url_as(format='jpeg'))
            e.add_field(name="Command", value=f'{ctx.command.qualified_name}')
            e.add_field(name="User", value=f'{a.mention}', inline=False)
            
            tb = traceback.format_exception(type(error), error, error.__traceback__, limit=3)

            tb = "\n\n".join([re.sub(r'(C:(\\[^\\]+){1,4})', '', t).strip().replace(
                'venv\\lib\\site-packages', '...'
            ).replace(
                'The above exception was the direct cause of the following exception',
                'The above exception caused'
            ).replace(
                'Traceback (most recent call last):',
                ''
            ) for t in tb if t.strip()])
            
            e.add_field(name=f'Stack:', value=f'```python\n{tb[0:1023]}\n```')
            
            await self.get_channel(466192124115681281).send(embed=e)
        return self

    async def on_guild_join(self, guild):
        await self.get_channel(462253601360969758).send(
            f'Joined guild **{guild.name}** ({guild.id})'
        )
        if not [x for x in self._servers if x['id']==guild.id]:
            g = {'id': guild.id}
            gm = dict_to_model(Server, g)
            # conf = await self.cog['Helpers'].spawn_config('server')
            # g['config'] = conf
            self._servers.append(gm)
            asyncio.ensure_future(self.cogs['Helpers'].upsert_records([gm]))

    async def on_guild_remove(self, guild):
        await self.get_channel(462253601360969758).send(
            f'Left guild **{guild.name}** ({guild.id})'
        )

    def run(self):
        token = self.config.get('TOKEN', os.environ.get('TOKEN', ""))
        try:
            super().run(token, bot=True, reconnect=True)
        except discord.errors.LoginFailure:
            print("failed to login to discord")


def inline(text):
    return "```\n{}\n```".format(text)

bot = Effribot(command_prefix=get_prefix)
if __name__ == '__main__':
    bot.run()
