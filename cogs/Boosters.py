import discord
from discord.ext import commands, tasks
import json
import os

class Boosters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boosters_role_id = 1264340179297243279  # The "boosters" role ID
        self.channel_id = None  # Channel to send the embed
        self.data_file = 'data.json'  # File to save the channel ID
        self.load_data()
        self.update_boosters_embed.start()  # Start the task to update the boosters embed

    def load_data(self):
        """Load saved data from file (channel_id)."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.channel_id = data.get("channel_id", None)

    def save_data(self):
        """Save the channel ID to a file."""
        with open(self.data_file, 'w') as f:
            json.dump({"channel_id": self.channel_id}, f)

    def create_boosters_embed(self):
        """Create the embed with boosters and perks."""
        # Get the list of users with the boosters role
        guild = self.bot.get_guild(1264302631174668299)  # Replace with your server ID
        boosters_role = guild.get_role(self.boosters_role_id)
        boosters = [member.mention for member in guild.members if boosters_role in member.roles]

        # Perks
        perks = """
## <:02SataniaThumbsUp:1264963006102634547> Boost Perks <:01ZeroTwo_heartlove:1264960807855460363>
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

        """

        embed = discord.Embed(title="Boosters and Perks", description=perks, color=discord.Color.blue())
        embed.add_field(name="Awesome Boosters!! <:ahriheart:1304359317050490881>", value="\n<:01ZeroTwo_heartlove:1264960807855460363> - ".join(boosters) if boosters else "No boosters yet!", inline=False)
        return embed

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Listener to update the embed when a member gains or loses the boosters role."""
        if self.boosters_role_id in [role.id for role in after.roles]:
            # The user has gained the boosters role
            await self.update_embed()
        elif self.boosters_role_id not in [role.id for role in before.roles]:
            # The user has lost the boosters role
            await self.update_embed()

    @commands.command()
    async def bc(self, ctx, channel: discord.TextChannel):
        """Set the channel where the boosters embed will be posted."""
        self.channel_id = channel.id
        self.save_data()
        embed = self.create_boosters_embed()
        await channel.send(embed=embed)
        await ctx.send(f"Boosters list will now be posted in {channel.mention}")

    async def update_embed(self):
        """Update the boosters embed."""
        if not self.channel_id:
            return  # If no channel is set, do nothing

        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return  # If the channel doesn't exist, do nothing

        # Create the updated embed
        embed = self.create_boosters_embed()

        # Check if an embed already exists in the channel
        async for message in channel.history(limit=5):
            if message.author == self.bot.user and message.embeds:
                await message.edit(embed=embed)
                return

        # Send a new embed if no previous embed exists
        await channel.send(embed=embed)

    @tasks.loop(minutes=5)
    async def update_boosters_embed(self):
        """Regularly update the boosters embed."""
        await self.update_embed()

async def setup(bot):
    await bot.add_cog(Boosters(bot))
