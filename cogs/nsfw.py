import discord
from discord.ext import commands
from __main__ import send_cmd_help
from bs4 import BeautifulSoup
import random


class Nsfw:
    """Nsfw commands."""

    def __init__(self, bot):
        self.bot = bot
        self.session = self.bot.http.session

    @commands.group(pass_context=True)
    async def nsfw(self, ctx):
        """Nsfw Commands"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @nsfw.command(no_pm=True)
    async def yandere(self):
        """Random Image From Yandere"""
        try:
            query = ("https://yande.re/post/random")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="highres").get("href")
            await self.bot.say(image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(no_pm=True)
    async def konachan(self):
        """Random Image From Konachan"""
        try:
            query = ("https://konachan.com/post/random")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="highres").get("href")
            await self.bot.say(image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(no_pm=True)
    async def e621(self):
        """Random Image From e621"""
        try:
            query = ("https://e621.net/post/random")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="highres").get("href")
            await self.bot.say(image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(no_pm=True)
    async def rule34(self):
        """Random Image From rule34"""
        try:
            query = ("http://rule34.xxx/index.php?page=post&s=random")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            await self.bot.say('http:' + image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(no_pm=True)
    async def danbooru(self):
        """Random Image From Danbooru"""
        try:
            query = ("http://danbooru.donmai.us/posts/random")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            await self.bot.say('http://danbooru.donmai.us' + image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(no_pm=True)
    async def gelbooru(self):
        """Random Image From Gelbooru"""
        try:
            query = ("http://www.gelbooru.com/index.php?page=post&s=random")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            await self.bot.say(image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(no_pm=True)
    async def tbib(self):
        """Random Image From DrunkenPumken"""
        try:
            query = ("http://www.tbib.org/index.php?page=post&s=random")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            await self.bot.say("http:" + image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(no_pm=True)
    async def xbooru(self):
        """Random Image From Xbooru"""
        try:
            query = ("http://xbooru.com/index.php?page=post&s=random")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            await self.bot.say(image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(no_pm=True)
    async def furrybooru(self):
        """Random Image From Furrybooru"""
        try:
            query = ("http://furry.booru.org/index.php?page=post&s=random")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            await self.bot.say(image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(no_pm=True)
    async def drunkenpumken(self):
        """Random Image From DrunkenPumken"""
        try:
            query = ("http://drunkenpumken.booru.org/index.php?page=post&s=random")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            await self.bot.say(image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(no_pm=True)
    async def lolibooru(self):
        """Random Image From Lolibooru"""
        try:
            query = ("https://lolibooru.moe/post/random/")
            page = await self.session.get(query)
            page = await page.text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            image = image.replace(' ','%20')
            await self.bot.say(image)
        except Exception as e:
            await self.bot.say(":x: **Error:** `{}`".format(e))

    @nsfw.command(pass_context=True, no_pm=True)
    async def ysearch(self, ctx, *tags: str):
        """Search Yandere With A Tag"""
        if tags == ():
            await self.bot.say(":warning: Tags are missing.")
        else:
            try:
                tags = ("+").join(tags)
                query = ("https://yande.re/post.json?limit=42&tags=" + tags)
                page = await self.session.get(query)
                json = await page.json()
                if json != []:
                    await self.bot.say(random.choice(json)['jpeg_url'])
                else:
                    await self.bot.say(":warning: Yande.re has no images for requested tags.")
            except Exception as e:
                await self.bot.say(":x: `{}`".format(e))

def setup(bot):
    n = Nsfw(bot)
    bot.add_cog(n)
