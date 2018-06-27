import sys, traceback
import discord
import json
from pathlib import Path
from discord.ext import commands
from os import listdir
from os.path import isfile, join

with Path('./config.json').open('r') as fh:
    CONFIG = json.load(fh)


def get_prefix(bot, message):
    prefixes = CONFIG['PREFIXES']
    if not message.guild:
        return '.'
    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = commands.Bot(command_prefix=get_prefix, description="Effrille's custom bot.")
setattr(bot, 'config', CONFIG)



@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('--------')


bot.remove_command('help')
if __name__ == '__main__':
    for extension in [
        f.replace('.py', '') for f in listdir(bot.config['COGS_DIR'])
        if isfile(join(bot.config['COGS_DIR'], f))
    ]:
        try:
            bot.load_extension(f"{bot.config['COGS_DIR']}.{extension}")
        except (discord.ClientException, ModuleNotFoundError) as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()
bot.run(bot.config['TOKEN'], bot=True, reconnect=True)
