import discord
from discord.ext import commands

class ServerManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.main_guild_id = [1264302631174668299, 1282315062756769803] 
        self.owner_id = 1264251459231416391  # Replace with your Discord user ID

    @commands.Cog.listener()
    async def on_ready(self):
        # Check all servers the bot is currently in on startup
        for guild in self.bot.guilds:
            if guild.id not in self.main_guild_id:
                await self.leave_guild(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Automatically leave if the bot joins any server other than the main one
        if guild.id != self.main_guild_id:
            await self.leave_guild(guild)

    async def leave_guild(self, guild):
        """Helper function to leave a guild and notify the bot owner."""
        owner = self.bot.get_user(self.owner_id)
        
        # Notify the owner before leaving
        if owner:
            await owner.send(f"Bot is about to leave the server: **{guild.name}** (ID: {guild.id}) because it's not the main server.")
        
        try:
            await guild.leave()
            print(f"Left server: {guild.name} (ID: {guild.id}) as it's not the main server.")
        except discord.Forbidden:
            print(f"Couldn't leave {guild.name} due to lack of permissions.")
        except Exception as e:
            print(f"An error occurred while leaving {guild.name}: {e}")

    @commands.command(aliases=["fm", "firstmessage"])
    async def first_message(self, ctx):
        """Jump to the first message in the current channel."""
        # Fetch the first message in the channel
        first_message = None
        async for message in ctx.channel.history(oldest_first=True, limit=1):
            first_message = message
        if first_message:
            # Create a button view
            fm_jump = discord.ui.View()
            button = discord.ui.Button(label="Jump to the First Message", url=first_message.jump_url)
            fm_jump.add_item(button)
            await ctx.send(view=fm_jump)
        else:
            await ctx.send("Couldn't find the first message.")
            
async def setup(bot):
    await bot.add_cog(ServerManager(bot))