import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice
from decimal import Decimal
from string import ascii_lowercase, digits
from math import floor


def is_owner():
    async def _is_owner(ctx):
        return ctx.author.id == 305879281580638228
    return commands.check(_is_owner)

def is_admin_or_owner():
    async def _is_admin_or_owner(ctx):
        msg = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        if g.roles.get('admin') in [a.id for a in msg.author.roles]:
            return True
        elif ctx.author.id == 305879281580638228:
            return True
        elif msg.author.id == msg.guild.owner_id:
            return True
        elif g.roles.get('admin') not in [a.id for a in msg.author.roles]:
            await ctx.send('You need to be a server admin to do that.')
            return False
    return commands.check(_is_admin_or_owner)

class SettingsCog():
    """Set up server roles, configure logging, welcome messages, and so on."""
    def __init__(self, bot):
        self.bot = bot
        self.helpers = self.bot.get_cog('Helpers')
        self.flags = self.helpers.flags
        self.flagstr = self.helpers.flagstr

    @commands.group(name="my", pass_context=True)
    async def my(self, ctx):
        pass

    @my.command(name='country')
    async def _country(self, ctx, *country):
        msg = None
        if not country:
            msg = 'Did you forget to supply a country?'
        else:
            country = '-'.join(country).lower()
            countries = list(self.flags.keys())
            c=next((c for c in countries if c.startswith(country.lower())), None)
            if c:
                a = ctx.author
                await self.helpers.sql_update_key('user', a.id, 'tt', 'country', c)
                msg = f'Set the country for {a.name}#{a.discriminator} to {c}'
            else:
                msg = 'Could not find that country.'
        asyncio.ensure_future(ctx.send(msg))

    @my.command(name="language", aliases=["locale", "lang"])
    async def _language(self, ctx, language_code=None):
        available_locales = '`{}`'.format('`, `'.join(
            self.bot.get_cog('Help').locales.locales.keys()
        ))
        if not language_code:
            asyncio.ensure_future(ctx.send(f'Available Languages: {available_locales}'))
            return
        lc = language_code.lower().strip()
        if lc in available_locales:
            a = ctx.author
            await self.helpers.sql_update_key('user', a.id, 'tt', 'locale', lc)
            asyncio.ensure_future(ctx.send(f'Set your locale to: `{lc}`'))
        else:
            asyncio.ensure_future(ctx.send(
                f'Sorry, but `{lc}` is not an available locale.\nAvailable locales: {available_locales}'))
    
    @my.command(name='ms', aliases=['maxstage'])
    async def _ms(self, ctx, ms="1"):
        k = ms.endswith('k') and 1000 or 1
        try:
            float(ms[:-1])
        except:
            asyncio.ensure_future(ctx.send('You must submit a whole number.'))
            return
        a = ctx.author
        ms = k == 1 and int(ms) or int(float(ms[:-1])*k)
        g = await self.helpers.get_record('user', a.id)
        ms_cap = self.bot.config['MS']
        msg = None
        if ms <= g['tt'].get('ms', 0):
            msg = ('You cannot lower your MS. If you need it reset,'
                ' join the support server: `.support`')
        elif ms > ms_cap:
            msg = f'You cannot set your MS over the current cap: `{ms_cap:,}`'
        else:
            await self.helpers.sql_update_key('user', a.id, 'tt', 'ms', ms)
            msg = f'Successfully updated MS to `{ms:,}`!'
        asyncio.ensure_future(ctx.send(msg))

    @my.command(name='tcq', aliases=['cq'])
    async def _tcq(self, ctx, tcq="1"):
        k = tcq.endswith('k') and 1000 or 1
        try:
            float(tcq[:-1])
        except:
            asyncio.ensure_future(ctx.send('You must submit a whole number.'))
            return
        a = ctx.author
        tcq = k == 1 and int(tcq) or int(float(tcq[:-1])*k)
        g = await self.helpers.get_record('user', a.id)
        if tcq <= g['tt'].get('tcq', 0):
            asyncio.ensure_future(ctx.send(
                'You can only ever set your TCQ higher than previous. If you'
                ' need it reset, join the support server: `.support`'
            ))
        else:
            await self.helpers.sql_update_key('user', a.id, 'tt', 'tcq', tcq)
            asyncio.ensure_future(ctx.send(f'Successfully updated TCQ to `{tcq:,}`!'))


    @my.command(name='ign')
    async def _ign(self, ctx, *ign):
        if not ign:
            return
        ign = ' '.join(ign)
        if len(ign) > 16:
            asyncio.ensure_future(ctx.send('IGNs are less than 17 characters long.'))
            return
        if ign:
            a = ctx.author
            await self.helpers.sql_update_key('user', a.id, 'tt', 'ign', ign.strip())
            asyncio.ensure_future(ctx.send(
                f'Set the IGN for **{a.name}#{a.discriminator}** to **{ign}**'
            ))

    async def _normalize_number(self, ctx, number):
        if not number.isnumeric():
            mode = await self.helpers.choose_conversion(number)
            if mode == 2:
                asyncio.ensure_future(ctx.send(
                    'I could not recognise your input as a number. :<'
                ))
                return None
            elif number[-1].lower() in 'mbtk' and number[-2].isnumeric():
                try:
                    float(number[:-1])
                except:
                    return None
                else:
                    number = Decimal(float(number[:-1])*pow(
                        10,{'m':6,'k':3,'b':9,'t':12}[number[-1].lower()]
                    ))
            elif mode == 1:
                n = await self.helpers.to_scientific(number)
                number = Decimal(b.replace(',', ''))
            elif mode == 0:
                number = Decimal(number)
            return number

    @my.command(name='bos', aliases=['bookofshadows'])
    async def _bos(self, ctx, bos):
        o = bos
        a = ctx.author
        bos = await self._normalize_number(ctx, bos)
        if bos:
            await self.helpers.sql_update_key('user', a.id, 'tt', 'bos', int(bos))
            asyncio.ensure_future(ctx.send(
                f'Set {a.name}#{a.discriminator}\'s BoS level to {o}'
            ))

    @my.command(name='ltr', aliases=['lifetimerelics'])
    async def _ltr(self, ctx, ltr):
        o = ltr
        ltr = await self._normalize_number(ctx, ltr)
        a = ctx.author
        if ltr:
            await self.helpers.sql_update_key('user', a.id, 'tt', 'ltr', int(ltr))
            asyncio.ensure_future(ctx.send(
                f'Set {a.name}#{a.discriminator}\'s lifetime relics to {o}'
            ))

    @commands.command(name='tt2')
    async def tt2(self, ctx, user=None):
        a = ctx.author
        if not user:
            user = await self.helpers.get_record('user', a.id)
        elif not user.isnumeric():
            a = await self.helpers.choose_member(ctx, ctx.guild, user)
            user = await self.helpers.get_record('user', a.id)
        elif user.isnumeric():
            return
        e = await self.tt2_card(a, user)
        asyncio.ensure_future(ctx.send(embed=e))

    async def humanize_decimal(self, decimal):
        bos = str(Decimal(decimal))
        if len(bos) < 15:
            bos = self.helpers.human_format(bos)
        else:
            x = bos[1:]
            dec = bos[1:3]
            bos = bos[0]
            bos = bos+'.'+dec+ 'e' + str(len(x))
        return bos
    async def tt2_card(self, a, u):
        
        avatar = await self.helpers.get_avatar(a)
        ms = u['tt'].get('ms', 1)
        tcq = u['tt'].get('tcq', 1)
        bos = await self.humanize_decimal(u['tt'].get('bos', 1))
        ltr = await self.humanize_decimal(u['tt'].get('ltr', 1))
        shr = u['tt'].get('shortcode', '')
        clan = await self.helpers.sql_query_db("SELECT * FROM server")
        clan = next((c['tt'].get('name') for c in clan if c['tt'].get('shortcode')==shr), 'no clan set')
        # clan = next((s.tt.get('name') for s in self.bot._servers if s.tt.get('shortcode')==shr), 'no clan set')
        final = f"Clan: **{clan}**\nMax Stage: **{ms:,}**\nTotal Clan Quests: **{tcq:,}**\nBook of Shadows: **{bos}**\nLifetime Relics: **{ltr}**"
        e = await self.helpers.full_embed(final,
            thumbnail=avatar,
            author=dict(name=f'{u["tt"].get("ign", a.name)} ({a.name}#{a.discriminator})',
                        image=self.flagstr.format(self.flags[u['tt'].get('country', 'united-states')]))
        )
        return e

    @my.command(name='clan')
    async def _clan(self, ctx, clan=None):
        if not clan or not clan.isalnum() or not len(clan) < 6:
            asyncio.ensure_future(ctx.send(
                'Clan shortcodes must be letters or numbers and less than 6 characters. e.g. `T2RC`'
            ))
        else:
            exists = await self.helpers.sql_filter_key('server', 'tt', 'shortcode', clan.upper())
            if exists:
                a = ctx.author
                await self.helpers.sql_update_key('user', a.id, 'tt', 'shortcode', clan.upper())
                asyncio.ensure_future(ctx.send(f'Set the shortcode for {a.name}#{a.discriminator} to: `{clan.upper()}`'))

    @my.command(name='supportcode', aliases=['sc', 'code'])
    async def _code(self, ctx, code=None):
        if not code or not isinstance(code, str):
            asyncio.ensure_future(ctx.send('You need to supply a code.'))
        elif isinstance(code, str) and len(code) < 4 or len(code) > 10:
            asyncio.ensure_future(ctx.send('Support codes are between 5 and 10 characters long.'))
        elif isinstance(code, str) and not all([x in ascii_lowercase+digits for x in code]):
            asyncio.ensure_future(ctx.send(f'Valid characters for support codes are: {ascii_lowercase+digits}'))
        else:
            used = await self.helpers.sql_filter_key('user', 'tt', 'code', code)
            if used:
                asyncio.ensure_future(ctx.send(
                    'Somebody has already used that code. If this was not you,'
                    ' use the `verify` command.'
                ))
            else:
                a = ctx.author
                result = None
                g = await self.helpers.get_record('user', a.id)
                if not g['tt'].get('code'):
                    result = await self.helpers.choose_from(ctx, ['confirm'],
                        f'This will set your code to {code}. Type 1 to confirm or `c` to cancel.')
                else:
                    c = g['tt']['code']
                    result = await self.helpers.choose_from(ctx, ['confirm'],
                        f'This will override your code from `{c}` to `{code}`. Type 1 to confirm or `c` to cancel.')

                if result:
                    await self.helpers.sql_update_key('user', a.id, 'tt', 'code', code)
                    asyncio.ensure_future(ctx.send(
                        f'Set the support code for **{a.name}#{a.discriminator}**!'))

    @is_owner()
    @my.command(name='set', hidden=True, visible=False)
    async def _setcode(self, ctx, key, value, user):

        u = await self.helpers.choose_member(ctx, ctx.guild, user)
        # m = await self.helpers.get_record('user', u.id)
        if value.isnumeric():
            value = int(value)
        # m['tt'][key]=value
        await self.helpers.sql_update_key('user', u.id, 'tt', key, value)
        asyncio.ensure_future(ctx.send('Success!'))

    @commands.group(pass_context=True, name="settings")
    async def settings(self, ctx):
        pass

    @settings.command(pass_context=True)
    @is_admin_or_owner()
    async def set(self, ctx, setting: str=None, value: str=None):
        guild_id = ctx.message.guild.id
        key = setting.lower().strip()
        msg = ctx.message
        g = await self.helpers.get_record('server', msg.guild.id)
        
        if key.replace('role', '')=='admin' and msg.author.id in [msg.guild.owner_id, 305879281580638228]:
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            key = key.replace('role', '')
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            if not result:
                asyncio.ensure_future(ctx.send('No roles found!'))
                return
            g.roles[key]=result.id
            asyncio.ensure_future(self.helpers.try_mention(ctx, f'`{key}` role', result))
            
        elif key.replace('role','') in ['moderator', 'curator', 'grandmaster', 'updates', 'auto', 'dj']:
            key = key.replace('role', '')
            result = await self.helpers.choose_role(ctx, msg.guild, value)
            if not result:
                asyncio.ensure_future(ctx.send('No roles found!'))
                return
            g.roles[key]=result.id
            asyncio.ensure_future(self.helpers.try_mention(ctx, f'{key} role', result))
            return

        elif key.replace('text', '') in ['welcome']:
            pfx = await self.bot.get_prefix(ctx.message)
            mc = ctx.message.content
            passed = 0
            while not passed:
                for p in pfx:
                    if mc.startswith(p):
                        mc = mc[len(p):].strip()
                        passed = 1
            mc = mc.replace('settings set '+key, '')
            g.texts['welcome'] = mc
            USERNUMBER = await self.helpers.member_number(ctx.message.author, ctx.message.guild)
            e = await self.helpers.build_embed(mc.format(
                USERID=ctx.message.author.id, USERNAME=ctx.message.author.name,
                USERDISCRIMINATOR=ctx.message.author.discriminator,
                USERNUMBER=USERNUMBER, SERVERNAME=ctx.guild.name
            ), 0xffffff)
            asyncio.ensure_future(ctx.send(
                f'Set the {key.replace("text", "")} text to:',
                embed=e))

        elif key.startswith('log') and key[3:] in 'leave,join,message,moderation':
            result = await self.helpers.choose_channel(ctx, msg.guild, value)
            if result or value=="0":
                if value == "0":
                    g.logs[key[3:]] = 0
                    await ctx.send(f'Unset the {key} setting.')
                else:
                    g.logs[key[3:]] = result.id
                # print(g.logs)
                    await ctx.send(f'Set the {key} setting to {result.mention}')


        elif key.replace('channel', '') in ['quotes', 'updates', 'curated', 'welcome']:
            result = await self.helpers.choose_channel(ctx, msg.guild, value)
            key = key.replace('channel', '')
            if not g.channels.get(key):
                g.channels[key] = []
            if result and key == 'curated' and result not in g.channels[key]:
                g.channels[key].append(result.id)
                asyncio.ensure_future(ctx.send(
                    f'Added {result.mention} to curated channels.'
                ))
            elif result and key == 'curated' and result in g.channels[key]:
                g.channels[key] = [c for c in g.channels[key] if c!=result.id]
                asyncio.ensure_future(ctx.send(
                    f'Removed {result.mention} from curated channels.'
                ))
            elif result:
                g.channels[key] = result.id
                asyncio.ensure_future(ctx.send(
                    f'Set the {key} setting to {result.mention}'
                ))

    async def auto_role(self, member):
        gid = member.guild.id
        g = await self.helpers.get_record('server', gid)
        if g['roles'].get('auto'):
            role = next((r for r in member.guild.roles if r.id == g['roles']['auto']), None)
            if role:
                asyncio.ensure_future(member.add_roles(role))

    async def welcome_message(self, m):
        gid = m.guild.id
        g = await self.helpers.get_record('server', gid)
        if g['texts'].get('welcome') and g['channels'].get('welcome'):
            USERNUMBER = await self.helpers.member_number(m, m.guild)
            asyncio.ensure_future(m.guild.get_channel(g['channels']['welcome']).send(
                g['texts']['welcome'].format(
                    **dict(USERNAME=m.name, USERID=m.id, SERVERID=gid,
                           SERVERNAME=m.guild.name,
                           USERDISCRIMINATOR=m.discriminator,
                           USERNUMBER=USERNUMBER)
                )
            ))

def setup(bot):
    cog = SettingsCog(bot)
    bot.add_listener(cog.auto_role, "on_member_join")
    bot.add_listener(cog.welcome_message, "on_member_join")
    bot.add_cog(cog)
