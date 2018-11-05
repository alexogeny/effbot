import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice
from decimal import Decimal
from string import ascii_lowercase, digits
from math import floor
from .helpers import has_any_role

def is_owner():
    async def _is_owner(ctx):
        return ctx.author.id == 305879281580638228
    return commands.check(_is_owner)

def is_trusted():
    async def _is_trusted(ctx):
        return ctx.author.id in [
            259451392630980610, 305879281580638228
        ]
    return commands.check(_is_trusted)

def is_admin_or_owner():
    async def _is_admin_or_owner(ctx):
        msg = ctx.message
        g = await ctx.bot.cogs['Helpers'].get_record('server', msg.guild.id)
        if g['roles'].get('admin') in [a.id for a in msg.author.roles]:
            return True
        elif ctx.author.id == 305879281580638228:
            return True
        elif msg.author.id == msg.guild.owner_id:
            return True
        elif ctx.author.guild_permissions.administrator == True:
            return True
        elif g['roles'].get('admin') not in [a.id for a in msg.author.roles]:
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
        self.last_check = int(time.time())

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

    @my.command(name='ms', aliases=['maxstage', 'MS'])
    async def _ms(self, ctx, ms="1"):
        k = ms.endswith('k') and 1000 or 1
        try:
            float(ms[:-1])
        except:
            asyncio.ensure_future(ctx.send('You must submit a whole number.'))
            return
        a = ctx.author
        try:
            ms = k == 1 and int(ms) or int(float(ms[:-1])*k)
        except ValueError:
            asyncio.ensure_future(ctx.send(
                'Sorry, MS only accepts whole numbers. If your MS is one of `30.000`, `30,000` or `30k`, enter: `30000`'
            ))
            return
        g = await self.helpers.get_record('user', a.id)
        ms_cap = self.bot.config['MS']
        msg = None
        if ms <= (g['tt'].get('ms') or 0):
            msg = ('You cannot lower your MS. If you need it reset,'
                ' join the support server: `.support`')
        elif ms > ms_cap or 0:
            msg = f'You cannot set your MS over the current cap: `{ms_cap:,}`'
        else:
            await self.helpers.sql_update_key('user', a.id, 'tt', 'ms', ms)
            msg = f'Successfully updated MS to `{ms:,}`!'
        asyncio.ensure_future(ctx.send(msg))

    @my.command(name='tcq', aliases=['cq', 'CQ', 'TCQ'])
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
        if tcq <= (g['tt'].get('tcq') or 0):
            asyncio.ensure_future(ctx.send(
                'You can only ever set your TCQ higher than previous. If you'
                ' need it reset, join the support server: `.support`'
            ))
        else:
            await self.helpers.sql_update_key('user', a.id, 'tt', 'tcq', tcq)
            asyncio.ensure_future(ctx.send(f'Successfully updated TCQ to `{tcq:,}`!'))


    @my.command(name='ign', aliases=['IGN'])
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
        if number.isnumeric():
            number = str(float(number))
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
                number = Decimal(n)
                # number = Decimal(b.replace(',', ''))
            elif mode == 0:
                number = Decimal(number)
            return number

    @my.command(name='craftingpower', aliases=['craft', 'craftpower'])
    async def _craftpower(self, ctx, craftpower):
        v, a = craftpower, ctx.author
        if not v.isnumeric():
            return
        if not 0<=int(v)<150:
            return
        await self.helpers.sql_update_key('user', a.id, 'tt', 'cp', int(v))
        asyncio.ensure_future(ctx.send(
            f'Set **{a.name}#{a.discriminator}**\'s crafting power to **{v}**!'
        ))

    @my.command(name='mythicsets', aliases=['sets'])
    async def _mythicsets(self, ctx, mythicsets):
        v, a = mythicsets, ctx.author
        if not v.isnumeric():
            return
        if not 0<=int(v)<=10:
            asyncio.ensure_future(ctx.send(
                '🚫 Oops, there are currently only 6 mythic sets in the game.'
            ))
            return
        await self.helpers.sql_update_key('user', a.id, 'tt', 'sets', int(v))
        asyncio.ensure_future(ctx.send(
            f'Set **{a.name}#{a.discriminator}**\'s mythic sets to **{v}**!'
        ))

    @my.command(name='skillpoints', aliases=['sp'])
    async def _skillpoints(self, ctx, skillpoints):
        v, a = skillpoints, ctx.author
        if not v.isnumeric():
            return
        if not 0<=int(v)<=100000:
            return
        await self.helpers.sql_update_key('user', a.id, 'tt', 'sp', int(v))
        asyncio.ensure_future(ctx.send(
            f'Set **{a.name}#{a.discriminator}**\'s skillpoints to **{v}**!'
        ))

    @my.command(name='bos', aliases=['bookofshadows', 'BoS'])
    async def _bos(self, ctx, bos):
        o = bos
        a = ctx.author
        bos = await self._normalize_number(ctx, bos)
        if bos:
            await self.helpers.sql_update_key('user', a.id, 'tt', 'bos', int(bos))
            asyncio.ensure_future(ctx.send(
                f'Set {a.name}#{a.discriminator}\'s BoS level to {o}'
            ))

    @my.command(name='ltr', aliases=['lifetimerelics', 'LTR'])
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
        elif user:
            a = await self.helpers.choose_member(ctx, ctx.guild, user)
            if not a:
                asyncio.ensure_future(ctx.send(
                    'Oops, I could not find a user with that name or ID.'
                ))
                return
            user = await self.helpers.get_record('user', a.id)
        if not user:
            asyncio.ensure_future(ctx.send(
                'Oops, I could not find a user with that name or ID.'
            ))
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
        ms = u['tt'].get('ms') or 1
        tcq = u['tt'].get('tcq') or 1
        bos = await self.humanize_decimal(u['tt'].get('bos') or 1)
        ltr = await self.humanize_decimal(u['tt'].get('ltr') or 1)
        shr = u['tt'].get('shortcode') or ''
        #clan = await self.helpers.sql_query_db("SELECT * FROM server")
        #clan = next((c['tt'].get('name') for c in clan if c['tt'].get('shortcode')==shr), 'no clan set')
        clan = await self.helpers.sql_filter('titanlord', 'shortcode', shr.upper())
        if not clan:
            clan = dict(clanname='no clan set')
        # clan = next((s.tt.get('name') for s in self.bot._servers if s.tt.get('shortcode')==shr), 'no clan set')
        final = f"Clan: **{clan.get('clanname')}**\nMax Stage: **{ms:,}**\nTotal Clan Quests: **{tcq:,}**\nBook of Shadows: **{bos}**\nLifetime Relics: **{ltr}**"
        e = await self.helpers.full_embed(final,
            thumbnail=avatar,
            author=dict(name=f'{u["tt"].get("ign", a.name)} ({a.name}#{a.discriminator})',
                        image=self.flagstr.format(self.flags[u['tt'].get('country', 'united-states')]))
        )
        return e

    @my.command(name='unset')
    async def _unset(self, ctx, value=None):
        value = value.lower()
        if value == 'clan':
            value = 'shortcode'
        if value.lower().strip() in ['ms', 'maxstage', 'supportcode', 'code']:
            asyncio.ensure_future(ctx.send('Sorry, you cannot unset your max stage or support code. If you need to change it, join the `.support` server'))
            return
        if not value:
            asyncio.ensure_future(ctx.send('You need to tell me what to unset!'))
            return

        g = await self.helpers.get_record('user', ctx.author.id)
        if g and not g['tt'].get(value):
            asyncio.ensure_future(ctx.send('There was nothing to unset!'))
            return
        elif g and g['tt'].get(value):
            g['tt'][value] = None
            await self.helpers.sql_update_key('user', ctx.author.id, 'tt', value, None)
            asyncio.ensure_future(ctx.send(f'All done! {value} cleared for {ctx.author.name}#{ctx.author.discriminator}'))

    @my.command(name='clan')
    async def _clan(self, ctx, clan=None):
        a = ctx.author
        if not clan:
            g = await self.helpers.get_record('user', a.id)
            if g and not g['tt'].get('shortcode'):
                asyncio.ensure_future(ctx.send(
                    f'{a.name}#{a.discriminator} does not belong to a clan. :<'
                ))
                return
            else:
                clan = await self.helpers.sql_filter(
                    'titanlord', 'shortcode', g['tt'].get('shortcode')
                )
                if not clan:
                    return

                if clan and clan.get('clanname'):
                    asyncio.ensure_future(ctx.send(
                        f'{a.name}#{a.discriminator} is a memeber of {clan["clanname"]}!'
                    ))
                    return
        elif not clan.isalnum():
            asyncio.ensure_future(ctx.send(
                'Clan shortcodes must be letters or numbers and less than 6 characters. e.g. `T2RC`'
            ))
            return
        clan_ = await self.helpers.sql_filter('titanlord', 'shortcode', clan.upper())
        if clan_ and clan_.get('clanname'):
            guild_ = self.bot.get_guild(clan_.get('guild'))
            if not guild_:
                return
            guild_record = await self.helpers.get_record('server', guild_.id)
            user_ = guild_.get_member(a.id)
            if not user_:
                return
            roles = [r.id for r in user_.roles]
            is_in_clan = False
            for role in ['roles.grandmaster', 'tt.master', 'tt.captain', 'tt.knight', 'tt.recruit']:
                if not is_in_clan:
                    key, subkey = role.split('.')
                    if guild_record[key].get(subkey, None) in roles:
                        is_in_clan = True
            if not is_in_clan:
                asyncio.ensure_future(ctx.send(
                    'Oops, it looks like you are not in this clan. Sorry!'
                ))
                return

            a = ctx.author
            await self.helpers.sql_update_key('user', a.id, 'tt', 'shortcode', clan.upper())
            asyncio.ensure_future(ctx.send(f'Set the shortcode for {a.name}#{a.discriminator} to: `{clan.upper()}`'))

        elif clan_ and not clan_.get('clanname'):
            asyncio.ensure_future(ctx.send('That clan exists but has no name set. :<'))
        elif not clan_:
            asyncio.ensure_future(ctx.send(f'I could not find a clan with code: {clan.upper()}'))

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

    @is_trusted()
    @my.command(name='set', hidden=True, visible=False)
    async def _setcode(self, ctx, key, value, user):
        if not getattr(user, 'roles', None) and not user.isnumeric():
            try:
                user = await self.helpers.choose_member(ctx, ctx.guild, user)
            except:
                user = await self.bot.get_user_info(int(user[2:-1]))
        elif user.isnumeric():
            try:
                user = await self.bot.get_user_info(int(user))
            except:
                pass
        if not user:
            return
        # u = await self.helpers.choose_member(ctx, ctx.guild, user)
        # m = await self.helpers.get_record('user', u.id)
        u = user
        if value.isnumeric():
            value = int(value)
        # m['tt'][key]=value
        await self.helpers.sql_update_key('user', u.id, 'tt', key, value)
        asyncio.ensure_future(ctx.send('Success!'))

    @commands.group(name="settings")
    async def settings(self, ctx):
        pass

    @commands.group(name='set')
    async def set(self, ctx):
        pass


    @set.command(name='role')
    @is_admin_or_owner()
    async def set_role(self, ctx, role_setting, role_name, extra: int=0):
        roles = 'administrator moderator curator grandmaster updates auto dj timed muted'.split()
        role = next((v for v in roles if v.startswith(role_setting.lower())), None)
        if not role or len(role_setting) < 2:
            return
        if role_setting.lower()[0:2] == 'ti' and not extra:
            return
        elif role_setting.lower()[0:2] == 'ti' and not 0 < extra <= 2400:
            return
        result = await self.helpers.choose_role(ctx, ctx.message.guild, role_name)
        if not result:
            asyncio.ensure_future(ctx.send(f'Error: No role with name **{role_name}** found!'))
            return

        g = await self.helpers.get_record('server', ctx.message.guild.id)
        if role == 'administrator':
            role = 'admin'
        g['roles'][role]=result.id
        if role_setting.lower()[0:2] == 'ti':
            g['extra']['timed_role_timer'] = int(extra)
        await self.helpers.sql_update_record('server', g)
        asyncio.ensure_future(self.helpers.try_mention(ctx, f'{role} role', result))
        return

    @set.command(name='prefix')
    @is_admin_or_owner()
    async def set_prefix(self, ctx, prefix):
        if not 0 < len(prefix) < 6:
            return
        g = await self.helpers.get_record('server', ctx.message.guild.id)
        g['prefix'] = prefix
        await self.helpers.sql_update_record('server', g)
        old = self.bot.prefixes.pop(str(ctx.guild.id), '')
        self.bot.prefixes.update({str(ctx.guild.id):prefix})
        asyncio.ensure_future(ctx.send('Successfully set the custom prefix from {} to **{}**'.format(
            old and f'**{old}**' or 'nothing', prefix
        )))
        return

    @set.command(name='welcome')
    @is_admin_or_owner()
    async def set_welcome(self, ctx):
        m = ctx.message
        pfx = await self.bot.get_prefix(m)
        mc = m.content
        passed = 0
        while not passed:
            for p in pfx:
                if mc.startswith(p):
                    mc = mc[len(p)+len('set welcome'):].strip()
                    passed = 1
        g = await self.helpers.get_record('server', m.guild.id)
        g['texts']['welcome'] = mc
        await self.helpers.sql_update_record('server', g)
        USERNUMBER = await self.helpers.member_number(m.author, m.guild)
        e = await self.helpers.build_embed(mc.format(
            USERID=m.author.id, USER=m.author,
            USERNAME=m.author.name, USERDISCRIMINATOR=m.author.discriminator,
            USERNUMBER=USERNUMBER, SERVER=ctx.guild.name, MENTION=m.author.mention
        ), 0xffffff)
        asyncio.ensure_future(ctx.send('Set the welcome message to:', embed=e))
        return

    @set.command(name='log')
    @is_admin_or_owner()
    async def set_log(self, ctx, log_setting, channel_name):
        valid = 'leaves joins messages moderation system'.split()
        kind = next((v for v in valid if v.startswith(log_setting.lower())), None)
        if not kind or len(channel_name) < 2:
            return
        if kind.endswith('s'):
            kind = kind[0:-1]
        if channel_name.lower() not in ['off', '0']:
            result = await self.helpers.choose_channel(ctx, ctx.message.guild, channel_name)
            if not result:
                asyncio.ensure_future(ctx.send(f'Error: No channel with name **{channel_name}** found!'))
                return
        else:
            result = 0
        g = await self.helpers.get_record('server', ctx.message.guild.id)
        g['logs'][kind]=result and result.id or 0
        await self.helpers.sql_update_record('server', g)
        if result:
            valid=f'Set the logging channel for **{kind}** to: {result.mention}'
        else:
            valid=f'**{kind.title()}** logging turned **off**.'
        asyncio.ensure_future(ctx.send(valid))
        return

    @set.command(name='logignore')
    @is_admin_or_owner()
    async def set_logignore(self, ctx, log_setting, item_name, mode: str='on'):
        valid = 'channel user member'.split()
        kind = next((v for v in valid if v.startswith(log_setting.lower())), None)
        if not kind or len(item_name) < 2:
            return
        if kind == 'user':
            kind = 'member'
        if mode.lower() not in ['off', '0', 'on', '1']:
            return
        result = await getattr(self.helpers, f'choose_{kind}')(ctx, ctx.message.guild, item_name)
        if not result:
            asyncio.ensure_future(ctx.send(f'Error: No {kind} with name **{item_name}** found!'))
            return
        g = await self.helpers.get_record('server', ctx.message.guild.id)
        if not g['logs'].get('ignored'):
            g['logs']['ignored']=[]
        if result.id not in g['logs']['ignored'] and mode.lower() in ['on', '1']:
            g['logs']['ignored'].append(result.id)
            valid = f'Added {result} to ignored {kind}s.'
        elif mode.lower() in ['off', '0']:
            g['logs']['ignored'] = [x for x in g['logs']['ignored'] if x!=result.id]
            valid = f'Removed {result} from ignored {kind}s.'
        elif mode.lower() in ['on', '1'] and result.id in g['logs']['ignored']:
            valid = f'{kind.title()} named {result} already in ignored {kind}s.'

        await self.helpers.sql_update_record('server', g)
        asyncio.ensure_future(ctx.send(valid))
        return

    @set.command(name='channel', aliases=['chan'])
    @is_admin_or_owner()
    async def set_channel(self, ctx, channel_setting, channel_name, mode: str='on'):
        valid = 'quotes updates welcome staff music reddit twitch youtube'.split()
        channel = next((v for v in valid if v.startswith(channel_setting.lower())), None)
        if not channel or len(channel_setting) < 2:
            return
        result = await self.helpers.choose_channel(ctx, ctx.message.guild, channel_name)
        if not result:
            asyncio.ensure_future(ctx.send(f'Error: No channel with name **{channel_name}** found!'))
            return

        g = await self.helpers.get_record('server', ctx.message.guild.id)
        g['channels'][channel]=result.id
        await self.helpers.sql_update_record('server', g)
        asyncio.ensure_future(ctx.send(f'Set the {channel} channel to {result.mention}'))
        return

    @set.command(name='curated', aliases=['curation'])
    @is_admin_or_owner()
    async def set_curated(self, ctx, channel_name, mode: str='on'):
        if mode.lower() not in ['off', '0', 'on', '1']:
            return
        result = await self.helpers.choose_channel(ctx, ctx.message.guild, channel_name)
        if not result:
            asyncio.ensure_future(ctx.send(f'Error: No channel with name **{channel_name}** found!'))
            return
        g = await self.helpers.get_record('server', ctx.message.guild.id)
        if not g['channels'].get('curated'):
            g['channels']['curated']=[]
        if result.id not in g['channels']['curated'] and mode.lower() in ['on', '1']:
            g['channels']['curated'].append(result.id)
            valid = f'Added **#{result}** to curated channels.'
        elif mode.lower() in ['off', '0'] and result.id not in g['channels']['curated']:
            valid = f'Channel named **#{result}** not in curated channels.'
        elif mode.lower() in ['off', '0'] and result.id in g['channels']['curated']:
            g['channels']['curated'] = [x for x in g['channels']['curated'] if x!=result.id]
            valid = f'Removed **#{result}** from curated channels.'
        elif mode.lower() in ['on', '1'] and result.id in g['channels']['curated']:
            valid = f'Channel named **#{result}** already in curated channels.'

        await self.helpers.sql_update_record('server', g)
        asyncio.ensure_future(ctx.send(valid))
        return


    async def timer_check(self):
        while self is self.bot.get_cog('SettingsCog'):
            if int(time.time()) - self.last_check >= 2399.9999999:
                asyncio.ensure_future(self.helpers.update_timed_roles())
            await asyncio.sleep(2399.9999999)

    async def auto_role(self, member):
        gid = member.guild.id
        g = await self.helpers.get_record('server', gid)
        if g['roles'].get('auto') and not member.bot:
            role = next((r for r in member.guild.roles if r.id == g['roles']['auto']), None)
            if role:
                asyncio.ensure_future(member.add_roles(role))

    async def welcome_message(self, m):
        gid = m.guild.id
        g = await self.helpers.get_record('server', gid)
        if g['texts'].get('welcome') and g['channels'].get('welcome') and not m.bot:
            USERNUMBER = await self.helpers.member_number(m, m.guild)
            asyncio.ensure_future(m.guild.get_channel(g['channels']['welcome']).send(
                g['texts']['welcome'].format(
                    **dict(
                        USERID=m.id, USER=m,
                        USERNAME=m.name, USERDISCRIMINATOR=m.discriminator,
                        USERNUMBER=USERNUMBER, SERVER=m.guild.name, MENTION=m.mention
                    )
                )
            ))

def setup(bot):
    cog = SettingsCog(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(cog.timer_check())
    bot.add_listener(cog.auto_role, "on_member_join")
    bot.add_listener(cog.welcome_message, "on_member_join")
    bot.add_cog(cog)
