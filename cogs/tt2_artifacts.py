import discord
from datetime import datetime, timedelta
from discord.ext import commands
from string import ascii_lowercase
from itertools import chain, zip_longest
from random import choice
from math import log, log10, floor, ceil
from pathlib import Path
from collections import defaultdict
from csv import DictReader
import functools
import asyncio
import re
import datetime as dt
import time
UOT = 60
SCIFI = re.compile(r'^([^a-z]+)([A-Za-z]+)$')
LIFI = re.compile(r'^([0-9\.]+)[^0-9]+([0-9,]+)$')
TIME_SUCKER = re.compile(r'([0-9]+)([^0-9]+)?')
LETTERS = re.compile(r'^[wdhms]')
MAP = dict(w='weeks', d='days', h='hours', m='minutes', s='seconds')

async def base_relics_amount(stage: int) -> int:
    return (
        3 * pow(1.21, pow(stage, .48))
    ) + (
        1.5 * (stage-110)
    ) + (
        pow(1.002, pow(stage, min(
            (1.005*(pow(stage, 1.1*.0000005+1))), 1.0155
        )))
)

async def artifact_boost(level: int, per_level: int, cost_exponent: float, 
                         growth_rate, growth_max, growth_exponent) -> int:
    return round(1 + per_level * pow(level, pow(
        (1 + (cost_exponent - 1) * min(growth_rate * level, growth_max)),
        growth_exponent
        )
    ) + .5)

class TT2Artifacts():
    """docstring for TT2Artifacts"""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        self.game_version = 2.9
        self.artifacts = []
        _cwd = Path('..')
        _csv = next(_cwd.rglob('ArtifactInfo.csv'))
        with _csv.open('r') as fh:
            for r in DictReader(fh):
                d = dict(r)
                d2 = {
                    'id': int(d['ArtifactID'].replace('Artifact','')),
                    'max_level': int(d['MaxLevel']),
                    'effect': float(d['EffectPerLevel']),
                    'growth_max': float(d['GrowthMax']),
                    'growth_rate': float(d['GrowthRate']),
                    'growth_exponent': float(d['GrowthExpo']),
                    'damage_bonus': float(d['DamageBonus']),
                    'cost_coefficient': float(d['CostCoef']),
                    'cost_exponent': float(d['CostExpo']),
                    'name': d['Name'].title()
                }
                d2['acronym'] = ''.join([x[0] for x in d['Name'].upper().split()])
                self.artifacts.append(d2)
    
    @commands.group(name='artifacts', aliases=['art', 'artifact', 'arti'])
    async def _artifacts(self, ctx):
        pfx = await self.bot.get_prefix(ctx.message)
        mc = ctx.message.clean_content
        passed = 0
        while not passed:
            for p in pfx:
                if mc.startswith(p):
                    mc = mc[len(p):]
                    passed = 1
        if mc.strip() in ['art', 'artifact', 'arti', 'artifacts']:
            # list all the artifacts
            # print(self.artifacts)
            capped = '\n'.join([f':[]: {a["name"]}' for a in self.artifacts if a['max_level']>0])
            uncapped = '\n'.join([f':[]: {a["name"]}' for a in self.artifacts if a['max_level']==0])
            e = await self.helpers.full_embed('Full list of artifacts!', fields={
                'Capped': capped,
                'Uncapped': uncapped    
            })
            await ctx.send(embed=e)

def setup(bot):
    cog = TT2Artifacts(bot)
    bot.add_cog(cog)
