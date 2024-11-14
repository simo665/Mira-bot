import discord
from discord.ext import commands

class Boosters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boosters_role_id = 1264340179297243279  # Boosters role ID
        self.channel_id = None

    async def create_boosters_embed(self, guild):
        """Create and return the embed with the list of boosters and the perks."""
        boosters_role = guild.get_role(self.boosters_role_id)
        if boosters_role:
            # Get members who have the boosters role
            boosters_names = [f"<@{member.id}>" for member in guild.members if boosters_role in member.roles]
            
            # Define the perks section
            perks_section = """
            ## Boosts perks:
            _ _ 
            <:02_animegirlpeek:1264992017826713725> **1 Boost:**
            - <:emoji_274:1272175998733123585> **Leveling Boost x30**
            - <:emoji_274:1272175998733123585> **Skip 5 Levels**
            - <:emoji_274:1272175998733123585> **Media Permission**
            - <:emoji_274:1272175998733123585> **Exclusive Booster Role**

            <:02_animegirloop:1264961707680202802> **2 Boosts:**
            - <:emoji_274:1272175998733123585> **All previous perks +**:
            - <:emoji_274:1272175998733123585> **Skip 10 Levels**
            - <:emoji_274:1272175998733123585> **Two Custom Emojis**
            - <:emoji_274:1272175998733123585> **VIP Role**

            <:02_animegirlyay:1264992016605909076> **3 or More Boosts:**
            - <:emoji_274:1272175998733123585> **All previous perks +**:
            - <:emoji_274:1272175998733123585> **1 Custom Role**
            - <:emoji_274:1272175998733123585> **1 Custom VC Channel**

            > Your support helps our community grow! Boosting gives you awesome perks and helps create a better server for everyone!

            -# **Note**: You get "Media Permission" automatically, but for other perks, we will grant them manually. Please create a **[ticket](https://discord.com/channels/1264302631174668299/1264350097118859294)** to claim your perks.
            """
            
            # Append the list of boosters names
            boosters_list = "\n".join(boosters_names) if boosters_names else "No boosters yet."
            
            embed = discord.Embed(title="Boosters", description=perks_section)
            embed.add_field(name="Boosters", value=boosters_list, inline=False)
            
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
