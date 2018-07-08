import discord
from discord.ext import commands

import importlib
import traceback
import asyncio
import threading
import datetime
import os
import glob

class CogNotFoundError(Exception):
    pass
class CogLoadError(Exception):
    pass
class NoSetupError(CogLoadError):
    pass
class CogUnloadError(Exception):
    pass
class OwnerUnloadWithoutReloadError(CogUnloadError):
    pass

def box(lang, text):
    return f"```{lang}\n{text}\n```"

def error(text):
    return "\N{NO ENTRY SIGN} {}".format(text)

def warning(text):
    return "\N{WARNING SIGN} {}".format(text)

def info(text):
    return "\N{INFORMATION SOURCE} {}".format(text)

def question(text):
    return "\N{BLACK QUESTION MARK ORNAMENT} {}".format(text)

def bold(text):
    return "**{}**".format(text)

def inline(text):
    return "`{}`".format(text)

def italics(text):
    return "*{}*".format(text)

def pagify(text, delims=["\n"], *, escape=True, shorten_by=8,
           page_length=2000):
    """DOES NOT RESPECT MARKDOWN BOXES OR INLINE CODE"""
    in_text = text
    if escape:
        num_mentions = text.count("@here") + text.count("@everyone")
        shorten_by += num_mentions
    page_length -= shorten_by
    while len(in_text) > page_length:
        closest_delim = max([in_text.rfind(d, 0, page_length)
                             for d in delims])
        closest_delim = closest_delim if closest_delim != -1 else page_length
        if escape:
            to_send = escape_mass_mentions(in_text[:closest_delim])
        else:
            to_send = in_text[:closest_delim]
        yield to_send
        in_text = in_text[closest_delim:]

    if escape:
        yield escape_mass_mentions(in_text)
    else:
        yield in_text

def strikethrough(text):
    return "~~{}~~".format(text)

def underline(text):
    return "__{}__".format(text)

def escape(text, *, mass_mentions=False, formatting=False):
    if mass_mentions:
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
    if formatting:
        text = (text.replace("`", "\\`")
                    .replace("*", "\\*")
                    .replace("_", "\\_")
                    .replace("~", "\\~"))
    return text

def escape_mass_mentions(text):
    return escape(text, mass_mentions=True)

def is_owner():
    async def predicate(ctx):
        return ctx.author.id == 305879281580638228
    return commands.check(predicate)

class Owner:
    """All owner-only commands that relate to debug bot operations."""

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @is_owner()
    async def load(self, ctx, *, cog_name: str):
        """Loads a cog
        Example: load mod"""
        module = cog_name.strip()
        if "cogs." not in module:
            module = "cogs." + module
        try:
            self._load_cog(module)
        except CogNotFoundError:
            await ctx.send("That cog could not be found.")
        except CogLoadError as e:
            traceback.print_exc()
            await ctx.send("There was an issue loading the cog. Check"
                               " your console or logs for more information.")
        except Exception as e:
            traceback.print_exc()
            await ctx.send('Cog was found and possibly loaded but '
                               'something went wrong. Check your console '
                               'or logs for more information.')
        else:
            # set_cog(module, True)
            # await self.disable_commands()
            await ctx.send("The cog has been loaded.")

    @commands.group(invoke_without_command=True)
    @is_owner()
    async def unload(self, ctx, *, cog_name: str):
        """Unloads a cog
        Example: unload mod"""
        module = cog_name.strip()
        if "cogs." not in module:
            module = "cogs." + module
        if not self._does_cogfile_exist(module):
            await ctx.send("That cog file doesn't exist. I will not"
                               " turn off autoloading at start just in case"
                               " this isn't supposed to happen.")
        # else:
            # set_cog(module, False)
        try:  # No matter what we should try to unload it
            self._unload_cog(module)
        except OwnerUnloadWithoutReloadError:
            await ctx.send("I cannot allow you to unload the Owner plugin"
                               " unless you are in the process of reloading.")
        except CogUnloadError as e:
            traceback.print_exc()
            await ctx.send('Unable to safely unload that cog.')
        else:
            await ctx.send("The cog has been unloaded.")

    @unload.command(name="all")
    @is_owner()
    async def unload_all(self):
        """Unloads all cogs"""
        cogs = self._list_cogs()
        still_loaded = []
        for cog in cogs:
            # set_cog(cog, False)
            try:
                self._unload_cog(cog)
            except OwnerUnloadWithoutReloadError:
                pass
            except CogUnloadError as e:
                traceback.print_exc()
                still_loaded.append(cog)
        if still_loaded:
            still_loaded = ", ".join(still_loaded)
            await ctx.send("I was unable to unload some cogs: "
                "{}".format(still_loaded))
        else:
            await ctx.send("All cogs are now unloaded.")

    @is_owner()
    @commands.command(name="reload")
    async def _reload(self, ctx, *, cog_name: str):
        """Reloads a cog
        Example: reload audio"""
        module = cog_name.strip()
        if "cogs." not in module:
            module = "cogs." + module

        try:
            self._unload_cog(module, reloading=True)
        except:
            pass

        try:
            self._load_cog(module)
        except CogNotFoundError:
            await ctx.send("That cog cannot be found.")
        except NoSetupError:
            await ctx.send("That cog does not have a setup function.")
        except CogLoadError as e:
            traceback.print_exc()
            await ctx.send("That cog could not be loaded. Check your"
                               " console or logs for more information.")
        else:
            # set_cog(module, True)
            # await self.disable_commands()
            await ctx.send("The cog has been reloaded.")

    @commands.command(name="cogs")
    @is_owner()
    async def _show_cogs(self, ctx):
        """Shows loaded/unloaded cogs"""
        # This function assumes that all cogs are in the cogs folder,
        # which is currently true.

        # Extracting filename from __module__ Example: cogs.owner
        loaded = [c.__module__.split(".")[1] for c in self.bot.cogs.values()]
        # What's in the folder but not loaded is unloaded
        unloaded = [c.split(".")[1] for c in self._list_cogs()
                    if c.split(".")[1] not in loaded]

        if not unloaded:
            unloaded = ["None"]

        msg = ("+ Loaded\n"
               "{}\n\n"
               "- Unloaded\n"
               "{}"
               "".format(", ".join(sorted(loaded)),
                         ", ".join(sorted(unloaded)))
               )
        for page in pagify(msg, [" "], shorten_by=16):
            await ctx.send(box(page.lstrip(" "), lang="diff"))

    @commands.command(name="shutdown")
    @is_owner()
    async def _shutdown(self, ctx):
        self.bot.cogs['Helpers'].save_records()
        await self.bot.logout()

    @commands.command(name="serverconfig")
    @is_owner()
    async def _serverconfig(self, ctx):
        # await ctx.send(ctx.guild.id)
        #print(self.bot._servers)
        #await ctx.send(ctx.bot._servers)
        server = await self.bot.cogs['Helpers'].get_record('server', ctx.guild.id)
        # server = [s for s in ctx.bot._servers if s['id']==ctx.guild.id]
        if server:
            await ctx.send(server['config'].as_pretty())

    @commands.command(name='userconfig', visible=False)
    @is_owner()
    async def _userconfig(self, ctx, user: str):
        user = await self.bot.cogs['Helpers'].get_obj(
            ctx.guild, 'member', 'name', value
        )
        if not user:
            user = await self.bot.cogs['Helpers'].get_record('user', user)
        if user:
            await ctx.send(user['config'].as_pretty())

    @commands.command(name="restart")
    @is_owner()
    async def _restart(self, ctx):
        await self.bot.logout()
        await self.bot.login()

    @commands.group(name="set", pass_context=True)
    async def _set(self, ctx):
        """Changes Red's core settings"""
        if ctx.invoked_subcommand is None:
            await ctx.send('derp')
            return

    @_set.command(pass_context=True, no_pm=True)
    @is_owner()
    async def nickname(self, ctx, *, nickname=""):
        """Sets Red's nickname
        Leaving this empty will remove it."""
        nickname = nickname.strip()
        if nickname == "":
            nickname = None
        try:
            await self.bot.change_nickname(ctx.message.server.me, nickname)
            await ctx.send("Done.")
        except discord.Forbidden:
            await ctx.send("I cannot do that, I lack the "
                "\"Change Nickname\" permission.")

    # @_set.command(name="token")
    # @is_owner()
    # async def _token(self, token):
    #     """Sets Red's login token"""
    #     if len(token) < 50:
    #         await ctx.send("Invalid token.")
    #     else:
    #         self.bot.settings.token = token
    #         self.bot.settings.save_settings()
    #         await ctx.send("Token set. Restart me.")
    #         log.debug("Token changed.")



    @commands.command(pass_context=True)
    @is_owner()
    async def traceback(self, ctx, public: bool=False):
        """Sends to the owner the last command exception that has occurred
        If public (yes is specified), it will be sent to the chat instead"""
        if not public:
            destination = ctx.message.author
        else:
            destination = ctx.message.channel

        if self.bot._last_exception:
            for page in pagify(self.bot._last_exception):
                await destination.send(box("python", page))
        else:
            await ctx.send("No exception has occurred yet.")



    def _load_cog(self, cogname):
        if not self._does_cogfile_exist(cogname):
            raise CogNotFoundError(cogname)
        try:
            mod_obj = importlib.import_module(cogname)
            importlib.reload(mod_obj)
            self.bot.load_extension(mod_obj.__name__)
        except SyntaxError as e:
            raise CogLoadError(*e.args)
        except:
            raise

    def _unload_cog(self, cogname, reloading=False):
        if not reloading and cogname == "cogs.owner":
            raise OwnerUnloadWithoutReloadError(
                "Can't unload the owner plugin :P")
        try:
            self.bot.unload_extension(cogname)
        except:
            raise CogUnloadError

    def _list_cogs(self):
        cogs = [os.path.basename(f) for f in glob.glob("cogs/*.py")]
        return ["cogs." + os.path.splitext(f)[0] for f in cogs]

    def _does_cogfile_exist(self, module):
        if "cogs." not in module:
            module = "cogs." + module
        if module not in self._list_cogs():
            return False
        return True




def setup(bot):
    n = Owner(bot)
    bot.add_cog(n)
