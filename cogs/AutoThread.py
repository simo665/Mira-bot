import discord
from discord.ext import commands
import json
import os

class AutoThread(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "auto_thread_config.json"
        self.thread_channel_id = None
        self.thread_first_message = None
        self.load_config()  # Load configuration when the cog is initialized

    def load_config(self):
        """Loads the configuration from the JSON file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config = json.load(f)
                self.thread_channel_id = config.get("thread_channel_id")
                self.thread_first_message = config.get("thread_first_message")

    def save_config(self):
        """Saves the configuration to the JSON file."""
        config = {
            "thread_channel_id": self.thread_channel_id,
            "thread_first_message": self.thread_first_message
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f)

    @commands.command(name="setthread")
    @commands.has_permissions(manage_channels=True)
    async def set_thread_channel(self, ctx, channel: discord.TextChannel, *, first_message: str):
        """Sets the channel for auto-threading and the first message in each thread."""
        self.thread_channel_id = channel.id
        self.thread_first_message = first_message
        self.save_config()  # Save the configuration to a file
        await ctx.send(f"Auto-threading is set up in {channel.mention} with the first thread message: '{first_message}'")

    @commands.command(name="removethread")
    @commands.has_permissions(manage_channels=True)
    async def remove_thread_channel(self, ctx, channel: discord.TextChannel):
        """Removes auto-threading for a specific channel."""
        if self.thread_channel_id == channel.id:
            self.thread_channel_id = None
            self.thread_first_message = None
            self.save_config()  # Save changes
            await ctx.send(f"Auto-threading has been disabled for {channel.mention}.")
        else:
            await ctx.send("Auto-threading is not currently enabled for that channel.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots and messages outside the specified channel
        if message.author.bot or message.channel.id != self.thread_channel_id:
            return

        # Create a thread for each message in the specified channel
        thread = await message.create_thread(name="Comments")

        # Send the first message in the thread, if set
        if self.thread_first_message:
            await thread.send(self.thread_first_message)

async def setup(bot):
    await bot.add_cog(AutoThread(bot))