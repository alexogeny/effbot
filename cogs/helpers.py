import os
import re
import gzip
import time
import asyncio
import discord
import datetime as dt
from copy import deepcopy
from json import dumps, loads
from math import log, log10, floor
from uuid import uuid4
from pprint import pprint
from string import ascii_lowercase
from difflib import get_close_matches
from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict
from discord.ext import commands
from urllib.parse import urlparse
#from playhouse.shortcuts import dict_to_model, model_to_dict
TIME_SUCKER = re.compile(r'([0-9]+)([^0-9]+)?')
LETTERS = re.compile(r'^[wdhms]')
MAP = dict(w='weeks', d='days', h='hours', m='minutes', s='seconds')
PRIZE_ROTATOR = ['Weapons', 'SP & Perks', 'Shards & Eggs']

BONUS_ROTATOR = [
    '🧝‍♀️ 5x all hero dmg',
    '⚔ 8x melee dmg',
    '🏹 8x ranged dmg',
    '🧙‍♀️ 8x spell dmg',
    '👆 5x tap dmg',
    '🔮 +4 mana regen',
    '⚗ +200 mana pool',
    '🧚‍♀️ +100% x2 fairy chance',
    '💫 +40% crit chance',
    '🙅 None'
]

async def get_next_prize(days=1):
    now = datetime.utcnow()+timedelta(days=days+1)
    origin_date = datetime.utcfromtimestamp(1532242116.705826)
    weeks, remainder = divmod((now-origin_date).days, 3.5)
    tourneys = floor(weeks)+1
    prize = await rotate(PRIZE_ROTATOR, tourneys%3)
    bonus = await rotate(BONUS_ROTATOR, tourneys%10)
    return bonus[0], prize[0], now.strftime('%A'), now.strftime('%d %b, %Y')

async def tournament_forecast():
    result = []
    for i in range(14):
        item = await get_next_prize(days=i)
        if item not in result and item[2] in ['Sunday','Wednesday']:
            result.append(item)
    return [
        f'{r[2][0:3]}, **{r[3]}** | {r[1]}\n{r[0]}'
        for r
        in result[0:10]
    ]

async def rotate(table, mod):
    return table[mod:] + table [:mod]




async def role_in_list(role, role_list):
    return any([role_ for role_ in role_list if role_ == role])

async def any_roles_in_list(list_one, list_two):
    return any(await asyncio.gather(*[
        role_in_list(list_item, list_one) for list_item in list_two
    ]))

def has_any_role(*roles):
    async def _has_any_role(ctx):
        m, a, g = ctx.message, ctx.author, await ctx.bot.get_cog('Helpers').get_record('server',ctx.guild.id)
        user_roles = [r.id for r in a.roles]
        for role in roles:
            key, val = role.split('.')
            if g[key].get(val, None) in user_roles:
                return True
        asyncio.ensure_future(ctx.send('Sorry, you do not have permission.'))
        return False
    return commands.check(_has_any_role)

def role_exists(role):
    async def _role_exists(ctx):
        g = await ctx.bot.cogs['Helpers'].get_record('server', ctx.guild.id)
        key, value = role.split('.')
        result = g[key].get(value)
        if result:
            return True
        asyncio.ensure_future(ctx.send(f'No `{value}` role found.'))
        return False
    return commands.check(_role_exists)



class Helpers():
    def __init__(self, bot):
        self.bot = bot
        self.scifi = re.compile(r'^([^a-z]+)([A-Za-z]+)$')
        self.lifi = re.compile(r'^([0-9\.]+)[^0-9]+([0-9,]+)$')
        self.flagstr = 'https://s26.postimg.cc/{}.png'
        self.flags = {
            "afghanistan":"as5f0y0ax/flag-for-afghanistan_1f1e6-1f1eb",
            "aland-islands":"yj4sj287t/flag-for-aland-islands_1f1e6-1f1fd",
            "albania":"jzxnhnmsp/flag-for-albania_1f1e6-1f1f1",
            "algeria":"669asm1x5/flag-for-algeria_1f1e9-1f1ff",
            "american-samoa":"7lavhcaq1/flag-for-american-samoa_1f1e6-1f1f8",
            "andorra":"b4wt75l5l/flag-for-andorra_1f1e6-1f1e9",
            "angola":"as5f0zall/flag-for-angola_1f1e6-1f1f4",
            "anguilla":"fe1j9c3uh/flag-for-anguilla_1f1e6-1f1ee",
            "antarctica":"n6s71bhjd/flag-for-antarctica_1f1e6-1f1f6",
            "antigua-barbuda":"wekfi0wbd/flag-for-antigua-barbuda_1f1e6-1f1ec",
            "argentina":"pbck2eyll/flag-for-argentina_1f1e6-1f1f7",
            "armenia":"gt33y2zsp/flag-for-armenia_1f1e6-1f1f2",
            "aruba":"dm8kegn2h/flag-for-aruba_1f1e6-1f1fc",
            "ascension-island":"dyzyknd21/flag-for-ascension-island_1f1e6-1f1e8",
            "australia":"jaev5d6uh/flag-for-australia_1f1e6-1f1fa",
            "austria":"yj4sj588p/flag-for-austria_1f1e6-1f1f9",
            "azerbaijan":"xtm06sfex/flag-for-azerbaijan_1f1e6-1f1ff",
            "bahamas":"yj4sj5no9/flag-for-bahamas_1f1e7-1f1f8",
            "bahrain":"78jhb8sh5/flag-for-bahrain_1f1e7-1f1ed",
            "bangladesh":"9d3ucc1tl/flag-for-bangladesh_1f1e7-1f1e9",
            "barbados":"w1t1bwqx5/flag-for-barbados_1f1e7-1f1e7",
            "belarus":"b4wt790m1/flag-for-belarus_1f1e7-1f1fe",
            "belgium":"si73m43mx/flag-for-belgium_1f1e7-1f1ea",
            "belize":"669asqc8p/flag-for-belize_1f1e7-1f1ff",
            "benin":"tx8oauk5l/flag-for-benin_1f1e7-1f1ef",
            "bermuda":"3oxjlh7rt/flag-for-bermuda_1f1e7-1f1f2",
            "bhutan":"8atntu10p/flag-for-bhutan_1f1e7-1f1f9",
            "bolivia":"oyl5wc3i1/flag-for-bolivia_1f1e7-1f1f4",
            "bosnia-herzegovina":"53z4a7w09/flag-for-bosnia-herzegovina_1f1e7-1f1e6",
            "botswana":"afe0uxpsp/flag-for-botswana_1f1e7-1f1fc",
            "bouvet-island":"vca8zlvjd/flag-for-bouvet-island_1f1e7-1f1fb",
            "brazil":"8nl201lvd/flag-for-brazil_1f1e7-1f1f7",
            "british-indian-ocean-territory":"as5f14v7t/flag-for-british-indian-ocean-territory_1f1ee-1f1f4",
            "british-virgin-islands":"q0vcewwm1/flag-for-british-virgin-islands_1f1fb-1f1ec",
            "brunei":"n6s71h25l/flag-for-brunei_1f1e7-1f1f3",
            "bulgaria":"vca8zmy49/flag-for-bulgaria_1f1e7-1f1ec",
            "burkina-faso":"h5ui4euyx/flag-for-burkina-faso_1f1e7-1f1eb",
            "burundi":"m4i0iy6hl/flag-for-burundi_1f1e7-1f1ee",
            "cambodia":"kcp1o1uuh/flag-for-cambodia_1f1f0-1f1ed",
            "cameroon":"c76zpwebd/flag-for-cameroon_1f1e8-1f1f2",
            "canada":"xtm06xkll/flag-for-canada_1f1e8-1f1e6",
            "canary-islands":"yj4sjasux/flag-for-canary-islands_1f1ee-1f1e8",
            "cape-verde":"4r7q44drd/flag-for-cape-verde_1f1e8-1f1fb",
            "caribbean-netherlands":"r35ixikl5/flag-for-caribbean-netherlands_1f1e7-1f1f6",
            "cayman-islands":"78jhbed3d/flag-for-cayman-islands_1f1f0-1f1fe",
            "central-african-republic":"5thwmojq1/flag-for-central-african-republic_1f1e8-1f1eb",
            "ceuta-melilla":"n6s71jmqx/flag-for-ceuta-melilla_1f1ea-1f1e6",
            "chad":"g3kblxp15/flag-for-chad_1f1f9-1f1e9",
            "chile":"o92dk3kzt/flag-for-chile_1f1e8-1f1f1",
            "china":"umrgncxll/flag-for-china_1f1e8-1f1f3",
            "christmas-island":"6j0oz2muh/flag-for-christmas-island_1f1e8-1f1fd",
            "clipperton-island":"4r7q46b7d/flag-for-clipperton-island_1f1e8-1f1f5",
            "cocos-islands":"i84on1t8p/flag-for-cocos-islands_1f1e8-1f1e8",
            "colombia":"g3kblyzbt/flag-for-colombia_1f1e8-1f1f4",
            "comoros":"eoiqx95yh/flag-for-comoros_1f1f0-1f1f2",
            "congo-brazzaville":"53z4adoc9/flag-for-congo-brazzaville_1f1e8-1f1ec",
            "congo-kinshasa":"mu0svf9mx/flag-for-congo-kinshasa_1f1e8-1f1e9",
            "cook-islands":"mu0svfhcp/flag-for-cook-islands_1f1e8-1f1f0",
            "costa-rica":"ua02h8crt/flag-for-costa-rica_1f1e8-1f1f7",
            "cote-divoire":"si73mc14p/flag-for-cote-divoire_1f1e8-1f1ee",
            "croatia":"5gqigl96x/flag-for-croatia_1f1ed-1f1f7",
            "cuba":"rfwx3sxqx/flag-for-cuba_1f1e8-1f1fa",
            "curacao":"vp1n5zgft/flag-for-curacao_1f1e8-1f1fc",
            "cyprus":"l27u0kg09/flag-for-cyprus_1f1e8-1f1fe",
            "czech-republic":"m4i0j46jd/flag-for-czech-republic_1f1e8-1f1ff",
            "denmark":"i84on4t9l/flag-for-denmark_1f1e9-1f1f0",
            "diego-garcia":"wrbtoju49/flag-for-diego-garcia_1f1e9-1f1ec",
            "djibouti":"cwps2fmmh/flag-for-djibouti_1f1e9-1f1ef",
            "dominican-republic":"n6s71orxl/flag-for-dominican-republic_1f1e9-1f1f4",
            "dominica":"78jhbjpzt/flag-for-dominica_1f1e9-1f1f2",
            "ecuador":"qdmqlbk3d/flag-for-ecuador_1f1ea-1f1e8",
            "egypt":"53z4ahbih/flag-for-egypt_1f1ea-1f1ec",
            "el-salvador":"s5fpg8ivt/flag-for-el-salvador_1f1f8-1f1fb",
            "england_1f3f4-e0067-e0062-e0065-e006e":"41oxry84p/flag-for-england_1f3f4-e0067-e0062-e0065-e006e-e0067-e007f",
            "equatorial-guinea":"suyhslyux/flag-for-equatorial-guinea_1f1ec-1f1f6",
            "eritrea":"h5ui4nfm1/flag-for-eritrea_1f1ea-1f1f7",
            "estonia":"qdmqlcue1/flag-for-estonia_1f1ea-1f1ea",
            "ethiopia":"xtm075pt5/flag-for-ethiopia_1f1ea-1f1f9",
            "european-union":"5thwmvu2h/flag-for-european-union_1f1ea-1f1fa",
            "falkland-islands":"d9h68ophl/flag-for-falkland-islands_1f1eb-1f1f0",
            "faroe-islands":"vca8zwt21/flag-for-faroe-islands_1f1eb-1f1f4",
            "fiji":"41oxrzxux/flag-for-fiji_1f1eb-1f1ef",
            "finland":"4egby6nuh/flag-for-finland_1f1eb-1f1ee",
            "france":"9eds5jll5/flag-for-france_1f1eb-1f1f7",
            "french-guiana":"9r56bqbkp/flag-for-french-guiana_1f1ec-1f1eb",
            "french-polynesia":"6kams3yuh/flag-for-french-polynesia_1f1f5-1f1eb",
            "french-southern-territories":"9r56bqr09/flag-for-french-southern-territories_1f1f9-1f1eb",
            "gabon":"nktj0srbd/flag-for-gabon_1f1ec-1f1e6",
            "gambia":"9r56br6ft/flag-for-gambia_1f1ec-1f1f2",
            "georgia":"lg95zq549/flag-for-georgia_1f1ec-1f1ea",
            "germany":"4fq9r1zsp/flag-for-germany_1f1e9-1f1ea",
            "ghana":"ppdw1wnt5/flag-for-ghana_1f1ec-1f1ed",
            "gibraltar":"42yvkvwyh/flag-for-gibraltar_1f1ec-1f1ee",
            "greece":"kqqdndzft/flag-for-greece_1f1ec-1f1f7",
            "greenland":"8c3ln2fnd/flag-for-greenland_1f1ec-1f1f1",
            "grenada":"r4fgqnjrd/flag-for-grenada_1f1ec-1f1e9",
            "guadeloupe":"jog74v3rt/flag-for-guadeloupe_1f1ec-1f1f5",
            "guam":"im60mbso9/flag-for-guam_1f1ec-1f1fa",
            "guatemala":"i9emg5i49/flag-for-guatemala_1f1ec-1f1f9",
            "guernsey":"lt0k5ysjt/flag-for-guernsey_1f1ec-1f1ec",
            "guinea-bissau":"qewoeblsp/flag-for-guinea-bissau_1f1ec-1f1fc",
            "guinea":"k17lb2omh/flag-for-guinea_1f1ec-1f1f3",
            "guyana":"vqbkz1nax/flag-for-guyana_1f1ec-1f1fe",
            "haiti":"fs2v8x0sp/flag-for-haiti_1f1ed-1f1f9",
            "heard-mcdonald-islands":"67j8m1j6h/flag-for-heard-mcdonald-islands_1f1ed-1f1f2",
            "honduras":"67j8m1qw9/flag-for-honduras_1f1ed-1f1f3",
            "hong-kong":"91mdzi0s9/flag-for-hong-kong_1f1ed-1f1f0",
            "hungary":"3q7hesmfd/flag-for-hungary_1f1ed-1f1fa",
            "iceland":"ppdw20azd/flag-for-iceland_1f1ee-1f1f8",
            "india":"xuvy066y1/flag-for-india_1f1ee-1f1f3",
            "indonesia":"67j8m2th5/flag-for-indonesia_1f1ee-1f1e9",
            "iran":"6x20yg1qh/flag-for-iran_1f1ee-1f1f7",
            "iraq":"yx64iqcwp/flag-for-iraq_1f1ee-1f1f6",
            "ireland":"n824urtnt/flag-for-ireland_1f1ee-1f1ea",
            "isle-of-man":"epsoqfuux/flag-for-isle-of-man_1f1ee-1f1f2",
            "israel":"67j8m3w21/flag-for-israel_1f1ee-1f1f1",
            "italy":"rty9352c9/flag-for-italy_1f1ee-1f1f9",
            "jamaica":"7zc7h0uuh/flag-for-jamaica_1f1ef-1f1f2",
            "japan":"z9xioy5h5/flag-for-japan_1f1ef-1f1f5",
            "jersey":"91mdzkt3d/flag-for-jersey_1f1ef-1f1ea",
            "jordan":"4fq9r8fa1/flag-for-jordan_1f1ef-1f1f4",
            "kazakhstan":"l3hrtqhrd/flag-for-kazakhstan_1f1f0-1f1ff",
            "kenya":"55923lv95/flag-for-kenya_1f1f0-1f1ea",
            "kiribati":"i9emgav0p/flag-for-kiribati_1f1f0-1f1ee",
            "kosovo":"5i0g9ssyh/flag-for-kosovo_1f1fd-1f1f0",
            "kuwait":"m5rycavft/flag-for-kuwait_1f1f0-1f1fc",
            "kyrgyzstan":"3q7hewp15/flag-for-kyrgyzstan_1f1f0-1f1ec",
            "laos":"5urufzydl/flag-for-laos_1f1f1-1f1e6",
            "latvia":"hjvu3yx21/flag-for-latvia_1f1f1-1f1fb",
            "lebanon":"e09we6221/flag-for-lebanon_1f1f1-1f1e7",
            "lesotho":"7mktax4vt/flag-for-lesotho_1f1f1-1f1f8",
            "liberia":"5urug0t8p/flag-for-liberia_1f1f1-1f1f7",
            "libya":"tlr7y515l/flag-for-libya_1f1f1-1f1fe",
            "liechtenstein":"nktj12m95/flag-for-liechtenstein_1f1f1-1f1ee",
            "lithuania":"nktj12tyx/flag-for-lithuania_1f1f1-1f1f9",
            "luxembourg":"4fq9rbn0p/flag-for-luxembourg_1f1f1-1f1fa",
            "macau":"fs2v943fd/flag-for-macau_1f1f2-1f1f4",
            "macedonia":"4shnxikq1/flag-for-macedonia_1f1f2-1f1f0",
            "madagascar":"ppdw26qgp/flag-for-madagascar_1f1f2-1f1ec",
            "malawi":"5urug2iyx/flag-for-malawi_1f1f2-1f1fc",
            "malaysia":"v0ssmwryx/flag-for-malaysia_1f1f2-1f1fe",
            "maldives":"epsoqln6x/flag-for-maldives_1f1f2-1f1fb",
            "mali":"6kamsg6nt/flag-for-mali_1f1f2-1f1f1",
            "malta":"7mktazx6x/flag-for-malta_1f1f2-1f1f9",
            "marshall-islands":"l3hrtvf89/flag-for-marshall-islands_1f1f2-1f1ed",
            "martinique":"cxzpvpyp5/flag-for-martinique_1f1f2-1f1f6",
            "mauritania":"55923r0ft/flag-for-mauritania_1f1f2-1f1f7",
            "mauritius":"v0ssmy9zd/flag-for-mauritius_1f1f2-1f1fa",
            "mayotte":"dnii83me1/flag-for-mayotte_1f1fe-1f1f9",
            "mexico":"z9xip4so9/flag-for-mexico_1f1f2-1f1fd",
            "micronesia":"hwn8aa52x/flag-for-micronesia_1f1eb-1f1f2",
            "moldova":"l3hrtwx8p/flag-for-moldova_1f1f2-1f1e9",
            "monaco":"atfcuof2x/flag-for-monaco_1f1f2-1f1e8",
            "mongolia":"agnyoi4ix/flag-for-mongolia_1f1f2-1f1f3",
            "montenegro":"nktj174ah/flag-for-montenegro_1f1f2-1f1ea",
            "montserrat":"7zc7h9021/flag-for-montserrat_1f1f2-1f1f8",
            "morocco":"79tf4w789/flag-for-morocco_1f1f2-1f1e6",
            "mozambique":"w32z5jxyh/flag-for-mozambique_1f1f2-1f1ff",
            "myanmar":"ozv3py08p/flag-for-myanmar_1f1f2-1f1f2",
            "namibia":"7mktb3cnd/flag-for-namibia_1f1f3-1f1e6",
            "nauru":"b66r0wn2x/flag-for-nauru_1f1f3-1f1f7",
            "nepal":"x5d5o4bmx/flag-for-nepal_1f1f3-1f1f5",
            "netherlands":"r4fgr1wqh/flag-for-netherlands_1f1f3-1f1f1",
            "new-caledonia":"epsoqqcy1/flag-for-new-caledonia_1f1f3-1f1e8",
            "new-zealand":"mijcipqmx/flag-for-new-zealand_1f1f3-1f1ff",
            "nicaragua":"7zc7hb57t/flag-for-nicaragua_1f1f3-1f1ee",
            "nigeria":"pcmhw6fyh/flag-for-nigeria_1f1f3-1f1ec",
            "niger":"sjh1fssop/flag-for-niger_1f1f3-1f1ea",
            "niue":"q25a8jo7t/flag-for-niue_1f1f3-1f1fa",
            "norfolk-island":"y7nc6pk6h/flag-for-norfolk-island_1f1f3-1f1eb",
            "north-korea":"i9emgkxo9/flag-for-north-korea_1f1f0-1f1f5",
            "northern-mariana-islands":"y7nc6pzm1/flag-for-northern-mariana-islands_1f1f2-1f1f5",
            "norway":"vdk6ta55l/flag-for-norway_1f1f3-1f1f4",
            "oman":"4shnxqai1/flag-for-oman_1f1f4-1f1f2",
            "pakistan":"z9xipa5kp/flag-for-pakistan_1f1f5-1f1f0",
            "palau":"xi4judtxl/flag-for-palau_1f1f5-1f1fc",
            "palestinian-territories":"y7nc6r26x/flag-for-palestinian-territories_1f1f5-1f1f8",
            "panama":"5i0ga45wp/flag-for-panama_1f1f5-1f1e6",
            "papua-new-guinea":"h74fy34l5/flag-for-papua-new-guinea_1f1f5-1f1ec",
            "paraguay":"h74fy3cax/flag-for-paraguay_1f1f5-1f1fe",
            "peru":"pcmhw989l/flag-for-peru_1f1f5-1f1ea",
            "philippines":"tyim4m1ih/flag-for-philippines_1f1f5-1f1ed",
            "pitcairn-islands":"n824v6m2h/flag-for-pitcairn-islands_1f1f5-1f1f3",
            "poland":"dosg14qo9/flag-for-poland_1f1f5-1f1f1",
            "portugal":"6ybyrpb89/flag-for-portugal_1f1f5-1f1f9",
            "puerto-rico":"6lkklj0o9/flag-for-puerto-rico_1f1f5-1f1f7",
            "qatar":"6lkklj8e1/flag-for-qatar_1f1f6-1f1e6",
            "reunion":"4trlqmwqx/flag-for-reunion_1f1f7-1f1ea",
            "romania":"bk8302rmh/flag-for-romania_1f1f7-1f1f4",
            "russia":"eeb8dj1ih/flag-for-russia_1f1f7-1f1fa",
            "rwanda":"6ybyrqlix/flag-for-rwanda_1f1f7-1f1fc",
            "samoa":"bk8303ert/flag-for-samoa_1f1fc-1f1f8",
            "san-marino":"9fnpz0kux/flag-for-san-marino_1f1f8-1f1f2",
            "sao-tome-principe":"qg6m7p5m1/flag-for-sao-tome-principe_1f1f8-1f1f9",
            "saudi-arabia":"c9qvch2gp/flag-for-saudi-arabia_1f1f8-1f1e6",
            "scotland_1f3f4-e0067-e0062-e0073-e0063":"l4rpmzyyx/flag-for-scotland_1f3f4-e0067-e0062-e0073-e0063-e0074-e007f",
            "senegal":"5jae31uqh/flag-for-senegal_1f1f8-1f1f3",
            "serbia":"f3u0pxrs9/flag-for-serbia_1f1f7-1f1f8",
            "seychelles":"bwzh6bf21/flag-for-seychelles_1f1f8-1f1e8",
            "sierra-leone":"er2mjroy1/flag-for-sierra-leone_1f1f8-1f1f1",
            "singapore":"jcyqs4i6x/flag-for-singapore_1f1f8-1f1ec",
            "sint-maarten":"a56ibfiuh/flag-for-sint-maarten_1f1f8-1f1fd",
            "slovakia":"infyfrx2x/flag-for-slovakia_1f1f8-1f1f0",
            "slovenia":"7nur46edl/flag-for-slovenia_1f1f8-1f1ee",
            "solomon-islands":"56izwx26x/flag-for-solomon-islands_1f1f8-1f1e7",
            "somalia":"pdwfp87e1/flag-for-somalia_1f1f8-1f1f4",
            "south-africa":"ta9rl803d/flag-for-south-africa_1f1ff-1f1e6",
            "south-georgia-south-sandwich-islands":"luahzfk3t/flag-for-south-georgia-south-sandwich-islands_1f1ec-1f1f8",
            "south-korea":"bk83071y1/flag-for-south-korea_1f1f0-1f1f7",
            "south-sudan":"6ybyruo4p/flag-for-south-sudan_1f1f8-1f1f8",
            "spain":"kf8xaq661/flag-for-spain_1f1ea-1f1f8",
            "sri-lanka":"448tef1e1/flag-for-sri-lanka_1f1f1-1f1f0",
            "st-barthelemy":"ta9rl9ae1/flag-for-st-barthelemy_1f1e7-1f1f1",
            "st-helena":"rv86wjh0p/flag-for-st-helena_1f1f8-1f1ed",
            "st-kitts-nevis":"ks0bgxjax/flag-for-st-kitts-nevis_1f1f0-1f1f3",
            "st-lucia":"4trlqswsp/flag-for-st-lucia_1f1f1-1f1e8",
            "st-martin":"pdwfpak9l/flag-for-st-martin_1f1f2-1f1eb",
            "st-pierre-miquelon":"sxidf3up5/flag-for-st-pierre-miquelon_1f1f5-1f1f2",
            "st-vincent-grenadines":"6lkklq3ax/flag-for-st-vincent-grenadines_1f1fb-1f1e8",
            "sudan":"bwzh6fx3d/flag-for-sudan_1f1f8-1f1e9",
            "suriname":"sxidf4huh/flag-for-suriname_1f1f8-1f1f7",
            "svalbard-jan-mayen":"mjtabvko9/flag-for-svalbard-jan-mayen_1f1f8-1f1ef",
            "swaziland":"ahxwhqj5l/flag-for-swaziland_1f1f8-1f1ff",
            "sweden":"g6478mv7t/flag-for-sweden_1f1f8-1f1ea",
            "switzerland":"gvmzl03h5/flag-for-switzerland_1f1e8-1f1ed",
            "syria":"6ybyry3l5/flag-for-syria_1f1f8-1f1fe",
            "taiwan":"pdwfpcpfd/flag-for-taiwan_1f1f9-1f1fc",
            "tajikistan":"jcyqsaaix/flag-for-tajikistan_1f1f9-1f1ef",
            "tanzania":"ahxwhrtg9/flag-for-tanzania_1f1f9-1f1ff",
            "thailand":"r5pek9vxl/flag-for-thailand_1f1f9-1f1ed",
            "timor-leste":"wtvpb67zt/flag-for-timor-leste_1f1f9-1f1f1",
            "togo":"pqntvkaa1/flag-for-togo_1f1f9-1f1ec",
            "tokelau":"upbca3lsp/flag-for-tokelau_1f1f9-1f1f0",
            "tonga":"g6478p0dl/flag-for-tonga_1f1f9-1f1f4",
            "trinidad-tobago":"luahzlk5l/flag-for-trinidad-tobago_1f1f9-1f1f9",
            "tristan-da-cunha":"56izx44tl/flag-for-tristan-da-cunha_1f1f9-1f1e6",
            "tunisia":"ahxwhu6bt/flag-for-tunisia_1f1f9-1f1f3",
            "turkey":"9sf45hdi1/flag-for-turkey_1f1f9-1f1f7",
            "turkmenistan":"9fnpzbant/flag-for-turkmenistan_1f1f9-1f1f2",
            "turks-caicos-islands":"b7gou81qh/flag-for-turks-caicos-islands_1f1f9-1f1e8",
            "tuvalu":"56izx5ujt/flag-for-tuvalu_1f1f9-1f1fb",
            "uganda":"8ddjgsmpl/flag-for-uganda_1f1fa-1f1ec",
            "ukraine":"kf8xaybdl/flag-for-ukraine_1f1fa-1f1e6",
            "united-arab-emirates":"r5peke695/flag-for-united-arab-emirates_1f1e6-1f1ea",
            "united-kingdom":"n9c2oeszd/flag-for-united-kingdom_1f1ec-1f1e7",
            "united-nations":"f3u0q9cg9/flag-for-united-nations_1f1fa-1f1f3",
            "united-states":"3rhf8hqwp/flag-for-united-states_1f1fa-1f1f8",
            "uruguay":"luahzpuh5/flag-for-uruguay_1f1fa-1f1fe",
            "us-outlying-islands":"yyg2ceu8p/flag-for-us-outlying-islands_1f1fa-1f1f2",
            "us-virgin-islands":"xw5vtvj55/flag-for-us-virgin-islands_1f1fb-1f1ee",
            "uzbekistan":"obm9701ix/flag-for-uzbekistan_1f1fa-1f1ff",
            "vanuatu":"a56ibrydl/flag-for-vanuatu_1f1fb-1f1fa",
            "vatican-city":"ta9rljsh5/flag-for-vatican-city_1f1fb-1f1e6",
            "venezuela":"ftct2opvd/flag-for-venezuela_1f1fb-1f1ea",
            "vietnam":"nm3guo3k9/flag-for-vietnam_1f1fb-1f1f3",
            "wales":"ks0bh893t/flag-for-wales_1f3f4-e0067-e0062-e0077-e006c-e0073-e007f",
            "wallis-futuna":"448teqm21/flag-for-wallis-futuna_1f1fc-1f1eb",
            "western-sahara":"4trlr3ubd/flag-for-western-sahara_1f1ea-1f1ed",
            "yemen":"l4rpnfm8p/flag-for-yemen_1f1fe-1f1ea",
            "zambia":"yyg2chmjt/flag-for-zambia_1f1ff-1f1f2",
            "zimbabwe":"c9qvcxcvt/flag-for-zimbabwe_1f1ff-1f1fc"
            }


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

    async def tournament_time_remains(self):
        time, classifier = datetime.utcnow(), 'for another'
        date = datetime(time.year, time.month, time.day)
        due = date+timedelta(hours=23, minutes=55)
        if time.weekday() in [6,2] and time < due:
            weekday = time.strftime('%A')[0:3]
        else:
            classifier = 'in'
            today = date
            wkd = today.weekday()
            if wkd < 2:
                weekday, t = 'Wed', 2
            elif wkd < 6:
                weekday, t = 'Sun', 6
            due = date+timedelta((t-wkd) % 7)
        units = await self.mod_timedelta(due-time)
        #print(units)
        # h, m, s = map(lambda x: int(float(x)+.5), str(due-time).split(':'))
        mapped = await self.map_timedelta(units)
        remaining = ', '.join([f'{x} {y}' for x, y in mapped])
        # remaining = '`, `'.join()
        #remaining = str(due-time)
        
        return '{} `{}`'.format(classifier, remaining)

    async def full_embed(self, description, colour=0, thumbnail=None,
                         fields={}, author={}, inline=True):
        e = await self.build_embed(description, colour)
        for field in fields:
            e.add_field(name=field, value=fields[field], inline=inline)
        if author:
            e.set_author(name=author['name'], icon_url=author['image'])
        if thumbnail:
            e.set_thumbnail(url=thumbnail)
        return e

    async def member_number(self, member, guild):
        return sorted(guild.members, key=lambda m: m.joined_at).index(member) + 1

    async def try_mention(self, ctx, key, role):
        was_true = False
        try:
            if role.mentionable == True:
                was_true = True
                await role.edit(mentionable=False)
            await ctx.send(f'Set the {key} setting to {role.mention}!')
            if was_true:
                await role.edit(mentionable=True)
        except discord.Forbidden:
            await ctx.send(f'Set the `{key}` setting to `{role.name}`!')

    async def rotate(self, table, mod):
        return table[int(max(0, table%mod))]

    async def is_plural(self, number):
        return floor(number) > 1 or floor(number) == 0 or floor(number) < -1
    async def round_to_x(self, x, n):
        return round(x, -int(floor(log10(x))) + (n - 1))
    async def boss_hitpoints(self, level: int) -> int:
        return round(100000*pow(level, pow(level, .028))+.5)
    async def advance_start(self, level: int) -> float:
        return round(100*min(.003*pow(log(level+4),2.741), .9), 2)
    async def clan_damage(self, level: int) -> float:
        return round(pow(1.0233, level) + pow(level, 1.05), 2)

    async def mod_timedelta(self, time):
        current = time.total_seconds()
        hours, r = divmod(current, 3600)
        minutes, seconds = divmod(r, 60)
        return list(map(floor, (hours or 0, minutes or 0, seconds or 0)))

    async def map_timedelta(self, modded_time):
        keys = ['hour', 'minute', 'second']
        result = [
            (x, '{}{}'.format(keys[i], (await self.is_plural(x) and 's') or ''))
            for i, x in enumerate(modded_time)
        ]
        print(result)
        return result

    async def channel_exists(self, channel):
        return bool(self.bot.get_channel(channel))

    async def tl_has_settings(self, tl, c=('next', 'message', 'channel')):
        return all(tl.get(x) for x in c) and await self.channel_exists(tl.get(c[-1], 0))

    async def update_tls(self):
        titanlords = await self.sql_query_db(
            "SELECT * FROM titanlord"
        )
        await asyncio.gather(*[self.update_tl(dict(tl))
                               for tl
                               in titanlords
                               if await self.tl_has_settings(dict(tl))])

    async def get_tl_time_string(self, tl, kind='timer'):
        now, next_boss = datetime.utcnow(), tl['next']
        seconds_until_tl = (next_boss-now).total_seconds()
        H, M, S = await self.mod_timedelta(next_boss-now)
        boss_spawn = await self.get_spawn_string(tl.get('tz', 0), next_boss)
        params = dict(
            TIME='**{:02}:{:02}:{:02}**'.format(H, M, S),
            SPAWN=boss_spawn, ROUND=0, CQ=tl.get('cq_number', 1),
            GROUP=tl.get('group', 'Clan'))
        text = tl.get(kind).format(**params)
        return text


    async def update_tl(self, tl):
        chan, msg = None, None
        chan = self.bot.get_channel(tl['channel'])
        
        now, next_boss = datetime.utcnow(), tl['next']
        seconds_until_tl = (next_boss-now).total_seconds()
        H, M, S = await self.mod_timedelta(next_boss-now)
        is_not_final = seconds_until_tl > 10
        round_ping = tl.get('message') in range(1, 13) and tl.get('message') or 0
        boss_spawn = await self.get_spawn_string(tl.get('tz') or 0, next_boss)
        
        params = dict(
            TIME='**{:02}:{:02}:{:02}**'.format(H, M, S),
            SPAWN=boss_spawn, ROUND=1, CQ=tl.get('cq_number', 1),
            GROUP=tl.get('group', 'Clan'))
        
        ping_intervals = [p*60 for p in tl.get('ping_at', [15,5,1])]
        text_type, action, last_ping = 'timer', 'edit', tl.get('pinged_at')
        if is_not_final and seconds_until_tl <= max(ping_intervals) and not round_ping:
            text_type = 'ping'
        elif not is_not_final and not round_ping:
            text_type = 'now'
            action = 'send'
        elif round_ping and -seconds_until_tl//3600>=round_ping:
            tl['message'] = round_ping+1
            params['ROUND'] = round_ping+1
            action = 'send'
            text_type = 'round'
        elif not is_not_final:
            action = 'pass'

        text = tl.get(text_type).format(**params)
        
        if text_type != 'now' and action != 'pass':
            will_ping = await self.will_tl_ping(ping_intervals, seconds_until_tl, last_ping)
            if will_ping:
                action, tl['pinged_at'] = 'send', seconds_until_tl
        elif text_type == 'now':
            tl['cq_number'] += 1
            tl['pinged_at'] = 0
        
        if action == 'edit':
            mx = None
            try:
                mx = await chan.get_message(tl['message'])
            except:
                mx = await chan.send(txt)
                action = 'send'
                tl.update({'message': mx.id})
            else:   
                asyncio.ensure_future(mx.edit(content=text))
        elif action == 'send' and text_type != 'now' and text_type != 'round':
            # if tl.get('message') > 1:
            # m = await chan.get_message(tl['message'])
            # await m.delete()
            mx = await chan.send(text)
            tl.update({'message': mx.id})
        elif action == 'send' and text_type == 'now':
            await asyncio.sleep(seconds_until_tl)
            asyncio.ensure_future(chan.send(text))
            tl.update({'message': 1})
        elif action == 'send' and text_type == 'round':
            asyncio.ensure_future(chan.send(text))
        
        if await self.tl_has_settings(tl, c=('when_message', 'when_channel')):
            when_channel = self.bot.get_channel(tl['when_channel'])
            try:
                mx = await when_channel.get_message(tl['when_message'])
            except:
                tl.update({'when_message': 0})
            else:
                if is_not_final:
                    text = tl['timer'].format(**params)
                else:
                    text = 'Boss spawned!'
                    tl.update({'when_message': 0})
                asyncio.ensure_future(mx.edit(content=text))

        if action == 'send':
            asyncio.ensure_future(self.sql_update_record('titanlord', tl))

    async def will_tl_ping(self, intervals, seconds_until_tl, last_ping):
        filtered = next((p for p in intervals[::-1] if p > seconds_until_tl), 3660)
        if last_ping > filtered:
            return True
        return False

    async def process_time(self, input_time: str) -> timedelta:
        matches = re.match(r'(?:(?:(?P<hours>\d{1,2})[:.h])?(?P<minutes>\d{1,2})[:.m])?(?P<seconds>\d{1,2})', input_time)
        mgroups = {k: v and int(v) or 0 for k, v in matches.groupdict().items()}
        return (timedelta(**mgroups), {unit: value or 0 for unit, value in mgroups.items()})


    async def clear_tl(self, tl):
        tl.update({'next': 0, 'message': 0, 'when_message': 0})
        await self.sql_update_record('titanlord', tl)

    async def get_spawn_string(self, timezone, next_boss):
        boss_spawn = next_boss+timedelta(seconds=timezone*60*60)
        if timezone > 0:
            timezone = '+{}'.format(timezone)
        return boss_spawn.strftime('%H:%M:%S UTC{}').format(timezone or '')

    async def sql_query_db(self, statement, parameters=None):
        result = None
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                if parameters is not None:
                    result = await connection.execute(statement, *parameters)
                elif ' WHERE ' in statement:
                    result = await connection.fetchrow(statement)
                else:
                    result = await connection.fetch(statement)
        return result

    async def get_record(self, model, id):
        result = await self.sql_get_or_create_record(model, id)
        return result

    async def sql_update_key(self, kind, id, key, subkey, value):
        g = await self.get_record(kind, id)
        g[key][subkey] = value
        await self.sql_update_record(kind, g)
        return

    async def sql_filter_key(self, kind, key, subkey, value):
        collection = await self.sql_query_db(f'SELECT * FROM "{kind}"')
        collection = [dict(c) for c in collection]
        # print(collection[0:5])
        return any(c for c in collection if c[key].get(subkey)==value)

    async def sql_insert(self, table, data_dict):
        keys = ', '.join(f'"{m}"' for m in data_dict.keys())
        values = ', '.join(f'${i+1}' for i,x in enumerate(data_dict.values()))
        await self.sql_query_db(
            f'INSERT INTO "{table}" ({keys}) VALUES ({values}) ON CONFLICT (id) DO NOTHING',
            parameters=tuple(data_dict.values())
        )
        return

    async def sql_select(self, table, id):
        result = await self.sql_query_db(f'SELECT * FROM "{table}" WHERE id = {id}')
        return result

    async def sql_get_or_create_record(self, kind, id):
        model = self.bot.models.get(kind).default_factory()
        model.update(id=id)
        await self.sql_insert(kind, model)
        record = await self.sql_select(kind, id)
        return dict(record)

    async def sql_update_record(self, kind, data):
        id = data['id']
        model = self.bot.models.get(kind).default_factory()
        model.update(data)
        model.update({'update': datetime.utcnow()})
        keys = ', '.join(f'"{m}"' for m in model.keys())
        values = ', '.join(f'${i+1}' for i,x in enumerate(model.values()))
        result = await self.sql_query_db(
            f'UPDATE "{kind}" SET({keys}) = ({values}) WHERE id = {id}',
            parameters=tuple(model.values()),
        )
        return result


    async def search_for(self, items, term):
        return [items.index(x) for x in items if term in x]

    async def choose_from(self, ctx, choices, text, timeout=10):
        counter = datetime.utcnow().timestamp()+timeout
        chooser = await ctx.send(text)
        while True:
            if datetime.utcnow().timestamp() >= counter:
                break 

            def check(m):
                return m.content.isnumeric() or m.content.lower().strip() == 'c'
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=1.0)
            except asyncio.TimeoutError:
                continue
            else:
                if not msg.author.id == ctx.author.id:
                    continue
                is_author = msg.author.id == ctx.author.id
                if is_author:
                    if msg.content == 'c':
                        await chooser.delete()
                        await msg.channel.send('Query cancelled.')
                        return
                    i = int(msg.content)-1
                    if i > -1 and i < len(choices):
                        await chooser.delete()
                        return choices[i]
                    else:
                        await msg.channel.send('Query cancelled.')
                        return
        await chooser.delete()
        await ctx.channel.send('Query timed out.')

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
        if channel.startswith('<#') and channel.endswith('>'):
            channel = channel.replace('<#', '').replace('>', '')
        elif channel.startswith('#'):
            channel = channel.replace('#', '')
        if channel.isnumeric():
            try:
                channel = self.bot.get_channel(int(channel))
            except:
                pass
            else:
                return channel
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

    async def get_avatar(self, user):
        avatar=user.avatar_url_as(static_format='png')
        if user.is_avatar_animated():
            r = urlparse(user.avatar_url_as(format='gif'))
            avatar=str(f'{r.scheme}://{r.netloc}{r.path}')
        return avatar

    async def choose_conversion(self, number):
        if self.lifi.match(number):
            return 0
        elif self.scifi.match(number):
            return 1
        return 2

    async def from_scientific(self, number):
        number, notation = self.lifi.findall(number)[0]
        notation = int(notation.replace(',',''))-15
        modulo = notation % 3
        exponent = notation / 3
        output = []
        while exponent > 26:
            result, remainder = divmod(exponent, 26)
            output.append(remainder)
            exponent = result
        output.append(exponent)
        multiple = pow(10, modulo)
        l = len(output)
        if l > 2:
            output = [x for x in output[:-(l-2)]]+[max(x-1, 0) for x in output[-(l-2):]]
        last_result = ''.join([ascii_lowercase[int(last)] for last in output[::-1]])
        if len(last_result) == 1:
            last_result = 'a' + last_result
        return '{}{}'.format(int(float(number)*multiple), last_result)
    async def to_scientific(self, number):
        number, letter = self.scifi.findall(number)[0]
        map_to_alpha = [ascii_lowercase.index(x) for x in letter.lower()]
        a_to_one = [x+1 for x in map_to_alpha[:-2]]+map_to_alpha[-2:]
        dict_map = dict(enumerate(a_to_one))
        map_to_alpha = [pow(26, x) for x in  list(dict_map.keys())[::-1]]
        result = sum([x*a_to_one[i] for i, x in enumerate(map_to_alpha)])
        magnitude = int(log10(float(number)))
        number = float(number)/max((pow(10,magnitude)),1)
        return '{}e{:,}'.format(number, result*3+15+magnitude)

    async def humanize_decimal(self, decimal):
        bos = str(Decimal(decimal))
        if len(bos) < 15:
            bos = self.human_format(bos)
        else:
            x = bos[1:]
            dec = bos[1:3]
            bos = bos[0]
            bos = bos+'.'+dec+ 'e' + str(len(x))
        return bos

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
    # loop = asyncio.get_event_loop()
    # loop.create_task(cog.timer_save())
    bot.add_cog(cog)
