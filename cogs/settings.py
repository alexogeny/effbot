import os, time
import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice
from decimal import Decimal
from string import ascii_lowercase, digits
from math import floor

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

    @commands.group(name="my", pass_context=True)
    async def my(self, ctx):
        pass

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
            g = await self.helpers.get_record('user', ctx.author.id)
            g.tt['locale'] = lc
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

        ms = k == 1 and int(ms) or int(float(ms[:-1])*k)
        g = await self.helpers.get_record('user', ctx.author.id)
        ms_cap = self.bot.config['MS']
        if ms <= g.tt.get('ms', 0):
            asyncio.ensure_future(ctx.send(
                'You can only ever set your MS higher than previous. If you'
                ' need it reset, join the support server: `.support`'
            ))
        elif ms > ms_cap:
            asyncio.ensure_future(ctx.send(
                f'You cannot set your MS over the current cap: `{ms_cap:,}`'
            ))
        else:
            g.tt['ms'] = ms
            asyncio.ensure_future(ctx.send(f'Successfully updated MS to `{ms:,}`!'))

    @my.command(name='tcq', aliases=['cq'])
    async def _ms(self, ctx, ms="1"):
        k = ms.endswith('k') and 1000 or 1
        try:
            float(ms[:-1])
        except:
            asyncio.ensure_future(ctx.send('You must submit a whole number.'))
            return

        ms = k == 1 and int(ms) or int(float(ms[:-1])*k)
        g = await self.helpers.get_record('user', ctx.author.id)
        if ms <= g.tt.get('tcq', 0):
            asyncio.ensure_future(ctx.send(
                'You can only ever set your TCQ higher than previous. If you'
                ' need it reset, join the support server: `.support`'
            ))
        else:
            g.tt['tcq'] = ms
            asyncio.ensure_future(ctx.send(f'Successfully updated TCQ to `{ms:,}`!'))


    @my.command(name='ign')
    async def _ign(self, ctx, *ign):
        if not ign:
            return
        ign = ' '.join(ign)
        if len(ign) > 16:
            asyncio.ensure_future(ctx.send('IGNs are less than 17 characters long.'))
            return
        g = await self.helpers.get_record('user', ctx.author.id)
        g.tt['ign'] = ign.strip()
        asyncio.ensure_future(ctx.send(
            f'Set the IGN for **{ctx.author.name}#{ctx.author.discriminator}** to **{ign}**'
        ))

    @my.command(name='bos', aliases=['bookofshadows'])
    async def _bos(self, ctx, bos):
        g = await self.helpers.get_record('user', ctx.author.id)
        if not bos.isnumeric():
            valid = await self.helpers.choose_conversion(bos)
            if valid == 2:
                asyncio.ensure_future(ctx.send(
                    'Hm, did you enter your bos level correctly? It should be a number'
                    ', a scientific value, or a TT2 letter value. e.g. `1234`, `1e30`, '
                    'or `1ab`'
                ))
            elif bos[-1].lower() in ['m','b','t','k'] and bos[-2].isnumeric():
                try:
                    float(bos[:-1])
                except:
                    return
                else:
                    bos = Decimal(float(bos[:-1])*pow(10,{'m':6,'k':3,'b':9,'t':12}[bos[-1].lower()]))
            elif valid == 1:
                b = await self.helpers.to_scientific(bos)
                bos = Decimal(b.replace(',',''))
            elif valid == 0:
                bos = Decimal(bos)
        g.tt['bos'] = int(bos)
        asyncio.ensure_future(ctx.send(
            f'Set {ctx.author.name}#{ctx.author.discriminator}\'s BoS level to {int(bos):,}'
        ))

    @my.command(name='ltr', aliases=['lifetimerelics'])
    async def _ltr(self, ctx, bos):
        g = await self.helpers.get_record('user', ctx.author.id)
        if not bos.isnumeric():
            valid = await self.helpers.choose_conversion(bos)
            if valid == 2:
                asyncio.ensure_future(ctx.send(
                    'Hm, did you enter your LTR correctly? It should be a number'
                    ', a scientific value, or a TT2 letter value. e.g. `1234`, `1e30`, '
                    'or `1ab`'
                ))
            elif bos[-1].lower() in ['m','b','t','k'] and bos[-2].isnumeric():
                try:
                    float(bos[:-1])
                except:
                    return
                else:
                    bos = Decimal(float(bos[:-1])*pow(10,{'m':6,'k':3,'b':9,'t':12}[bos[-1].lower()]))
            elif valid == 1:
                b = await self.helpers.to_scientific(bos)
                bos = Decimal(b.replace(',',''))
            elif valid == 0:
                bos = Decimal(bos)
        g.tt['ltr'] = int(bos)
        asyncio.ensure_future(ctx.send(
            f'Set {ctx.author.name}#{ctx.author.discriminator}\'s lifetime relics to {int(bos):,}'
        ))



    @my.command(name='profile')
    async def _profile(self, ctx):
        g = await self.helpers.get_record('user', ctx.author.id)
        data = g.tt
        flags=dict(ger='https://i.imgur.com/Mkk1K1C.png')

        avatar = await self.helpers.get_avatar(ctx.author)

        ms = '`  •  `'.join([f'{g.tt[k]:,} {k.upper()}' for k in ['ms', 'tcq']])
        # relics = '` • `'.join([' '.join([
            # Decimal(g.tt.get(k, 1)).to_eng_string(), k.upper()]) for k in ['bos', 'ltr']])
        bos = str(Decimal(g.tt.get('bos', 1)))
        if len(bos) < 15:
            bos = self.helpers.human_format(bos)
        else:
            x = bos[3:]
            bos = bos[0:3]
            bos = bos+ 'e' + str(len(x))
        ltr = str(Decimal(g.tt.get('ltr', 1)))
        if len(ltr) < 15:
            ltr = self.helpers.human_format(ltr)
        else:
            x = ltr[3:]
            ltr = ltr[0:3]
            ltr = ltr+ 'e' + str(len(x))
        
        e = await self.helpers.full_embed((
            '\n'.join(['`'+x+'`' for x in (ms,bos+' BoS` • `'+ltr+' LTR')])
        ),
            thumbnail = avatar,
            author=dict(name=f'{g.tt.get("ign", ctx.author.name)} ({ctx.author.name}#{ctx.author.discriminator})',
                        image=flags[g.tt.get('locale', 'eng')])
        )
        asyncio.ensure_future(ctx.send(embed=e))


    @my.command(name='supportcode', aliases=['sc', 'code'])
    async def _code(self, ctx, code=None):
        if not code or not isinstance(code, str):
            asyncio.ensure_future(ctx.send('You need to supply a code.'))
        elif isinstance(code, str) and len(code) < 4 or len(code) > 10:
            asyncio.ensure_future(ctx.send('Support codes are between 5 and 10 characters long.'))
        elif isinstance(code, str) and not all([x in ascii_lowercase+digits for x in code]):
            asyncio.ensure_future(ctx.send(f'Valid characters for support codes are: {ascii_lowercase+digits}'))
        else:
            used = next((x for x in self.bot._users
                         if x.tt.get('code') == code.strip()), None)
            if used:
                asyncio.ensure_future(ctx.send(
                    'Somebody has already used that code. If this was not you,'
                    ' use the `verify` command.'
                ))
            else:
                result = None
                g = await self.helpers.get_record('user', ctx.author.id)
                if not g.tt.get('code'):
                    result = await self.helpers.choose_from(ctx, ['confirm'],
                        f'This will set your code to {code}. Type 1 to confirm or `c` to cancel.')
                else:
                    c = g.tt['code']
                    result = await self.helpers.choose_from(ctx, ['confirm'],
                        f'This will override your code from `{c}` to `{code}`. Type 1 to confirm or `c` to cancel.')

                if result:
                    g.tt['code'] = code
                    asyncio.ensure_future(ctx.send(
                        f'Set the support code for **{ctx.author.name}#{ctx.author.discriminator}**!'))

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
        if g.roles.get('auto'):
            role = next((r for r in member.guild.roles if r.id == g.roles['auto']), None)
            if role:
                asyncio.ensure_future(member.add_roles(role))

    async def welcome_message(self, member):
        gid = member.guild.id
        g = await self.helpers.get_record('server', gid)
        if g.texts.get('welcome') and g.channels.get('welcome'):
            USERNUMBER = await self.helpers.member_number(member, member.guild)
            asyncio.ensure_future(member.guild.get_channel(g.channels['welcome']).send(
                g.texts['welcome'].format(
                    **dict(USERNAME=member.name, USERID=member.id, SERVERID=gid,
                           SERVERNAME=member.guild.name,
                           USERDISCRIMINATOR=member.discriminator,
                           USERNUMBER=USERNUMBER)
                )
            ))

def setup(bot):
    cog = SettingsCog(bot)
    bot.add_listener(cog.auto_role, "on_member_join")
    bot.add_listener(cog.welcome_message, "on_member_join")
    bot.add_cog(cog)
