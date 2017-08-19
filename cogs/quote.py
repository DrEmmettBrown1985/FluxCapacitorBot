import discord
from discord.ext import commands


class Quote:
    """
    Quote someone with the message id. To get the message id you need to enable developer mode.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name='quote')
    async def _q(self, context, message_id: int, *text):
        """
        Quote someone with the message id. To get the message id you need to enable developer mode.
        """
        channel = context.message.channel
        try:
            message = await self.bot.get_message(channel, str(message_id))
            content = '\a\n'+message.clean_content
            author = message.author
            timestamp = message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            em = discord.Embed(description=content, color=discord.Color.blue())
            em.set_author(name='Quote from: {} on {}'.format(author.name, timestamp), icon_url=avatar)
            if message:
                await self.bot.say(' '.join(text), embed=em)
            else:
                await self.bot.say(embed=em)
        except discord.NotFound:
            em = discord.Embed(description='I\'m sorry, that message doesn\'t exist', color=discord.Color.red())
            await self.bot.say(embed=em)
        except Exception as error:
            await self.bot.say(error)


def setup(bot):
    bot.add_cog(Quote(bot))
