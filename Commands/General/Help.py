import discord
from discord.ext import commands


# Basic commands to getting started playing Pokemon
class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # Welcomes user into the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(
                'Welcome {0.mention}, use command !phelp to see how you can start catching Pokemon!'.format(member))

    # lists out commands user can use to play
    @commands.command(aliases=["phelp", "PHELP"])
    async def p_help(self, ctx):
        embed_var = discord.Embed(title="Help",
                                  description="A list of commands has been shown below",
                                  color=0x58FF6C,
                                  type="rich")
        embed_var.add_field(name="Getting Started",
                            value="!pstart to see a list of starter pokemon \n"
                                  "!ppick <pokemon-name> to pick a starter Pokemon",
                            inline=False)
        embed_var.add_field(name="General",
                            value="!pcatch <pokemon-name> to catch a pokemon when it spawns"
                                  " in the server \n"
                                  "!premove <pokemon-name> to remove a pokemon from your "
                                  "pokedex \n"
                                  "!mypokedex to view your pokemon \n"
                                  "!pokedex <pokemon-name> to view a pokemon and various"
                                  " details \n",
                            inline=False)
        embed_var.add_field(name="Trade",
                            value="!pselect <pokemon-name> to select a pokemon to trade \n"
                                  "!ptrade <USER#DISCRIM> <pokemon-name> to initiate a trade "
                                  "\n"
                                  "!paccept to accept trade from other user",
                            inline=False)
        await ctx.send(embed=embed_var)
