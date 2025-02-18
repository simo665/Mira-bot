import discord
from discord.ext import commands
import asyncio

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.owner_id = 1276601420652482643
        self.role_id = 1275849704197853276  # Replace with the role ID
        self.embed_message = None  # Stores the embed message for updates
        self.channel_id = 1308932001277149204  # Replace with your target channel ID
        self.wifi_online = "<:WiFi_Online:1308933707255775242>"
        self.wifi_offline = "<:WiFi_Offline:1308933727367336087>"
        self.online_icon = "<:online:1308942881829945395>"
        self.dnd_icon = "<:dnd:1308941478554505216>"
        self.invisible_icon = "<:invisible:1308941489656692807>"
        self.idle_icon = "<:idle_gray:1308948721207087194>"

    async def on_ready(self):
        """Check if the embed exists and update it when the bot is ready."""
        guild = self.bot.guilds[0]  # Assumes the bot is in at least one server
        await self.update_status_embed(guild)

    async def update_status_embed(self, guild):
        """Updates the status embed."""
        role = guild.get_role(self.role_id)
        if not role:
            print(f"Role with ID {self.role_id} not found.")
            return

        channel = guild.get_channel(self.channel_id)
        if not channel:
            print(f"Channel with ID {self.channel_id} not found.")
            return

        # Look for an existing embed message
        if not self.embed_message:
            async for message in channel.history(limit=10):  # Check last 10 messages
                if message.embeds:
                    self.embed_message = message
                    break

        available_mods = []
        unavailable_mods = []

        for member in role.members:
            if member.status == discord.Status.online:
                available_mods.append(f"> {self.online_icon} - {member.mention} *({member.name})*")
            elif member.status == discord.Status.dnd:
                unavailable_mods.append(f"> {self.dnd_icon} - {member.mention} *({member.name})*")
            elif member.status == discord.Status.idle:
                available_mods.append(f"> {self.idle_icon} - {member.mention} *({member.name})*")
            else:
                # Offline members
                unavailable_mods.append(f"> {self.invisible_icon} - {member.mention} *({member.name})*")

        # Create the embed
        embed = discord.Embed(
            title="Moderation Status",
            description="This list updates dynamically.",
            color=discord.Color.green(),
        )
        embed.add_field(name=f"{self.wifi_online} Available Mods", value="\n".join(available_mods) or "None", inline=False)
        embed.add_field(name=f"{self.wifi_offline} Unavailable Mods", value="\n".join(unavailable_mods) or "None", inline=False)

        # Update or send the embed
        if self.embed_message:
            try:
                await self.embed_message.edit(embed=embed)
            except discord.NotFound:
                # If the message was deleted, reset it
                self.embed_message = await channel.send(embed=embed)
        else:
            self.embed_message = await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        """Listener for member status updates."""
        guild = after.guild
        role = guild.get_role(self.role_id)
        if role and role in after.roles:
            # Schedule the update after a delay using create_task
            await self.bot.loop.create_task(self.delayed_update(guild))

    async def delayed_update(self, guild):
        """Delays the embed update to avoid rapid status update conflicts."""
        await asyncio.sleep(5)  # Delay
        await self.update_status_embed(guild)

# Setup function to add the cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
