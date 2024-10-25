import discord
from discord.ext import commands

class ServerManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.main_guild_ids = [1264302631174668299, 1282315062756769803]  # List of allowed server IDs
        self.owner_id = 1264251459231416391  # Your Discord user ID (for your personal notifications)

    @commands.Cog.listener()
    async def on_ready(self):
        # Check all servers the bot is currently in on startup
        for guild in self.bot.guilds:
            if guild.id not in self.main_guild_ids:
                await self.leave_guild(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Automatically leave if the bot joins any server not in the allowed list
        if guild.id not in self.main_guild_ids:
            await self.leave_guild(guild)

    async def leave_guild(self, guild):
        """Helper function to leave a guild and notify the bot owner with an invite link."""
        try:
            # Generate an invite link in a text channel
            invite_link = None
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    invite_link = await channel.create_invite(max_age=0, max_uses=0)
                    break

            # Notify the server owner (guild owner)
            guild_owner = guild.owner
            if guild_owner:
                await guild_owner.send(
                    f"The bot is leaving your server: **{guild.name}** (ID: {guild.id}) because it is not on the allowed list of servers."
                )

            # Leave the server
            await guild.leave()
            print(f"Left server: {guild.name} (ID: {guild.id}) as it's not in the allowed list.")

            # Notify you (the bot owner) about leaving the server
            bot_owner = self.bot.get_user(self.owner_id)
            if bot_owner:
                if invite_link:
                    await bot_owner.send(
                        f"Bot has left the server: **{guild.name}** (ID: {guild.id}) because it is not in the allowed list.\n"
                        f"Here’s an invite link to the server: {invite_link}"
                    )
                else:
                    await bot_owner.send(
                        f"Bot has left the server: **{guild.name}** (ID: {guild.id}) because it is not in the allowed list.\n"
                        "No invite link could be created due to insufficient permissions."
                    )
        
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