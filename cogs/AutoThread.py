import discord
from discord.ext import commands
import json
import asyncio
import os

class MultiChannelAutoThread(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "user/threads/auto_thread_config.json"
        self.thread_channels = {}  # Dictionary to store channel settings
        self.load_config()

    def load_config(self):
        """Load channel configuration from a JSON file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.thread_channels = json.load(f)

    def save_config(self):
        """Save channel configuration to a JSON file."""
        with open(self.config_file, "w") as f:
            json.dump(self.thread_channels, f, indent=2)

    @commands.command(name="setthread")
    @commands.has_permissions(manage_channels=True)
    async def set_thread_channel(self, ctx, channel: discord.TextChannel, *, first_message: str = None):
        """Set a channel for auto-threading with an optional first message."""
        self.thread_channels[str(channel.id)] = {
            "first_message": first_message
        }
        self.save_config()
        await ctx.send(f"Auto-threading is set up in {channel.mention} with the first message: '{first_message}'")

    @commands.command(name="removethread")
    @commands.has_permissions(manage_channels=True)
    async def remove_thread_channel(self, ctx, channel: discord.TextChannel):
        """Remove auto-threading for a specific channel."""
        if str(channel.id) in self.thread_channels:
            del self.thread_channels[str(channel.id)]
            self.save_config()
            await ctx.send(f"Auto-threading has been disabled for {channel.mention}.")
        else:
            await ctx.send("Auto-threading is not currently enabled for that channel.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots and messages outside the specified channels
        await asyncio.sleep(1.5)
        if message.author.bot or str(message.channel.id) not in self.thread_channels:
            return

        # Create a thread for each message in the specified channel
        thread = await message.create_thread(name="Comments")

        # Send the first message in the thread, if set
        first_message = self.thread_channels[str(message.channel.id)]["first_message"]
        if first_message:
            await thread.send(first_message)

async def setup(bot):
    await bot.add_cog(MultiChannelAutoThread(bot))