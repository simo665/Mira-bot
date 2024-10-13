import discord
from discord.ext import commands

class ServerManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.main_guild_id = 1264302631174668299  # Replace with your main server ID
        self.owner_id = 1264251459231416391  # Replace with your Discord user ID

    @commands.Cog.listener()
    async def on_ready(self):
        # Check all servers the bot is currently in on startup
        for guild in self.bot.guilds:
            if guild.id != self.main_guild_id:
                await self.leave_guild(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Automatically leave if the bot joins any server other than the main one
        if guild.id != self.main_guild_id:
            await self.leave_guild(guild)

    async def leave_guild(self, guild):
        """Helper function to leave a guild and notify the bot owner."""
        try:
            await guild.leave()
            print(f"Left server: {guild.name} (ID: {guild.id}) as it's not the main server.")
            
            # Send a DM to the owner (you) when the bot leaves a server
            owner = self.bot.get_user(self.owner_id)
            if owner:
                await owner.send(f"Bot has left a server: **{guild.name}** (ID: {guild.id}).")
        except discord.Forbidden:
            print(f"Couldn't leave {guild.name} due to lack of permissions.")
        except Exception as e:
            print(f"An error occurred while leaving {guild.name}: {e}")
    @commands.command(aliases=["fm", "firstmessage"])
    async def first_message(self, ctx):
        """Jump to the first message in the current channel."""
        first_message = None
        async for message in ctx.channel.history(oldest_first=True, limit=1):
        first_message = message
        if first_message:
            await ctx.send(f"Here's the first message in this channel: {first_message.jump_url}")
        else:
            await ctx.send("Couldn't find the first message.")
    
async def setup(bot):
    await bot.add_cog(ServerManager(bot))
