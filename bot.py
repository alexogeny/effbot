import sys, traceback
import discord
import json
import time
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
setattr(bot, 'start_time', time.time())
setattr(bot, '_last_exception', None)

def inline(text):
    return "```\n{}\n```".format(text)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print('--------')

@bot.event
async def on_command_error(ctx, error):
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
        await ctx.bot.get_channel(462204160524288021).send(inline(message))
    return bot
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
