import discord
from discord.ext import commands

class Boosters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boosters_role_id = 1264340179297243279  # Boosters role ID
        self.channel_id = None

    async def create_boosters_embed(self, guild):
        """Create and return the embed with the list of boosters."""
        boosters_role = guild.get_role(self.boosters_role_id)
        if boosters_role:
            # Get members who have the boosters role
            boosters_names = [member.name for member in guild.members if boosters_role in member.roles]
            embed = discord.Embed(title="Boosters", description="\n".join(boosters_names) if boosters_names else "No boosters yet.")
            return embed
        return None

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Check if a user gained or lost the boosters role and update the boosters list."""
        # Check if the user gained or lost the boosters role
        before_boosters = before.get_role(self.boosters_role_id)
        after_boosters = after.get_role(self.boosters_role_id)

        if before_boosters != after_boosters:
            if self.channel_id:
                channel = self.bot.get_channel(self.channel_id)
                if channel:
                    embed = await self.create_boosters_embed(after.guild)
                    message = await channel.fetch_message(self.channel_id)
                    await message.edit(embed=embed)

    @commands.command()
    async def set_boosters_channel(self, ctx, channel: discord.TextChannel):
        """Command to set the channel where the boosters list will be displayed."""
        self.channel_id = channel.id
        embed = await self.create_boosters_embed(ctx.guild)
        if embed:
            message = await channel.send(embed=embed)
            self.channel_id = message.channel.id  # Save the channel ID to update later

    @commands.command()
    async def test_boosters(self, ctx):
        """Command to test if the boosters system is working."""
        if self.channel_id:
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                embed = await self.create_boosters_embed(ctx.guild)
                message = await channel.fetch_message(self.channel_id)
                await message.edit(embed=embed)
                await ctx.send("Boosters embed updated successfully.")
            else:
                await ctx.send("Failed to fetch the channel.")
        else:
            await ctx.send("The boosters channel has not been set.")

async def setup(bot):
    await bot.add_cog(Boosters(bot))
