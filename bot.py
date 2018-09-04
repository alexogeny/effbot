import os
import re
import sys
import json
import time
import signal
import asyncio
import asyncpg
import discord
import traceback
import subprocess
from os import listdir
from models import get_db, Server, User, Titanlord
# from models import Server, User, db
from os.path import isfile, join
from pathlib import Path
from discord.ext import commands
# from playhouse.shortcuts import dict_to_model

# class Struct(object):
#     def __init__(self, **entries):
#         self.__dict__.update(entries)

if Path('./config.json').exists():
    with Path('./config.json').open('r') as fh:
        CONFIG = json.load(fh)
else:
    CONFIG = dict(PREFIXES=['e.', 'e!', 'e@', 'effbot '],
                  COGS_DIR="cogs",
                  TOKEN=os.getenv("TOKEN"),
                  MS=30000)

def get_prefix(bot, message):
    prefixes = CONFIG['PREFIXES']
    local_prefixes = prefixes+[bot.prefixes.get(str(message.guild.id),'.')]
    return commands.when_mentioned_or(*local_prefixes)(bot, message)

class Effribot(commands.Bot):
    """docstring for Effribot"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_command('help')
        self.config = CONFIG
        self.models = dict(server=Server, user=User, titanlord=Titanlord)
        self.start_time = time.time()
        self._last_exception = None
        self.description = "effrill3's custom bot"
        self.load_extensions()
        self.prefixes = {}

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

    async def add_custom_prefix(self, guild):
        g = await self.get_cog('Helpers').get_record('server', guild.id)
        self.prefixes[str(guild.id)]=g.get('prefix') or '.'
        return

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        print('--------')
        await self.get_cog('Helpers').update_timed_roles()
        print('Updated timed roles!')
        print('--------')
        await asyncio.gather(*[self.add_custom_prefix(guild) for guild in self.guilds])
        print('Initialised custom prefixes')
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
            
            e.add_field(name=f'Stack:', value=f'```python\n{tb[0:900]}\n```')
            
            await self.get_channel(466192124115681281).send(embed=e)
        return self

    async def on_guild_join(self, guild):
        await self.get_channel(462253601360969758).send(
            f'Joined guild **{guild.name}** ({guild.id})'
        )
        # if not [x for x in self._servers if x['id']==guild.id]:
        #     g = {'id': guild.id}
        #     gm = dict_to_model(Server, g)
        #     # conf = await self.cog['Helpers'].spawn_config('server')
        #     # g['config'] = conf
        #     self._servers.append(gm)
        #     asyncio.ensure_future(self.cogs['Helpers'].upsert_records([gm]))

    async def on_guild_remove(self, guild):
        await self.get_channel(462253601360969758).send(
            f'Left guild **{guild.name}** ({guild.id})'
        )

    def run(self):
        token = self.config.get('TOKEN', os.getenv('TOKEN'))
        try:
            super().run(token, bot=True, reconnect=True)
        except discord.errors.LoginFailure:
            print("failed to login to discord")


def inline(text):
    return "```\n{}\n```".format(text)

async def main():
    pool = await get_db()
    return pool
# bot = Effribot(command_prefix=get_prefix)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    pool = loop.run_until_complete(main())
    bot = Effribot(command_prefix=get_prefix, max_messages=20000, case_insensitive=True)
    setattr(bot, 'pool', pool)
    
    @bot.check
    async def globally_block_bots(ctx):
        return not ctx.author.bot

    bot.run()
