import discord
from discord.ext import commands
from datetime import datetime
import gzip
from json import dumps, loads
from copy import deepcopy
import asyncio
import time
from difflib import get_close_matches
import os
from collections import defaultdict
from playhouse.shortcuts import dict_to_model, model_to_dict


class Helpers():
    def __init__(self, bot):
        self.bot = bot
        self.last_save = int(time.time())

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

    async def timer_save(self):
        while self is self.bot.get_cog('Helpers'):
            if int(time.time()) - self.last_save >= 299:
                asyncio.ensure_future(self.save_records())
            await asyncio.sleep(300)

    async def save_records(self):
        for k in self.bot._models:
            records = [getattr(self.bot, f'_{k}s')]
            await self.upsert_records(records)

    async def upsert_records(self, records):
        model = records[0].__class__
        data_dicts = [model_to_dict(r) for r in records]
        with self.bot.db.atomic():
            for record in data_dicts:
                model.insert(**record).on_conflict(
                    preserve=[model.id, model.create_],
                    update=record
                )

    def load_records(self, models):
        setattr(self.bot, '_models', models)
        for k in models:
            result = [i for i in list(models[k].select())]
            setattr(self.bot, f'_{k}s', result)

    async def get_record(self, model, id):
        result = [x for x in getattr(self.bot,f'_{model}s') if x.id==id]
        if len(result) > 0:
            return result[0]
        else:
            valid = getattr(self.bot, f'_{model}s', None)
            if valid:
                result = valid[0].__class__(id=id)
                valid.append(result)
                return result

    async def get_obj(self, server, kind, key, value):
        result = [x for x in getattr(server, f'{kind}s')
                  if getattr(x, key)==value
                  or value.lower() in getattr(x, key).lower()]
        if result:
            return result[0].id
        else:
            return None

    async def search_for(self, items, term):
        return [items.index(x) for x in items if term in x]


    async def choose_from(self, ctx, choices, text):
        chooser = await ctx.send(text)
        def check(m):
            return m.content.isnumeric() or m.content.lower().strip() == 'c'
        try:
            msg = await self.bot.wait_for('message', check=check)
        except asyncio.TimeoutError as e:
            await chooser.delete()
            await msg.channel.send('Query timed out.')
            return
        else:
            await chooser.delete()
            if not msg.content.isnumeric():
                await msg.channel.send('Query cancelled.')
                return
            i = int(msg.content)-1
            if i > -1 and i < len(choices):
                return choices[i]
            else:
                await msg.channel.send('Query cancelled.')
                return

    async def choose_member(self, ctx, server, user: str):
        members = server.members
        result = await self.search_for([m.name.lower() for m in members], user.lower())
        if len(result) == 0:
            return None
        elif len(result) == 1:
            return members[result[0]]
        elif len(result) > 1:
            choices = [members[r] for r in result[0:10]]
            choicetext = "{}```\n{}\n-----\n{}```".format(
                'I found multiple users. Please reply with a matching number:',
                '\n'.join([f'{i+1} {c.name}#{c.discriminator}'
                for i, c in enumerate(choices)]),
                'Or, type "c" to cancel'
            )
            user = await self.choose_from(ctx, choices, choicetext)
            return user
    async def choose_channel(self, ctx, server, channel: str):
        channels = [c for c in server.text_channels if c not in server.categories]
        result = await self.search_for([m.name.lower() for m in channels], channel.lower())
        if len(result) == 0:
            return None
        elif len(result) == 1:
            return channels[result[0]]
        elif len(result) > 1:
            choices = [channels[r] for r in result[0:10]]
            choicetext = "{}```\n{}\n-----\n{}```".format(
                'I found multiple channels. Please reply with a matching number:',
                '\n'.join([f'{i+1} #{c.name}'
                for i, c in enumerate(choices)]),
                'Or, type "c" to cancel'
            )
            channel = await self.choose_from(ctx, choices, choicetext)
            return channel
    async def choose_role(self, ctx, server, role: str):
        roles = server.roles
        result = await self.search_for([m.name.lower() for m in roles], role.lower())
        if len(result) == 0:
            return None
        elif len(result) == 1:
            return roles[result[0]]
        elif len(result) > 1:
            choices = [roles[r] for r in result[0:10]]
            choicetext = "{}```\n{}\n-----\n{}```".format(
                'I found multiple roles. Please reply with a matching number:',
                '\n'.join([f'{i+1} @{c.name}'
                for i, c in enumerate(choices)]),
                'Or, type "c" to cancel'
            )
            role = await self.choose_from(ctx, choices, choicetext)
            return role



    @staticmethod
    def human_format(num):
        num = float(num)
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        # add more suffixes if you need them
        return '%.2f%s' % (num, ['', 'K', 'M', 'B', 'T'][magnitude])

    @staticmethod
    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    @staticmethod
    def ingest_timestring(string):
        return datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')

def setup(bot):
    cog = Helpers(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(cog.timer_save())
    bot.add_cog(cog)
