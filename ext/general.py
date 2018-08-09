from datetime import datetime
from discord.ext import commands
import discord
import logging
import os
import platform
import pytz
import time
import toml

from .utils import permissions as perms


log = logging.getLogger(__name__)


class General():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def _ping(self, ctx):
        """ Check the bot latency. """
        pingtime = time.time()
        e = discord.Embed(title="Pinging...", colour=0xFF0000)
        msg = await ctx.send(embed=e)
        ping = time.time() - pingtime
        em = discord.Embed(title='Pong!', description=f'Response latency: {1000.*ping:.2f}ms\nWebSocket latency: {1000.*adjutant.latency:.2f}ms', colour=0x00FF00)
        await msg.edit(embed=em)

    @commands.command(name="help")
    async def _help(self, ctx):
        """ Displays a list of Adjutants commands. """
        embed = discord.Embed(color=discord.Colour.blue(), title="Adjutant DiscordBot", description="My prefix is `a>`.")
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(icon_url=ctx.message.author.avatar_url, text="")
        embed.add_field(name="Commands", value="To see a list of all commands click [here](https://github.com/K4cePhoenix/Adjutant-DiscordBot/wiki).", inline=False)
        embed.add_field(name="Invite", value=f"To invite Adjutant to your server follow [this](https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot) link.", inline=False)
        embed.add_field(name="Server", value="To join the support server click [here](https://discordapp.com/invite/nfa9jnu).", inline=False)
        embed.add_field(name="More Information", value="You can find more information using the `info` command.", inline=False)
        await ctx.send(embed=embed)
    
    @commands.command(name='info')
    async def _info(self, ctx):
        """ Display information about Adjutant. """
        users = sum(1 for _ in self.bot.get_all_members())
        embed = discord.Embed(color=discord.Colour.blue(), title="Adjutant Information", description="")
        embed.set_footer(text="By Phoenix#2694")
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        try:
            embed.add_field(name="Statistics: ", value=f"Servers: **{len(self.bot.guilds)}**\nShards: **{len(self.bot.shards)}**\nUsers: **{users}**")
        except:
            embed.add_field(name="Statistics: ", value=f"Servers: **{len(self.bot.guilds)}**\nUsers: **{users}**")
        embed.add_field(name="Version: ", value=f"Adjutant: **{self.bot.version}**\ndiscord.py: **{discord.__version__}**\nPython: **{platform.python_version()}**")
        embed.add_field(name="Other: ", value = "Website: https://k4cephoenix.github.io/adjutant-discordbot\nDiscord: https://discord.gg/nfa9jnu")
        await ctx.send(embed=embed)

    @commands.command(name='user')
    async def _user(self, ctx):
        """ Shows info on the specified user. """
        try:
            user = ctx.message.mentions[0]
        except Exception:
            user = ctx.message.author
        roles = []
        for r in user.roles:
            roles.append(r.name)
        user_roles = "\n".join(roles)
        embed = discord.Embed(color=user.color, description=f"Here's some information about {user.name}!")
        if perms._check(ctx, 5):
            embed.title = f"{user} 🐦"
        if perms._check(ctx, 4):
            embed.title = f"{user} 🦆"
        elif perms._check(ctx, 3):
            embed.title = f"{user} 🐧"
        elif perms._check(ctx, 2):
            embed.title = f"{user} 🐔"
        elif perms._check(ctx, 1):
            embed.title = f"{user} 🐣"
        else:
            embed.title = f"{user}"
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Username", value=user.name, inline=False)
        embed.add_field(name="Discriminator", value=user.discriminator, inline=False)
        embed.add_field(name="ID", value=str(user.id), inline=False)
        embed.add_field(name="Roles", value=user_roles, inline=False)
        try:
            embed.add_field(name="Playing", value=user.game.name, inline=False)
        except:
            pass
        embed.add_field(name="Date of Account Creation", value=user.created_at, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='server')
    async def _server(self, ctx):
        """Link to the Adjutant support guild. """
        embed = discord.Embed(title="Join my guild!", description="You can join my guild [here](https://discord.gg/nfa9jnu).")
        await ctx.send(embed=embed)

    @commands.command(name='invite')
    async def _invite(self, ctx):
        """ Link to add Adjutant to a guild. """
        embed = discord.Embed(title="Invite me!", description=f"You can invite me [here](https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot).")
        await ctx.send(embed=embed)

    @commands.command()
    async def suggest(self, ctx, *, suggestion: str):
        """ Sends a suggestion. """
        channel = self.bot.get_channel(436581310379720705)
        color = discord.Colour.blue()
        embed = discord.Embed(color=color, title="New suggestion!", description="I'm so excited to read it!")
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        embed.add_field(name="Suggestion", value="{} sent this suggestion: ``{}``".format(ctx.message.author, suggestion))
        try:
            await channel.send(embed=embed)
        except Exception:
            self.bot.rclient.captureException()
            await ctx.send("There was an error... But don't worry! You can post your suggestion in my server. To receive an invitation, just say `a>server`!")
            traceback.print_exc()
        await ctx.send("I sent your suggestion, <@{}>~".format(ctx.message.author.id))

    @commands.command()
    async def report(self, ctx, *, report: str):
        """ Sends a bug report. """
        channel = self.bot.get_channel(436581310379720705)
        color = discord.Colour.blue()
        embed = discord.Embed(color=color, title="New report!", description="Hopefully, you guys can fix it..")
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        embed.add_field(name="Report", value="{} sent this report: ``{}``".format(ctx.message.author, report))
        try:
            await channel.send(embed=embed)
        except Exception:
            self.bot.rclient.captureException()
            await ctx.send("There was an error... Don't worry! You can contact my developers in my server. To enter my server, just say ``$!server``!")
            traceback.print_exc()
        await ctx.send("I sent your report, <@{}>~".format(ctx.message.author.id))


def setup(bot):
    n = General(bot)
    bot.add_cog(n)