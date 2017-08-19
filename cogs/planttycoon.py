from cogs.utils.dataIO import dataIO
from discord.ext import commands
from random import choice
import collections
import datetime
import discord
import asyncio
import time
import os


class PlantTycoon:
    """Grow your own plants! Be sure to take proper care of it."""
    def __init__(self, bot):
        self.bot = bot

        #
        # Loading all data
        #
        
        self.gardeners = dataIO.load_json('data/planttycoon/gardeners.json')
        self.plants = dataIO.load_json('data/planttycoon/plants.json')
        self.products = dataIO.load_json('data/planttycoon/products.json')
        self.defaults = dataIO.load_json('data/planttycoon/defaults.json')
        self.badges = dataIO.load_json('data/planttycoon/badges.json')
        self.notifications = dataIO.load_json('data/planttycoon/notifications.json')

        #
        # Starting loops
        #

        self.completion_task = bot.loop.create_task(self.check_completion())
        self.degradation_task = bot.loop.create_task(self.check_degradation())
        self.notification_task = bot.loop.create_task(self.send_notification())

        #
        # Loading bank
        #

        self.bank = bot.get_cog('Economy').bank

    async def _save_gardeners(self):

        #
        # This function saves the state of all gardeners.
        #

        dataIO.save_json('data/planttycoon/gardeners.json', self.gardeners)

    async def _gardener(self, id):

        #
        # This function returns an individual gardener namedtuple
        #

        g = self.gardeners[id]
        gardener = collections.namedtuple('gardener', 'badges points products current')
        return gardener(badges=g['badges'], points=g['points'], products=g['products'], current=g['current'])

    async def _grow_time(self, gardener):

        #
        # Calculating the remaining grow time for a plant
        #

        now = int(time.time())
        then = gardener.current['timestamp']
        return (gardener.current['time'] - (now - then)) / 60

    async def _degradation(self, gardener):

        #
        # Calculating the rate of degradation per check_completion() cycle.
        #

        modifiers = sum([self.products[product]['modifier'] for product in gardener.products if gardener.products[product] > 0] + [self.badges['badges'][badge]['modifier'] for badge in gardener.badges])
        degradation = (100 / (gardener.current['time'] / 60) * (self.defaults['degradation']['base_degradation'] + gardener.current['degradation'])) + modifiers
        d = collections.namedtuple('degradation', 'degradation time modifiers')
        return d(degradation=degradation, time=gardener.current['time'], modifiers=modifiers)

    async def _die_in(self, gardener, degradation):

        #
        # Calculating how much time in minutes remains until the plant's health hits 0
        #

        return int(gardener.current['health'] / degradation.degradation)

    async def _withdraw_points(self, id, amount):

        #
        # Substract points from the gardener
        #

        points = self.gardeners[id]['points']
        if (points - amount) < 0:
            return False
        else:
            self.gardeners[id]['points'] -= amount
            return True

    async def _get_member(self, user_id):

        #
        # Return a member object
        #

        return discord.User(id=str(id))  # I made it a string just to be sure

    async def _send_notification(self, user_id, message):

        #
        # Sends a Direct Message to the gardener
        #

        member = await self._get_member(user_id)
        await self.bot.send_message(member, message)

    async def _send_message(self, channel, message):

        #
        # Sends a message
        #

        await self.bot.send_message(channel, message)

    async def _add_health(self, channel, id, product, product_category):

        #
        # The function to add health
        #

        product = product.lower()
        product_category = product_category.lower()
        if product in self.products and self.products[product]['category'] == product_category:
            if product in self.gardeners[id]['products']:
                if self.gardeners[id]['products'][product] > 0:
                    self.gardeners[id]['current']['health'] += self.products[product]['health']
                    self.gardeners[id]['products'][product] -= 1
                    if self.gardeners[id]['products'][product] == 0:
                        del[self.gardeners[id]['products'][product.lower()]]
                    if product_category == "water":
                        emoji = ":sweat_drops:"
                    elif product_category == "fertilizer":
                        emoji = ":poop:"
                    elif product_category == "tool":
                        emoji = ":scissors:"
                    message = 'Your plant got some health back! {}'.format(emoji)
                    if self.gardeners[id]['current']['health'] > self.gardeners[id]['current']['threshold']:
                        self.gardeners[id]['current']['health'] -= self.products[product]['damage']
                        if product_category == 'tool':
                            damage_msg = 'You used {} too many times!'.format(product)
                        else:
                            damage_msg = 'You gave too much of {}.'.format(product)
                        message = '{} Your plant lost some health. :wilted_rose:'.format(damage_msg)
                    self.gardeners[id]['points'] += self.defaults['points']['add_health']
                    await self._save_gardeners()
                else:
                    message = 'You have no {}. Go buy some!'.format(product)
            else:
                if product_category == 'tool':
                    message = 'You have don\'t have a {}. Go buy one!'.format(product)
                else:
                    message = 'You have no {}. Go buy some!'.format(product)
        else:
            message = 'Are you sure you are using {}?'.format(product_category)

        if product_category == "water":
            em = discord.Embed(description=message, color=discord.Color.blue())
        elif product_category == "fertilizer":
            em = discord.Embed(description=message, color=discord.Color.dark_gold())
        elif product_category == "tool":
            em = discord.Embed(description=message, color=discord.Color.dark_grey())
        await self.bot.say(embed=em)

    @commands.group(pass_context=True, name='gardening')
    async def _gardening(self, context):
        """Gardening commands."""
        if context.invoked_subcommand is None:
            prefix = context.prefix

            title = '**Welcome to Plant Tycoon.**\n'
            description = 'This cog was made by **SnappyDragon18** and **PaddoInWonderland**.\n'
            description += 'Grow your own plant. Be sure to take proper care of yours. If it grows, you get a reward.\n'
            description += 'As you nurture your plant, you gain **Gro-cash** which can be traded for credits at a fixed rate.\n\n'
            description += '**Commands**\n\n'
            description += '``{}gardening seed``: Plant a seed inside the earth.\n'.format(prefix)
            description += '``{}gardening profile``: Check your gardening profile.\n'.format(prefix)
            description += '``{}gardening plants``: Look at the list of the available plants.\n'.format(prefix)
            description += '``{}gardening plant``: Look at the details of a plant.\n'.format(prefix)
            description += '``{}gardening state``: Check the state of your plant.\n'.format(prefix)
            description += '``{}gardening products``: Look at the list of the available gardening supplies.\n'.format(prefix)
            description += '``{}gardening buy``: Buy gardening supplies.\n'.format(prefix)
            description += '``{}gardening convert``: Exchange Gro-cash for credits.'.format(prefix)
            description += '``{}shovel``: Shovel your plant out.\n'.format(prefix)
            description += '``{}water``: Water your plant.\n'.format(prefix)
            description += '``{}fertilize``: Fertilize the soil.\n'.format(prefix)
            description += '``{}prune``: Prune your plant.\n'.format(prefix)

            em = discord.Embed(title=title, description=description, color=discord.Color.green())
            em.set_thumbnail(url='http://i.imgur.com/iLVSemK.png')
            await self.bot.say(embed=em)

    @_gardening.command(pass_context=True, name='seed')
    async def _seed(self, context):
        """Plant a seed inside the earth."""
        author = context.message.author
        # server = context.message.server
        if author.id not in self.gardeners:
            self.gardeners[author.id] = {}
            self.gardeners[author.id]['current'] = False
            self.gardeners[author.id]['points'] = 0
            self.gardeners[author.id]['badges'] = []
            self.gardeners[author.id]['products'] = {}
        if not self.gardeners[author.id]['current']:
            d = datetime.date.today()
            month = d.month

            #
            # Event Plant Check start
            #

            if month == 1:
                self.plants['plants'].append(self.plants['event']['January'])
                event_plant = True
            elif month == 2:
                self.plants['plants'].append(self.plants['event']['February'])
                event_plant = True
            elif month == 3:
                self.plants['plants'].append(self.plants['event']['March'])
                event_plant = True
            elif month == 4:
                self.plants['plants'].append(self.plants['event']['April'])
                event_plant = True
            elif month == 10:
                self.plants['plants'].append(self.plants['event']['October'])
                event_plant = True
            elif month == 11:
                self.plants['plants'].append(self.plants['event']['November'])
                event_plant = True
            elif month == 12:
                self.plants['plants'].append(self.plants['event']['December'])
                event_plant = True
            else:
                event_plant = False

            #
            # Event Plant Check end
            #

            plant = choice(self.plants['plants'])
            plant['timestamp'] = int(time.time())
            if event_plant:
                del[self.plants['plants'][40]]
            message = 'During one of your many heroic adventures, you came across a mysterious bag that said "pick one". '
            message += 'To your surprise it had all kinds of different seeds in them. And now that you\'re home, you want to plant it. '
            message += 'You went to a local farmer to identify the seed, and the farmer said it was {} **{} ({})** seed.\n\n'.format(plant['article'], plant['name'], plant['rarity'])
            message += 'Take good care of your seed and water it frequently. Once it blooms, something nice might come from it. If it dies, however, you will get nothing.'
            if 'water' not in self.gardeners[author.id]['products']:
                self.gardeners[author.id]['products']['water'] = 0
            self.gardeners[author.id]['products']['water'] += 5
            self.gardeners[author.id]['current'] = plant
            await self._save_gardeners()

            em = discord.Embed(description=message, color=discord.Color.green())
            await self.bot.say(embed=em)
        else:
            plant = self.gardeners[author.id]['current']
            await self.bot.say('You\'re already growing {} **{}**, silly.'.format(plant['article'], plant['name']))

    @_gardening.command(pass_context=True, name='profile')
    async def _profile(self, context, *, member: discord.Member=None):
        """Check your gardening profile."""
        if member:
            author = member
        else:
            author = context.message.author
        if author.id in self.gardeners:
            gardener = await self._gardener(author.id)
            em = discord.Embed(color=discord.Color.green(), description='\a\n')
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            em.set_author(name='Gardening profile of {}'.format(author.name), icon_url=avatar)
            em.add_field(name='**Gro-cash**', value=gardener.points)
            if not gardener.current:
                em.add_field(name='**Currently growing**', value='None')
            else:
                em.set_thumbnail(url=gardener.current['image'])
                em.add_field(name='**Currently growing**', value='{0} ({1:.2f}%)'.format(gardener.current['name'], gardener.current['health']))
            if not gardener.badges:
                em.add_field(name='**Badges**', value='None')
            else:
                badges = ''
                for badge in gardener.badges:
                    badges += '{} {}\n'.format(badge.capitalize(), self.badges['badges'][badge]['modifier'])
                em.add_field(name='**Badges**', value=badges)
            if not gardener.products:
                em.add_field(name='**Products**', value='None')
            else:
                products = ''
                for product in gardener.products:
                    products += '{} ({}) {}\n'.format(product.capitalize(), gardener.products[product]/self.products[product.lower()]['uses'], self.products[product]['modifier'])
                em.add_field(name='**Products**', value=products)
            if gardener.current:
                degradation = await self._degradation(gardener)
                die_in = await self._die_in(gardener, degradation)
                to_grow = await self._grow_time(gardener)
                em.set_footer(text='Total degradation: {0:.2f}% / {1} min (100 / ({2} / 60) * (BaseDegr {3:.2f} + PlantDegr {4:.2f})) + ModDegr {5:.2f}) Your plant will die in {6} minutes and {7:.1f} minutes to go for flowering.'.format(degradation.degradation, self.defaults['timers']['degradation'], degradation.time, self.defaults['degradation']['base_degradation'], gardener.current['degradation'], degradation.modifiers, die_in, to_grow))
            await self.bot.say(embed=em)
        else:
            await self.bot.say('Who?')

    @_gardening.command(pass_context=True, name='plants')
    async def _plants(self, context):
        """Look at the list of the available plants."""
        tick = ''
        tock = ''
        tick_tock = 0
        for plant in self.plants['plants']:
            if tick_tock == 0:
                tick += '**{}**\n'.format(plant['name'])
                tick_tock = 1
            else:
                tock += '**{}**\n'.format(plant['name'])
                tick_tock = 0
        em = discord.Embed(title='All plants that are growable', color=discord.Color.green())
        em.add_field(name='\a', value=tick)
        em.add_field(name='\a', value='\a')
        em.add_field(name='\a', value=tock)
        await self.bot.say(embed=em)

    @_gardening.command(pass_context=True, name='plant')
    async def _plant(self, context, *plant):
        """Look at the details of a plant."""
        plant = ' '.join(plant)
        for p in self.plants['plants']:
            if p['name'].lower() == plant.lower():
                plant = p
                t = True
                break
            t = False
        if t:
            em = discord.Embed(title='Plant statistics of {}'.format(plant['name']), color=discord.Color.green(), description='\a\n')
            em.set_thumbnail(url=plant['image'])
            em.add_field(name='**Name**', value=plant['name'])
            em.add_field(name='**Rarity**', value=plant['rarity'].capitalize())
            em.add_field(name='**Grow Time**', value='{0:.1f} minutes'.format(plant['time'] / 60))
            em.add_field(name='**Damage Threshold**', value='{}%'.format(plant['threshold']))
            em.add_field(name='**Badge**', value=plant['badge'])
            em.add_field(name='**Reward**', value=plant['reward'])
            await self.bot.say(embed=em)
        else:
            await self.bot.say('What plant?')

    @_gardening.command(pass_context=True, name='state')
    async def _state(self, context):
        """Check the state of your plant."""
        author = context.message.author
        gardener = await self._gardener(author.id)
        if author.id not in self.gardeners or not gardener.current:
            message = 'You\'re currently not growing a plant.'
        else:
            plant = gardener.current
            degradation = await self._degradation(gardener)
            die_in = await self._die_in(gardener, degradation)
            to_grow = await self._grow_time(gardener)
            message = 'You\'re growing {0} **{1}**. Its health is **{2:.2f}%** and still has to grow for **{3:.1f}** minutes. It is losing **{4:.2f}%** per minute and will die in **{5:.1f}** minutes.'.format(plant['article'], plant['name'], plant['health'], to_grow, degradation.degradation, die_in)
        await self.bot.say(message)

    @_gardening.command(pass_context=True, name='products')
    async def _products(self, context):
        """Look at the list of the available gardening supplies."""
        em = discord.Embed(title='All gardening supplies you can buy', description='\a\n', color=discord.Color.green())
        for product in self.products:
                em.add_field(name='**{}**'.format(product.capitalize()), value='Cost: {} pts\n+{} health\n-{}% damage\nUses: {}\nCategory: {}'.format(self.products[product]['cost'], self.products[product]['health'], self.products[product]['damage'], self.products[product]['uses'], self.products[product]['category']))
        await self.bot.say(embed=em)

    @_gardening.command(pass_context=True, name='buy')
    async def _buy(self, context, product, amount: int):
        """Buy gardening supplies."""
        author = context.message.author
        if author.id not in self.gardeners:
            message = 'You\'re currently not growing a plant.'
        else:
            if product.lower() in self.products and amount > 0:
                cost = self.products[product.lower()]['cost'] * amount
                withdraw_points = await self._withdraw_points(author.id, cost)
                if withdraw_points:
                    if product.lower() not in self.gardeners[author.id]['products']:
                        self.gardeners[author.id]['products'][product.lower()] = 0
                    self.gardeners[author.id]['products'][product.lower()] += amount
                    self.gardeners[author.id]['products'][product.lower()] += amount * self.products[product.lower()]['uses']
                    await self._save_gardeners()
                    message = 'You bought {}.'.format(product.lower())
                else:
                    message = 'You don\'t have enough points. You have {}, but need {}.'.format(self.gardeners[author.id]['points'], self.products[product.lower()]['cost'] * amount)

            else:
                message = 'I don\'t have this product.'
        await self.bot.say(message)
        

    @_gardening.command(pass_context=True, name='convert')
    async def _convert(self, context, amount: int):
        """Exchange Gro-Cash for credits."""
        id = await self._get_member(context.message.author.id)
        if self.bank.account_exists(id):
            withdraw_points = await self._withdraw_points(id, amount)
            if withdraw_points:
                self.bank.deposit_credits(id, amount)
                message = '{} Gro-cash successfully exchanged for credits.'.format(amount)
            else:
                message = 'You don\'t have enough points. You have {}, but need {}.'.format(self.gardeners[author.id]['points'], amount)
        else:
            message = 'Account not found.'
        await self.bot.say(message)


    @commands.command(pass_context=True, name='shovel')
    async def _shovel(self, context):
        """Shovel your plant out."""
        author = context.message.author
        if author.id not in self.gardeners or not self.gardeners[author.id]['current']:
            message = 'You\'re currently not growing a plant.'
        else:
            self.gardeners[author.id]['current'] = False
            message = 'You sucessfuly shovelled your plant out.'
            if self.gardeners[author.id]['points'] < 0:
                self.gardeners[author.id]['points'] = 0
            await self._save_gardeners()
        em = discord.Embed(description=message, color=discord.Color.dark_grey())
        await self.bot.say(embed=em)

    @commands.command(pass_context=True, name='water')
    async def _water(self, context):
        """Water your plant."""
        author = context.message.author
        channel = context.message.channel
        product = 'water'
        product_category = 'water'
        if author.id not in self.gardeners or not self.gardeners[author.id]['current']:
            message = 'You\'re currently not growing a plant.'
            await self._send_message(channel, message)
        else:
            await self._add_health(channel, author.id, product, product_category)

    @commands.command(pass_context=True, name='fertilize')
    async def _fertilize(self, context, fertilizer):
        """Fertilize the soil."""
        author = context.message.author
        channel = context.message.channel
        product = fertilizer
        product_category = 'fertilizer'
        if author.id not in self.gardeners or not self.gardeners[author.id]['current']:
            message = 'You\'re currently not growing a plant.'
            await self._send_message(channel, message)
        else:
            await self._add_health(channel, author.id, product, product_category)

    @commands.command(pass_context=True, name='prune')
    async def _prune(self, context):
        """Prune your plant."""
        author = context.message.author
        channel = context.message.channel
        product = 'pruner'
        product_category = 'tool'
        if author.id not in self.gardeners or not self.gardeners[author.id]['current']:
            message = 'You\'re currently not growing a plant.'
            await self._send_message(channel, message)
        else:
            await self._add_health(channel, author.id, product, product_category)

    # TODO
    #
    # Future function
    #
    # @commands.command(pass_context=True, name='pesticide')
    # async def _pesticide(self, context):
    #    """Spray pesticide on your plant."""
    #    author = context.message.author
    #    if author.id not in self.gardeners or not self.gardeners[author.id]['current']:
    #        message = 'You\'re currently not growing a plant.'
    #    else:
    #        if 'pesticide' in self.gardeners[author.id]['products']:
    #            if self.gardeners[author.id]['products']['pesticide']['uses'] > 0:
    #                self.gardeners[author.id]['current']['health'] += self.products['pesticide']['health']
    #                self.gardeners[author.id]['products']['pesticide']['uses'] -= 1
    #                message = 'Your plant is free of pests!'
    #                if self.gardeners[author.id]['current']['health'] > self.gardeners[author.id]['current']['threshold']:
    #                    self.gardeners[author.id]['current']['health'] -= self.products['pesticide']['damage']
    #                    message = 'You sprayed too much pesticide! Your plant lost some health. :wilted_rose:'
    #                self.gardeners[author.id]['points'] += self.defaults['points']['pesticide']
    #                await self._save_gardeners()
    #            else:
    #                message = 'You have no pesticide. Go buy some!'
    #        else:
    #            message = 'You have no pesticide. Go buy some!'
    #    await self.bot.say(message)

    async def check_degradation(self):
        while 'PlantTycoon' in self.bot.cogs:
            for id in self.gardeners:
                gardener = await self._gardener(id)
                if gardener.current:
                    degradation = await self._degradation(gardener)
                    self.gardeners[id]['current']['health'] -= degradation.degradation
                    self.gardeners[id]['points'] += self.defaults['points']['growing']
                    await self._save_gardeners()
            await asyncio.sleep(self.defaults['timers']['degradation'] * 60)

    async def check_completion(self):
        while 'PlantTycoon' in self.bot.cogs:
            now = int(time.time())
            delete = False
            for id in self.gardeners:
                gardener = await self._gardener(id)
                if gardener.current:
                    then = gardener.current['timestamp']
                    health = gardener.current['health']
                    grow_time = gardener.current['time']
                    badge = gardener.current['badge']
                    reward = gardener.current['reward']
                    if (now - then) > grow_time:
                        self.gardeners[id]['points'] += self.defaults['points']['complete']
                        if badge not in self.gardeners[id]['badges']:
                            self.gardeners[id]['badges'].append(badge)
                        message = 'Your plant made it! You are rewarded with the **{}** badge and you have recieved **{}** points.'.format(badge, reward)
                        delete = True
                    if health < 0:
                        message = 'Your plant died!'
                        delete = True
                if delete:
                    await self.bot.send_message(discord.User(id=str(id)), message)
                    self.gardeners[id]['current'] = False
                    await self._save_gardeners()
            await asyncio.sleep(self.defaults['timers']['completion'] * 60)

    async def send_notification(self):
        while 'PlantTycoon' in self.bot.cogs:
            for id in self.gardeners:
                gardener = await self._gardener(id)
                if gardener.current:
                    health = gardener.current['health']
                    if health < self.defaults['notification']['max_health']:
                        message = choice(self.notifications['messages'])
                        await self.bot.send_notification(gardener, message)
            await asyncio.sleep(self.defaults['timers']['notification'] * 60)

    def __unload(self):
        self.completion_task.cancel()
        self.degradation_task.cancel()
        self.notification_task.cancel()
        self._save_gardeners()


def check_folder():
    if not os.path.exists('data/planttycoon'):
        print('Creating data/planttycoon folder...')
        os.makedirs('data/planttycoon')


def check_file():
    if not dataIO.is_valid_json('data/planttycoon/gardeners.json'):
        print('Creating default gardeners.json...')
        dataIO.save_json('data/planttycoon/gardeners.json', {})


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(PlantTycoon(bot))
