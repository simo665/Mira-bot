import discord
from discord.ext import commands
import asyncio
import json
import os

class AutoReact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.react_channels = self.load_channels()
        self.default_reaction = "👍"  # Change this to the default emoji you want to use

    def load_channels(self):
        # Load the auto-react channels from JSON file
        if os.path.exists("auto_react_channels.json"):
            with open("auto_react_channels.json", "r") as f:
                return json.load(f)
        else:
            return []

    def save_channels(self):
        # Save the auto-react channels to JSON file
        with open("auto_react_channels.json", "w") as f:
            json.dump(self.react_channels, f)

    @commands.command(name="add_auto_react")
    @commands.has_permissions(manage_channels=True)
    async def add_auto_react(self, ctx, channel: discord.TextChannel, emoji: str = None):
        """Add a channel to auto-react with a specified emoji."""
        emoji = emoji or self.default_reaction
        # Add channel ID and emoji to the list if it's not already added
        if {"channel_id": channel.id, "emoji": emoji} not in self.react_channels:
            self.react_channels.append({"channel_id": channel.id, "emoji": emoji})
            self.save_channels()
            await ctx.send(f"Auto-react with {emoji} set for {channel.mention}.")
        else:
            await ctx.send("This channel is already set for auto-react.")

    @commands.command(name="remove_auto_react")
    @commands.has_permissions(manage_channels=True)
    async def remove_auto_react(self, ctx, channel: discord.TextChannel):
        """Remove auto-react from a specified channel."""
        initial_count = len(self.react_channels)
        # Filter out the specified channel from the list
        self.react_channels = [
            entry for entry in self.react_channels if entry["channel_id"] != channel.id
        ]
        if len(self.react_channels) < initial_count:
            self.save_channels()
            await ctx.send(f"Auto-react removed from {channel.mention}.")
        else:
            await ctx.send("This channel was not set for auto-react.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages and non-specified channels
        if message.author.bot:
            return

        # Check if the message's channel is in the auto-react list
        for entry in self.react_channels:
            if message.channel.id == entry["channel_id"]:
                try:
                    await asyncio.sleep(1.5)  # Add delay before reacting
                    await message.add_reaction(entry["emoji"])
                except discord.Forbidden:
                    print(f"Bot lacks permissions to react in {message.channel.name}")
                except discord.HTTPException:
                    print("Failed to add reaction due to an HTTP error.")

async def setup(bot):
    await bot.add_cog(AutoReact(bot))