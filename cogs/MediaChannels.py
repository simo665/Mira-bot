import discord
from discord.ext import commands
import json
import os

class MediaOnlyChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "media_only_config.json"
        self.media_only_channels = {}  # Dictionary to store channel settings per server
        self.load_config()

    def load_config(self):
        """Load channel configuration from a JSON file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.media_only_channels = json.load(f)

    def save_config(self):
        """Save channel configuration to a JSON file."""
        with open(self.config_file, "w") as f:
            json.dump(self.media_only_channels, f)

    @commands.command(name="setmediachannel")
    @commands.has_permissions(manage_channels=True)
    async def set_media_channel(self, ctx, channel: discord.TextChannel):
        """Sets a channel as media-only, allowing only files/attachments."""
        guild_id = str(ctx.guild.id)
        channel_id = str(channel.id)

        # Add the channel to the media-only list for the server
        if guild_id not in self.media_only_channels:
            self.media_only_channels[guild_id] = []
        if channel_id not in self.media_only_channels[guild_id]:
            self.media_only_channels[guild_id].append(channel_id)
            self.save_config()
            await ctx.send(f"{channel.mention} has been set as a media-only channel.")
        else:
            await ctx.send(f"{channel.mention} is already a media-only channel.")

    @commands.command(name="removemediachannel")
    @commands.has_permissions(manage_channels=True)
    async def remove_media_channel(self, ctx, channel: discord.TextChannel):
        """Removes a media-only restriction from a channel."""
        guild_id = str(ctx.guild.id)
        channel_id = str(channel.id)

        if guild_id in self.media_only_channels and channel_id in self.media_only_channels[guild_id]:
            self.media_only_channels[guild_id].remove(channel_id)
            if not self.media_only_channels[guild_id]:  # Remove guild entry if empty
                del self.media_only_channels[guild_id]
            self.save_config()
            await ctx.send(f"{channel.mention} is no longer a media-only channel.")
        else:
            await ctx.send(f"{channel.mention} is not currently set as a media-only channel.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots and messages outside of designated media-only channels
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)

        if guild_id in self.media_only_channels and channel_id in self.media_only_channels[guild_id]:
            # Delete messages without attachments
            if not message.attachments:
                await message.delete()
                try:
                    await message.channel.send(f"{message.author.mention}, this channel is for media files only!", delete_after=5)
                except discord.Forbidden:
                    print("Bot lacks permission to send messages in the media-only channel.")

async def setup(bot):
    await bot.add_cog(MediaOnlyChannels(bot))