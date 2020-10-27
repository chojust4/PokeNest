import discord
from discord.ext import commands
from Commands.General import Help
from Commands import Pokemon


'''
KEY THINGS TO PUT:
- DISCORD BOT TOKEN
- GUILD ID
- CHANNEL ID - specify Pokemon.py file
- SPECIFY INTENTS IN DISCORD DEVELOPER APPLICATION
'''


# SPECIFY YOUR INTENTS HERE: BOT MAY NOT WORK IF CERTAIN INTENTS NOT ALLOWED, # SUCH AS MEMBERS
# I HAVE SPECIFIED ALL, SO YOU MUST ALLOW PRIVILEGED GATEWAY INTENTS IN YOUR DISCORD APP IF
# YOU ARE NOT SPECIFYING YOUR OWN INTENTS
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print('Logged in as {}, {}'.format(bot.user.name, bot.user.id))
    await bot.change_presence(activity=discord.Game(name="Pokemon!"))
    my_guild = bot.get_guild('''YOUR GUILD ID''')  # YOUR GUILD ID HERE
    bot.add_cog(Pokemon.Pokemon(bot, my_guild))


bot.add_cog(Pokemon.Pokedex(bot))
bot.add_cog(Help.Greetings(bot))
bot.run('YOUR DISCORD BOT TOKEN')  # YOUR BOT TOKEN HERE

