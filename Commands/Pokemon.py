import asyncio
import discord
import pokepy
import random
from beckett.exceptions import InvalidStatusCodeError
from discord.ext import commands, tasks

from Commands import Users

# create instance of V2Client
client = pokepy.V2Client()
channel_id = '''YOUR CHANNEL ID'''  # YOUR CHANNEL ID HERE

# user list accessed by all classes and commands
user_list = Users.Users()


# Pokedex class to access exhaustive list of 893 Pokemon available
class Pokedex(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Search Pokemon by national Pokedex number or name
    # Returns embedded message containing:
    # Pokemon name, default sprite, type, main ability, weight, and height
    @commands.command(aliases=["Pokedex", "POKEDEX"])
    async def pokedex(self, ctx, pokemon_name):
        try:
            client.get_pokemon(pokemon_name)
        except InvalidStatusCodeError:
            print("Invalid Status Code Error: Please enter a valid pokemon name")
            await ctx.send(
                embed=discord.Embed(title="ERROR", description="Invalid pokemon name!", color=0xF84F4F, type="rich"))
        else:
            pokemon = client.get_pokemon(pokemon_name)
            pokemon_url = pokemon.sprites.front_default

            embed_var = discord.Embed(description=pokemon.name.upper(),
                                      color=color(pokemon.types[0].type.name),
                                      type="rich", )
            embed_var.set_thumbnail(url=pokemon_url)
            embed_var.set_author(name="Pokedex",
                                 icon_url="https://cdn2.iconfinder.com/data/icons/pokemon-filledoutline/64/pokeball"
                                          "-people-pokemon-nintendo-video-game-gaming-gartoon-ball-512.png")
            embed_var.add_field(name="Type", value=pokemon.types[0].type.name.upper(), inline=False)
            embed_var.add_field(name="Abilities", value=pokemon.abilities[0].ability.name.upper())
            embed_var.add_field(name="Weight", value=pokemon.weight, inline=False)
            embed_var.add_field(name="Height", value=pokemon.height, inline=False)
            await ctx.send(embed=embed_var)


# Pokemon class wrapping all the pokemon commands
class Pokemon(commands.Cog):
    catch_pokemon = None
    set_status = False
    trade_status = False
    trade_offerer = None
    trade_acceptor = None
    trade_pokemon = None
    accept_pokemon = None
    accept_trade = False

    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        self.spawn.start()

    # Spawns random pokemon into the server every 3 minutes
    @tasks.loop(seconds=180)
    async def spawn(self):
        message_channel = self.bot.get_channel(channel_id)
        pokemon_num = random.randrange(893)
        pokemon = client.get_pokemon(pokemon_num)
        pokemon_url = pokemon.sprites.front_default
        embed_var = discord.Embed(title="A wild Pokemon has appeared!",
                                  description="Guess the name of the pokemon and type !pcatch <pokemon> to catch!",
                                  color=color(pokemon.types[0].type.name))
        embed_var.set_thumbnail(url=pokemon_url)
        await message_channel.send(embed=embed_var)
        print(pokemon.name)
        self.set_pokemon_status(False)
        self.set_pokemon(pokemon.name)
        await self.got_away(pokemon)

    # Method that prints when the pokemon has got away
    async def got_away(self, pokemon):
        await asyncio.sleep(30.0)
        if self.set_status:
            return
        else:
            self.set_pokemon()
            message_channel = self.bot.get_channel(channel_id)
            embed_var2 = discord.Embed(title="Got away safely!", color=color(pokemon.types[0].type.name))
            embed_var2.add_field(name="NAME", value=pokemon.name.upper(), inline=False)
            embed_var2.set_thumbnail(url=pokemon.sprites.front_default)
            await message_channel.send(embed=embed_var2)

    # Set the pokemon name when catch status is active
    @classmethod
    def set_pokemon(cls, pokemon_name=None):
        cls.catch_pokemon = pokemon_name

    # class method to set active status
    @classmethod
    def set_pokemon_status(cls, status):
        cls.set_status = status

    # set trade status
    @classmethod
    def set_trade_status(cls, status, offerer=None, acceptor=None, pokemon1=None, pokemon2=None):
        cls.trade_status = status
        cls.trade_offerer = offerer
        cls.trade_acceptor = acceptor
        cls.trade_pokemon = pokemon1
        cls.accept_pokemon = pokemon2

    # set status of trade if accepted
    @classmethod
    def set_accept_trade(cls, status):
        cls.accept_trade = status

    # Catch the pokemon that spawns in the server
    # Once a pokemon spawns in the server, users are given 30 seconds to guess the pokemon name.
    # * only one user can catch the pokemon
    # * users need a starter pokemon to catch
    @commands.command(aliases=["pcatch", "PCATCH"])
    async def p_catch(self, ctx, pokemon_name):
        if self.catch_pokemon is None:
            embed_var = discord.Embed(title="Got away safely!", color=0xF84F4F)
            await ctx.send(embed=embed_var)
        else:
            try:
                client.get_pokemon(pokemon_name)
            except InvalidStatusCodeError:
                print("Invalid Status Code Error: Please enter a valid pokemon name")
                await ctx.send(
                    embed=discord.Embed(title="ERROR",
                                        description="Invalid pokemon name!",
                                        color=0xF84F4F,
                                        type="rich"))
            else:
                if pokemon_name == self.catch_pokemon:
                    if ctx.author not in user_list.users:
                        embed_message = discord.Embed(description="You must choose a starter pokemon first... use "
                                                                  "!pstart to see a list of starter pokemon",
                                                      color=0xF84F4F)
                        await ctx.send(embed=embed_message)
                    else:
                        self.set_pokemon_status(True)
                        user_list.users.get(ctx.author).add(client.get_pokemon(pokemon_name))
                        pokemon = client.get_pokemon(pokemon_name)
                        pokemon_url = pokemon.sprites.front_default
                        embed_var = discord.Embed(title="You've caught a {}!".format(pokemon.name),
                                                  description="Added to your pokedex",
                                                  color=color(pokemon.types[0].type.name),
                                                  type="rich")
                        embed_var.set_thumbnail(url=pokemon_url)
                        await ctx.send(embed=embed_var)
                else:
                    embed_var = discord.Embed(title="Wrong pokemon name...", color=0xF84F4F)
                    await ctx.send(embed=embed_var)

    # Basic command giving user a list of all the regions and starter pokemon they can choose
    @commands.command(aliases=["pstart", "PSTART"])
    async def p_start(self, ctx):
        embed_var = discord.Embed(title="Choose a starter pokemon", type="rich", color=0x58FF92)
        embed_var.set_author(name="Professor Oak",
                             icon_url="https://static.wikia.nocookie.net/pokemon/images/b/b3/Dream_Professor_Oak.png"
                                      "/revision/latest/scale-to-width-down/1000?cb=20150724015853")
        embed_var.add_field(name="KANTO", value="Bulbasaur | Charmander | Squirtle", inline=False)
        embed_var.add_field(name="JOHTO", value="Chikorita | Cyndaquil | Totodile", inline=False)
        embed_var.add_field(name="HOENN", value="Treecko | Torchic | Mudkip", inline=False)
        embed_var.add_field(name="SINNOH", value="Turtwig | Chimchar | Piplup", inline=False)
        embed_var.add_field(name="UNOVA", value="Snivy | Tepig | Oshawott", inline=False)
        embed_var.add_field(name="KALOS", value="Chespin | Fennekin | Froakie", inline=False)
        embed_var.add_field(name="ALOLA", value="Rowlet | Litten | Popplio", inline=False)
        embed_var.set_image(url="https://i.imgur.com/kFlj6ke.jpg")
        embed_var.add_field(name="Use", value="Use command !ppick to pick your starter pokemon!")
        await ctx.send(embed=embed_var)

    # Pick the starter pokemon the user wants and add to their list
    # To create a user, users must choose a starter pokemon
    # User cannot pick another starter pokemon once they already have one
    @commands.command(aliases=["ppick", "PPICK"])
    async def p_pick(self, ctx, pokemon_name):
        try:
            client.get_pokemon(pokemon_name)
        except InvalidStatusCodeError:
            print("Invalid Status Code Error: Please enter a valid pokemon name")
            await ctx.send(
                embed=discord.Embed(title="ERROR", description="Invalid pokemon name!", color=0xF84F4F, type="rich"))
        else:
            pokemon_start_list = ["bulbasaur", "charmander", "squirtle",
                                  "chikorita", "cyndaquil", "totodile",
                                  "treecko", "torchic", "mudkip",
                                  "turtwig", "chimchar", "piplup",
                                  "snivy", "tepig", "oshawott",
                                  "chespin", "fennekin", "froakie",
                                  "rowlet", "litten", "popplio"
                                  ]
            if pokemon_name.lower() not in pokemon_start_list:
                await ctx.send("Not a valid starter pokemon")
            elif ctx.author in user_list.users:
                await ctx.send("You already have a starter pokemon")
            else:
                pokemon = client.get_pokemon(pokemon_name)
                pokemon_user = Users.User(ctx.author, pokemon)
                user_list.add(pokemon_user)
                pokemon = client.get_pokemon(pokemon_name)
                pokemon_url = pokemon.sprites.front_default
                embed_var = discord.Embed(color=color(pokemon.types[0].type.name))
                embed_var.add_field(name="Congratulations {0.name}".format(ctx.author),
                                    value="You've caught a {}!".format(pokemon_name))
                embed_var.set_thumbnail(url=pokemon_url)
                await ctx.send(embed=embed_var)

    # Select pokemon to trade
    # Users must do this before initiating a trade
    # Throws error when pokemon name is not valid or user does not have selected pokemon
    @commands.command(aliases=["pselect", "PSELECT"])
    async def p_select(self, ctx, pokemon_name):
        try:
            client.get_pokemon(pokemon_name)
        except InvalidStatusCodeError:
            print("Invalid Status Code Error: Please enter a valid pokemon name")
            await ctx.send(
                embed=discord.Embed(title="ERROR", description="Invalid pokemon name!", color=0xF84F4F, type="rich"))
        else:
            if pokemon_name not in user_list.users.get(ctx.author).user_collection:
                await ctx.send("You do not have this pokemon... to view your pokemon, use command !mypokedex")
            else:
                user_list.users.get(ctx.author).select_pokemon(pokemon_name)
                await ctx.send("You have selected {}".format(pokemon_name))

    # Propose a pokemon trade with another user in server
    # Throws discord embedded error when:
    #   user has not selected a pokemon
    #   end user is not valid
    #   end user does not have pokemon they are looking for
    #   pokemon names is invalid
    @commands.command(aliases=["ptrade", "PTRADE"])
    async def p_trade(self, ctx, user_id, user_pokemon):
        if user_list.users.get(ctx.author).selected_pokemon is None:
            await ctx.send("You must select a pokemon to trade first... use command !pselect to select a pokemon")
            return
        try:
            client.get_pokemon(user_pokemon)
        except InvalidStatusCodeError:
            print("Invalid Status Code Error: Please enter a valid pokemon name")
            await ctx.send(
                embed=discord.Embed(title="ERROR", description="Invalid pokemon name!", color=0xF84F4F, type="rich"))
        else:
            user = self.guild.get_member_named(user_id)
            if user not in user_list.users:
                await ctx.send("Not a valid user...")
            elif user_id in user_list.users and user_pokemon not in user_list.users.get(user_id).user_collection:
                await ctx.send("User does not have a {}".format(user_pokemon))
            else:
                self.set_trade_status(True, ctx.author, user, user_list.users.get(ctx.author).selected_pokemon,
                                      client.get_pokemon(user_pokemon))
                embed_var = discord.Embed(title="TRADE",
                                          description="{0.name} has offered a {1.name} to @{2} for a {3}".format(
                                              ctx.author,
                                              user_list.users.get(
                                                  ctx.author).selected_pokemon,
                                              user_id, user_pokemon),
                                          color=0xFFC758)
                await ctx.send(embed=embed_var)
                await asyncio.sleep(60.0)
                self.set_trade_status(False)

                if self.accept_trade:
                    self.accept_trade = False
                    return
                else:
                    embed_var2 = discord.Embed(title="TRADE EXPIRED",
                                               color=0xFFC758)
                    embed_var2.add_field(name="Trade Details",
                                         value="{0.name} has offered a {1.name} to @{2} for a {3}".format(
                                             ctx.author,
                                             user_list.users.get(
                                                 ctx.author).selected_pokemon,
                                             user_id, user_pokemon))
                    await ctx.send(embed=embed_var2)

    # Accept trade offer from another user
    # Returns "Trade has expired..." if trade has exceed 1 minute limit
    @commands.command(aliases=["paccept", "PACCEPT"])
    async def p_accept_trade(self, ctx):
        if self.trade_status:
            user1 = self.trade_offerer
            user2 = self.trade_acceptor
            pokemon1 = self.trade_pokemon
            pokemon2 = self.accept_pokemon
            pokemon1_name = pokemon1.name
            pokemon2_name = pokemon2.name
            del user_list.users.get(user1).user_collection[pokemon1_name]
            del user_list.users.get(user2).user_collection[pokemon2_name]
            user_list.users.get(user1).add(pokemon2)
            user_list.users.get(user2).add(pokemon1)
            await ctx.send("Trade Successful!")
            self.accept_trade = True
            self.set_trade_status(False)
        else:
            await ctx.send("Trade has expired...")

    # View users pokedex
    # Returns none if user does not have a pokedex yet
    @commands.command(aliases=["mypokedex", "MYPOKEDEX"])
    async def my_pokedex(self, ctx):
        if ctx.author not in user_list.users:
            embed_var = discord.Embed(title="Error", description="You do not have a pokedex yet... use command "
                                                                 "!pstart to "
                                                                 "view a list of starter pokemon", color=0xF84F4F)
            await ctx.send(embed=embed_var)
        else:
            embed_var = discord.Embed(color=0x58FF92)
            embed_var.set_author(name="{0.name}'s Pokedex".format(ctx.author),
                                 icon_url="https://cdn2.iconfinder.com/data/icons/pokemon-filledoutline/64/pokeball"
                                          "-people-pokemon-nintendo-video-game-gaming-gartoon-ball-512.png")
            user = user_list.users.get(ctx.author)
            for key, item in user.user_collection.items():
                embed_var.add_field(name=key.upper(), value=item.types[0].type.name, inline=False)
            await ctx.send(embed=embed_var)

    # Remove a pokemon from users pokedex
    # Returns an embedded error when:
    #   pokemon name does not exist
    #   user does not contain pokemon
    @commands.command(aliases=["premove", "PREMOVE"])
    async def p_remove(self, ctx, pokemon_name):
        try:
            client.get_pokemon(pokemon_name)
        except InvalidStatusCodeError:
            print("Invalid Status Code Error: Please enter a valid pokemon name")
            await ctx.send(
                embed=discord.Embed(title="ERROR", description="Invalid pokemon name!", color=0xF84F4F, type="rich"))
        else:
            if pokemon_name not in user_list.users.get(ctx.author).user_collection:
                await ctx.send("You do not have this pokemon... to view your pokemon, use command !mypokedex")
            else:
                del user_list.users.get(ctx.author).user_collection[pokemon_name]
                await ctx.send("{} has been released to the wild!".format(pokemon_name))

    '''
    FUTURE IDEAS:
    MINI-GAMES:
        Fishing - Users can catch pokemon by playing hangman
        Berry Blender - Users collect berries and can blend them to catch a special pokemon
    '''


# Set discord embed color based on Pokemon type
def color(type):
    if type == "normal":
        return 0xD8CA9C
    elif type == "water":
        return 0x006AFF
    elif type == "electric":
        return 0xFBFF28
    elif type == "fighting":
        return 0xFF6128
    elif type == "ground":
        return 0x78623A
    elif type == "psychic":
        return 0x9B39B6
    elif type == "rock":
        return 0x4E400F
    elif type == "dark":
        return 0x231C04
    elif type == "steel":
        return 0x9F9F9F
    elif type == "fire":
        return 0xFE3200
    elif type == "grass":
        return 0x21CF16
    elif type == "ice":
        return 0xDCFFFE
    elif type == "poison":
        return 0xFE6EEA
    elif type == "flying":
        return 0xFFB2F4
    elif type == "bug":
        return 0x4E7E0A
    elif type == "ghost":
        return 0x5F0A7E
    elif type == "dragon":
        return 0xFC8C17
    else:
        return 0xFC17F1
