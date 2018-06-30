import sys, traceback
import discord
import json
import time
from pathlib import Path
from discord.ext import commands
from os import listdir
from os.path import isfile, join
from models import ServerTT2, Titanlord, UserTT2, db

class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

with Path('./config.json').open('r') as fh:
    CONFIG = json.load(fh)

def get_prefix(bot, message):
    prefixes = CONFIG['PREFIXES']
    if not message.guild:
        return '.'
    return commands.when_mentioned_or(*prefixes)(bot, message)

class Effribot(commands.Bot):
    """docstring for Effribot"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = CONFIG
        self.database = db
        self.start_time = time.time()
        self._last_exception = None
        self.description = "effrill3's custom bot"
        self.load_extensions()
        self.create_tables()
        self.add_models([ServerTT2, Titanlord, UserTT2])

    def load_extensions(self):
        for extension in [
            f.replace('.py', '') for f in listdir(self.config['COGS_DIR'])
            if isfile(join(self.config['COGS_DIR'], f))]:
            try:
                self.load_extension(f"{self.config['COGS_DIR']}.{extension}")
            except (discord.ClientException, ModuleNotFoundError) as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    def create_tables(self):
        if not Path('data').exists():
            Path('data').mkdir()
            import sqlite3
            with sqlite3.connect('data\\db.db') as conn:
                pass
        with self.database:
            self.database.create_tables([ServerTT2, Titanlord, UserTT2])
        return

    def add_models(self, models):
        # print(self.database.__dir__())
        self.models = Struct(**{str(model)[8:-1]: model for model in models})
        return

    async def on_ready(self):
        print(f'Logged in as {bot.user.name}')
        print('--------')

    async def on_command_error(self, ctx, error):
        channel = ctx.message.channel
        if isinstance(error, commands.CommandInvokeError):
            no_dms = "Cannot send messages to this user"
            is_help_cmd = ctx.command.qualified_name == "help"
            is_forbidden = isinstance(error.original, discord.Forbidden)
            if is_help_cmd and is_forbidden and error.original.text == no_dms:
                msg = ("I can't send messages to you. Either you blocked me or you disabled server DMs.")
                await ctx.bot.get_channel(462204160524288021).send(msg)

            message = (f"Error in command '{ctx.command.qualified_name}'. Traceback:\n")

            message += "".join(traceback.format_exception(type(error), error,
                                                      error.__traceback__))
            bot._last_exception = message
            await ctx.bot.get_channel(462204160524288021).send(inline(message[0:1950]))
        return self

    def run(self):
        token = self.config['TOKEN']
        try:
            super().run(token, bot=True, reconnect=True)
        except discord.errors.LoginFailure:
            print("failed to login to discord")

# bot = commands.Bot(command_prefix=get_prefix, description="Effrille's custom bot.")
# setattr(bot, 'config', CONFIG)
# setattr(bot, 'start_time', time.time())
# setattr(bot, '_last_exception', None)

def inline(text):
    return "```\n{}\n```".format(text)

bot = Effribot(command_prefix=get_prefix)
# bot.remove_command('help')
if __name__ == '__main__':
    bot.run()
