import discord
from discord.ext import commands
import os
import sys
import shutil
from .utils import checks

class Chatter:
    """Chatter cog: talk as your bot using the console. Thanks to MissingNO123 for the inspiration."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    @checks.is_owner()
    async def chatter(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @chatter.command(pass_context=True)
    @checks.is_owner()
    async def here(self, ctx):
        """Start talk mode to send messages to the current channel as your bot via the console.

           Console commands:
           ~~exit to exit this mode
           ~~switch to start sending messages to another channel. Only lets you send 1 message in the channel you specify using this command.

           Errors:
           HTTPException (discord.HTTPException): either you tried to send an empty message or something messed up
           Forbidden (discord.Forbidden): Your bot does not have the permission to delete messages.
           Other: not really sure
        """
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            await self.bot.say("Not allowed to delete messages.")
        except discord.HTTPException:
            await self.bot.say("Failed to delete message.")
        except:
            await self.bot.say("Unknown error encountered, failed to delete message.")
        while True:
            hereInput = input("Message to say: ")

            if hereInput == "~~exit":
                break
            elif hereInput == "~~switch":
                toChannel = input("ID of channel to switch to: ")
                toInput = input("Message to say: ")
                getChannelObj = self.bot.get_channel(toChannel)
                await self.bot.send_message(getChannelObj, toInput)
            else:
                await self.bot.say(hereInput)

    @chatter.command(pass_context=True)
    @checks.is_owner()
    async def overthere(self, ctx, *, channelid: str):
        """Start talk mode in another channel, must specify the channel ID.

           Console commands:
           ~~exit - Exits talk mode
           ~~switch - Switches channel you are talking in, only lets you send 1 message in the channel you specify with this command.

           Errors:
           HTTPException (discord.HTTPException): either you tried to send an empty message or something messed up
           Forbidden (discord.Forbidden): The bot does not have permissions to delete messages.
           Other: not really sure
        """
        if channelid is None:
            await self.bot.say("Please specify a channel ID.")
        else:
            pass
        try:
            await self.bot.delete_message(ctx.message)
        except discord.Forbidden:
            await self.bot.say("No permissions, cannot delete message.")
        except discord.HTTPException:
            await self.bot.say("Failed to delete message.")
        except:
            await self.bot.say("Failed to delete message.")
        while True:
            sendMessage = input("Message to send to channel " + channelid + ": ")
            if sendMessage == "~~exit":
                break
            elif sendMessage == "~~switch":
                switchTo = input("ID of channel to switch to: ")
                inputToSwitch = input("Message to say: ")
                getObjChannel = self.bot.get_channel(switchTo)
                await self.bot.send_message(getObjChannel, inputToSwitch)
            else:
                channelObj = self.bot.get_channel(channelid)
                await self.bot.send_message(channelObj, sendMessage)


    @commands.command(pass_context=True)
    async def chattercoginfo(self, ctx):
        """Information about the Chatter cog."""
        try:
            embed = discord.Embed(title='Chatter cog - Information', color=discord.Colour.red())
            embed.add_field(name="Creator", value="Hexexpeck#8781")
            embed.add_field(name="Version", value="v0.2")
            embed.add_field(name="Download", value="[Hex-Cogs GitHub repository](https://cogs.red/cogs/Hexexpeck/Hex-Cogs)")
            embed.add_field(name="Description", value="A cog made by Hexexpeck to let you talk as the bot using your bot console.")
            embed.add_field(name="Commands in this cog", value="`[p]chatter righthere`, `[p]chatter overthere <channel id here>`, `[p]chattercoginfo`")
            embed.set_footer(text="Another cog made by Hexexpeck for Red-DiscordBot with love")
            await self.bot.say(embed=embed)
        except TypeError:
            pass
        except:
            await self.bot.say("Exception occured when trying to post embed.")
            print("Exception occured when trying to post embed for Chatter cog.")

def setup(bot):
    n = Chatter(bot)
    bot.add_cog(n)
            
