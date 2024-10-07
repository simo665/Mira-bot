import discord
from discord.ext import commands
import asyncio  
from config import TOKEN, intents

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='servercount')
    async def sc(self, ctx):
        """Send the number of servers the bot is in."""
        guild_count = len(self.bot.guilds)
        await ctx.send(f"I am in {guild_count} servers!")

# Set up the cog
async def setup(bot):
    await bot.add_cog(Utility(bot))
  
