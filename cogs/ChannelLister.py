import discord
from discord.ext import commands

class ChannelLister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="channelsL")
    async def list_channels(self, ctx):
        """Lists all channels organized by category in a tree-like structure."""
        channel_output = ""

        # Loop through each category
        for category in ctx.guild.categories:
            channel_output += f"**{category.name}**\n"  # Add the category name
            
            # Add each text/voice channel under this category
            for channel in category.channels:
                channel_output += f"└ {channel.name}\n"
        
        # Add uncategorized channels, if any
        uncategorized_channels = [channel for channel in ctx.guild.channels if channel.category is None]
        if uncategorized_channels:
            channel_output += "\n**Uncategorized Channels**\n"
            for channel in uncategorized_channels:
                channel_output += f"└ {channel.name}\n"
        
        # Send the organized channel list
        await ctx.send(channel_output or "No channels found in this server.")

async def setup(bot):
    await bot.add_cog(ChannelLister(bot))