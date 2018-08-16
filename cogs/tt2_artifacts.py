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


def artifact_map():
    return [
        dict(id=1, op='x', type='gold', acronym='hsh', name='Heroic Shield', effect='boss', emote=''),
        dict(id=2, op='^', type='multi', acronym='sotv', name='Stone of the Valrunes', effect='gold', emote=''),
        dict(id=3, op='-', type='mana', acronym='tac', name='The Arcana Cloak', effect='warcry', emote=''),
        dict(id=4, op='+', type='chance', acronym='aom', name='Axe of Muerte', effect='critical', emote=''),
        dict(id=5, op='+', type='chance', acronym='is', name='Invader\'s Shield', effect='fairy', emote=''),
        dict(id=6, op='+', type='damage', acronym='eoe', name='Elixir of Eden', effect='shadowclone', emote=''),
        dict(id=7, op='x', type='damage', acronym='pof', name='Parchment of Foresight', effect='warcry', emote=''),
        dict(id=8, op='-', type='mana', acronym='ho', name='Hunter\'s Ointment', effect='shadowclone', emote=''),
        dict(id=9, op='x', type='gold', acronym='lp', name='Labourer\'s Pendant', effect='handofmidas', emote=''),
        dict(id=10, op='x', type='damage', acronym='bor', name='Bringer of Ragnarok', effect='firesword', emote=''),
        dict(id=11, op='x', type='damage', acronym='tm', name='Titan\'s Mask', effect='heavenlystrike', emote=''),
        dict(id=12, op='+', type='duration', acronym='sg', name='Swamp Gauntlet', effect='shadowclone', emote=''),
        dict(id=13, op='+', type='duration', acronym='fs', name='Forbidden Scroll', effect='deadlystrike', emote=''),
        dict(id=14, op='+', type='duration', acronym='a', name='Aegis', effect='warcry', emote='warcry'),
        dict(id=15, op='+', type='duration', acronym='rof', name='Ring of Fealty', effect='handofmidas', emote=''),
        dict(id=16, op='+', type='duration', acronym='ga', name='Glacial Axe', effect='firesword', emote=''),
        dict(id=17, op='x', type='damage', acronym='hom', name='Helmet of Madness', effect='equipment', emote=''),
        dict(id=18, op='+', type='chance', acronym='eof', name='Egg of Fortune', effect='chesterson', emote=''),
        dict(id=19, op='x', type='gold', acronym='coc', name='Chest of Contentment', effect='chesterson', emote=''),
        dict(id=20, op='x', type='gold', acronym='bop', name='Book of Prophecy', effect='all', emote=''),
        dict(id=21, op='+', type='chance', acronym='dc', name='Divine Chalice', effect='x10gold', emote=''),
        dict(id=22, op='x', type='relics', acronym='bos', name='Book of Shadows', effect='relics', emote=''),
        dict(id=23, op='x', type='gold', acronym='tp', name='Titanium Plating', effect='equipment', emote=''),
        dict(id=24, op='-', type='cost', acronym='sor', name='Staff of Radiance', effect='hero', emote=''),
        dict(id=25, op='x', type='damage', acronym='bod', name='Blade of Damocles', effect='equipment', emote=''),
        dict(id=26, op='x', type='damage', acronym='hsw', name='Heavenly Sword', effect='artifact', emote=''),
        dict(id=27, op='-', type='mana', acronym='gok', name='Glove of Kuma', effect='deadlystrike', emote=''),
        dict(id=28, op='x', type='damage', acronym='ast', name='Amethyst Staff', effect='equipment', emote=''),
        dict(id=29, op='x', type='damage', acronym='dh', name='Drunken Hammer', effect='tap', emote=''),
        dict(id=30, op='x', type='damage', acronym='ie', name='Influential Elixir', effect='clanship', emote=''),
        dict(id=31, op='x', type='damage', acronym='dr', name='Divine Retribution', effect='all', emote=''),
        dict(id=32, op='x', type='damage', acronym='tsos', name='The Sword of Storms', effect='melee', emote=''),
        dict(id=33, op='x', type='damage', acronym='fb', name='Furies Bow', effect='range', emote=''),
        dict(id=34, op='x', type='damage', acronym='cota', name='Charm of the Ancient', effect='spell', emote=''),
        dict(id=35, op='x', type='damage', acronym='hb', name='Hero\'s Blade', effect='hero', emote=''),
        dict(id=36, op='-', type='mana', acronym='ip', name='Infinity Pendulum', effect='heavenlystrike', emote=''),
        dict(id=37, op='-', type='mana', acronym='os', name='Oak Staff', effect='firesword', emote=''),
        dict(id=38, op='x', type='damage', acronym='foe', name='Fruit of Eden', effect='pet', emote=''),
        dict(id=39, op='-', type='mana', acronym='tsp', name='Titan Spear', effect='handofmidas', emote=''),
        dict(id=40, op='^', type='multi', acronym='roc', name='Ring of Calisto', effect='equipment', emote=''),
        dict(id=41, op='x', type='damage', acronym='rt', name='Royal Toxin', effect='deadlystrike', emote=''),
        dict(id=42, op='x', type='damage', acronym='af', name='Avian Feather', effect='offline', emote=''),
        dict(id=43, op='x', type='gold', acronym='zk', name='Zakynthos Coin', effect='offline', emote=''),
        dict(id=44, op='x', type='gold', acronym='gfm', name='Great Fay Medallion', effect='fairy', emote=''),
        dict(id=45, op='x', type='gold', acronym='coe', name='Coins of Ebizu', effect='splash', emote=''),
        dict(id=46, op='%', type='damage', acronym='crh', name='Corrupted Rune Heart', effect='splash', emote=''),
        dict(id=47, op='^', type='multi', acronym='ig', name='Invader\'s Gjalarhorn', effect='allskill', emote=''),
        dict(id=48, op='+', type='duration', acronym='pt', name='Phantom Timepiece', effect='allskill', emote=''),
        dict(id=49, op='%', type='damage', acronym='tms', name='The Master\'s Sword', effect='tap', emote=''),
        dict(id=50, op='+', type='pool', acronym='ae', name='Ambrosia Elixir', effect='mana', emote=''),
        dict(id=51, op='x', type='damage', acronym='ss', name='Samosek Sword', effect='swordattack', emote=''),
        dict(id=52, op='^', type='multi', acronym='hos', name='Heart of Storms', effect='all', emote=''),
        dict(id=53, op='^', type='gold', acronym='ao', name='Apollo Orb', effect='all', emote=''),
        dict(id=54, op='+', type='chance', acronym='eotk', name='Essence of the Kitsune', effect='multispawn', emote=''),
        dict(id=55, op='x', type='damage', acronym='ds', name='Durendal Sword', effect='titan', emote=''),
        dict(id=56, op='x', type='damage', acronym='hsk', name='Helheim Skull', effect='boss', emote=''),
        dict(id=57, op='-', type='hp', acronym='asp', name='Aram Spear', effect='all', emote=''),
        dict(id=58, op='+', type='regen', acronym='MSt', name='Mystic Staff', effect='mana', emote=''),
        dict(id=59, op='x', type='damage', acronym='tr', name='The Retaliator', effect='critical', emote=''),
        dict(id=60, op='+', type='duration', acronym='wotd', name='Ward of the Darkness', effect='boss', emote=''),
        dict(id=61, op='x', type='damage', acronym='ttt', name='Tiny Titan Tree', effect='ground', emote=''),
        dict(id=62, op='x', type='damage', acronym='hoh', name='Helm of Hermes', effect='flying', emote=''),
        dict(id=63, op='-', type='cost', acronym='lkm', name='Lost King\'s Mask', effect='gold', emote=''),
        dict(id=64, op='x', type='damage', acronym='orc', name='O\'Ryan\'s Charm', effect='companion', emote=''),
        dict(id=65, op='-', type='cooldown', acronym='hoti', name='Hourglass of the Impatient', effect='allskill', emote=''),
        dict(id=66, op='^', type='multi', acronym='kb', name='Khrysos Bowl', effect='stealthgold', emote=''),
        dict(id=67, op='^', type='multi', acronym='eop', name='Earrings of Portarra', effect='stealthdamage', emote=''),
        dict(id=68, op='+', type='refund', acronym='mbos', name='Mystical Beans of Senzu', effect='mana', emote=''),
        dict(id=69, op='^', type='chance', acronym='lfoam', name='Lucky Foot of Al-Mi\'Raj', effect='all', emote=''),
        dict(id=70, op='+', type='chance', acronym='boh', name='Boots of Hermes', effect='special', emote=''),
        dict(id=71, op='^', type='damage', acronym='MSw', name='Morgelai Sword', effect='weapon', emote=''),
        dict(id=72, op='+', type='chance', acronym='op', name='Oberon Pendant', effect='special', emote=''),
        dict(id=73, op='x', type='damage', acronym='mb', name='Moonlight Bracelet', effect='equipment', emote=''),
        dict(id=74, op='+', type='chance', acronym='ug', name='Unbound Gauntlet', effect='special', emote=''),
        dict(id=75, op='^', type='multi', acronym='ob', name='Oath\'s Burden', effect='knight', emote=''),
        dict(id=76, op='^', type='multi', acronym='cotc', name='Crown of the Constellation', effect='warlord', emote=''),
        dict(id=77, op='^', type='multi', acronym='tsc', name='Titania\'s Sceptre', effect='sorcerer', emote=''),
        dict(id=78, op='^', type='multi', acronym='fg', name='Fagin\'s Grip', effect='stealth', emote=''),
    ]

def arti_op_map(op):
    return {'%': 1.4, '+': 1.45, '-': 1.3, '^': 2.43, 'x': 1.5}[op]

def arti_type_map(kind):
    return {'chance': 1.625, 'cooldown': 1.5, 'cost': 1.12, 'damage': 2.75, 'duration': 1.825,
            'gold': 1.775, 'hp': 1.125, 'mana': 1.45, 'multi': 3, 'pool': 1.125, 'refund': 1.2,
            'relics': 5, 'regen': 1.5}[kind]

def arti_effect_map(effect):
    return {'all': 3.775, 'allskill': 3, 'artifact': 2, 'boss': 2,
            'chesterson': 2.25, 'clanship': 2.25, 'companion': 3, 'critical': 2.825,
            'deadlystrike': 2, 'equipment': 3.175, 'fairy': 2.76, 'firesword': 2.5,
            'flying': 1.8, 'gold': 2.25, 'ground': 2, 'handofmidas': 2.55,
            'heavenlystrike': 3.55, 'hero': 1.875, 'knight': 2.875, 'mana': 2.5,
            'melee': 2, 'multispawn': 1.25, 'offline': 1.1875, 'pet': 1,
            'range': 2, 'relics': 5, 'shadowclone': 2.55, 'sorcerer': 2.875,
            'special': 4, 'spell': 2, 'splash': 1.625, 'stealth': 2.475, 
            'stealthdamage': 1.725, 'stealthgold': 1.725, 'swordattack': 2,
            'tap': 2, 'titan': 1, 'warcry': 2.5, 'warlord': 3, 'weapon': 1.25,
            'x10gold': 1.25}[effect]

def get_arti_tier(arti):
    raw = round(arti_op_map(arti['op'])*arti_type_map(arti['type'])*arti_effect_map(arti['effect']))
    if raw > 15:
        return 'A'
    elif raw > 8.5:
        return 'B'
    elif raw > 5.5:
        return 'C'
    elif raw > 3:
        return 'D'
    else:
        return 'E'


class TT2Artifacts():
    """docstring for TT2Artifacts"""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        self.game_version = 2.9
        self.artifacts = artifact_map()
        print('loaded artifacts')
        # self.artifacts = []
        # _cwd = Path('..')
        # _csv = next(_cwd.rglob('ArtifactInfo.csv'))
        # with _csv.open('r') as fh:
        #     for r in DictReader(fh):
        #         d = dict(r)
        #         d2 = {
        #             'id': int(d['ArtifactID'].replace('Artifact','')),
        #             'max_level': int(d['MaxLevel']),
        #             'effect': float(d['EffectPerLevel']),
        #             'growth_max': float(d['GrowthMax']),
        #             'growth_rate': float(d['GrowthRate']),
        #             'growth_exponent': float(d['GrowthExpo']),
        #             'damage_bonus': float(d['DamageBonus']),
        #             'cost_coefficient': float(d['CostCoef']),
        #             'cost_exponent': float(d['CostExpo']),
        #             'name': d['Name'].title()
        #         }
        #         d2['acronym'] = ''.join([x[0] for x in d['Name'].upper().split()])
        #         self.artifacts.append(d2)
    
    @commands.group(name='artifacts', aliases=['art', 'artifact', 'arti', 'arts'])
    async def _artifacts(self, ctx):
        # asyncio.ensure_future(ctx.send('hello'))
        # print('hi')
        pfx = await self.bot.get_prefix(ctx.message)
        mc = ctx.message.clean_content
        passed = 0
        while not passed:
            for p in pfx:
                if mc.startswith(p):
                    mc = mc[len(p):]
                    passed = 1
        if mc.strip() in ['art', 'artifact', 'arti', 'artifacts', 'arts']:
            for tier in 'A B C D E'.split():
                e = await self.helpers.full_embed(
                    '\n'.join(['<:sponge_right:475979143964524544> {} (**{}**) [{}]'.format(a['name'], a['acronym'].upper(), get_arti_tier(a)) for a in self.artifacts if get_arti_tier(a) == tier])
                )
                asyncio.ensure_future(ctx.send(
                    embed=e
                ))
            

    @_artifacts.command(name='tiers', aliases=['tierlist', 'tier'])
    async def _artifacts_tiers(self, ctx, tier=None):
        # print('tier list asked for')
        # asyncio.ensure_future(ctx.send('well i hope it might work'))
        if tier is None:
            for tier in 'A B C D E'.split():
                e = await self.helpers.full_embed(
                    '\n'.join(['<:sponge_right:475979143964524544> {} (**{}**) [{}]'.format(a['name'], a['acronym'].upper(), get_arti_tier(a)) for a in self.artifacts if get_arti_tier(a) == tier])
                )
                asyncio.ensure_future(ctx.send(
                    embed=e
                ))
        elif tier.upper() not in 'A B C D E'.split():
            asyncio.ensure_future(ctx.send('Not a valid tier! Valid tiers are: `A` `B` `C` `D` `E`'))
        else:
            tierlist = ['{} ({})'.format(a['name'], a['acronym']) for a in self.artifacts if get_arti_tier(a) == tier.upper()]
            e = await self.helpers.full_embed(
                '__List of **{}** tier artifacts__:\n\n{}'.format(
                    tier.upper(),
                    "\n".join(tierlist)
                )
            )
            asyncio.ensure_future(ctx.send(
                'The following list of artifacts was sorted into tiers by a totally "fine" algorithm:tm::',
                embed=e
            ))

def setup(bot):
    cog = TT2Artifacts(bot)
    bot.add_cog(cog)
