import discord
from discord.ext import commands
import asyncio
import json
import os

class AutoDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "user/delete_channels.json"  # File path for JSON storage
        self.delete_channels = self.load_channels()  # Load the channels and delays from JSON

    def load_channels(self):
        """Load channels and deletion delay from JSON file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return {}

    def save_channels(self):
        """Save channels and delays to JSON file."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump(self.delete_channels, f)

    @commands.command(name="autodelete")
    @commands.has_permissions(manage_channels=True)
    async def add_autodelete(self, ctx, channel: discord.TextChannel, delay: int):
        """Add a channel with a specific deletion delay."""
        self.delete_channels[str(channel.id)] = delay
        self.save_channels()
        await ctx.send(f"Messages in {channel.mention} will now be deleted after {delay} seconds.")

    @commands.command(name="remove_autodelete")
    @commands.has_permissions(manage_channels=True)
    async def remove_autodelete(self, ctx, channel: discord.TextChannel):
        """Remove a channel from the auto-delete list."""
        if str(channel.id) in self.delete_channels:
            del self.delete_channels[str(channel.id)]
            self.save_channels()
            await ctx.send(f"Auto-delete has been removed from {channel.mention}.")
        else:
            await ctx.send(f"{channel.mention} is not set for auto-delete.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages and check if the channel is in the auto-delete list

        channel_id = str(message.channel.id)
        if channel_id in self.delete_channels:
            delay = self.delete_channels[channel_id]
            await asyncio.sleep(delay)
            try:
                await message.delete()
            except discord.NotFound:
                # Message was already deleted, ignore
                pass
            except discord.Forbidden:
                print(f"Bot lacks permission to delete messages in {message.channel.name}.")
            except discord.HTTPException:
                print("Failed to delete message due to an HTTP error.")

async def setup(bot):
    await bot.add_cog(AutoDelete(bot))