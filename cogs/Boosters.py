import discord
from discord.ext import commands
import json
import os

class Boosters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boosters_file = "boosters.json"
        self.channel_id = None
        self.boosters_list = self.load_boosters()

    def load_boosters(self):
        """Load the boosters from the JSON file."""
        if os.path.exists(self.boosters_file):
            with open(self.boosters_file, "r") as f:
                return json.load(f)
        return []

    def save_boosters(self):
        """Save the boosters list to a JSON file."""
        with open(self.boosters_file, "w") as f:
            json.dump(self.boosters_list, f)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Check if a user boosted the server and update the boosters list."""
        if before.premium_since != after.premium_since:
            if after.premium_since:  # Boosted
                if after.id not in self.boosters_list:
                    self.boosters_list.append(after.id)
                    self.save_boosters()
            else:  # Unboosted
                if after.id in self.boosters_list:
                    self.boosters_list.remove(after.id)
                    self.save_boosters()

            # Update the embed in the set channel
            if self.channel_id:
                channel = self.bot.get_channel(self.channel_id)
                if channel:
                    embed = await self.create_boosters_embed()
                    message = await channel.fetch_message(self.channel_id)
                    await message.edit(embed=embed)

    async def create_boosters_embed(self):
        """Create and return the embed with the list of boosters."""
        boosters_names = [self.bot.get_user(user_id).name for user_id in self.boosters_list]
        embed = discord.Embed(title="Boosters", description="\n".join(boosters_names) if boosters_names else "No boosters yet.")
        return embed

    @commands.command("bchannel")
    async def set_boosters_channel(self, ctx, channel: discord.TextChannel):
        """Command to set the channel where the boosters list will be displayed."""
        self.channel_id = channel.id
        embed = await self.create_boosters_embed()
        message = await channel.send(embed=embed)
        self.channel_id = message.channel.id  # Save the channel ID to update later

    @commands.command()
    async def test_boosters(self, ctx):
        """Command to test if the boosters system is working."""
        if self.channel_id:
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                embed = await self.create_boosters_embed()
                message = await channel.fetch_message(self.channel_id)
                await message.edit(embed=embed)
                await ctx.send("Boosters embed updated successfully.")
            else:
                await ctx.send("Failed to fetch the channel.")
        else:
            await ctx.send("The boosters channel has not been set.")

async def setup(bot):
    await bot.add_cog(Boosters(bot))
