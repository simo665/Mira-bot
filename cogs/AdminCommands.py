import discord
from discord.ext import commands, tasks

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Your user ID as the bot owner
        self.owner_id = 1276601420652482643
        self.role_id = 1275849704197853276  # Replace with the role ID
        self.embed_message = None  # Stores the embed message for updates
        self.channel_id = 1308932001277149204  # Replace with your target channel ID
        self.update_status_embed.start()  # Start the task to update the embed every 15 minutes
        self.wifi_online = "<:WiFi_Online:1308933707255775242>"
        self.wifi_offline = "<:WiFi_Offline:1308933727367336087>"
        self.online_icon = "<:online:1308942881829945395>"
        self.dnd_icon = "<:dnd:1308941478554505216>"
        self.invisible_icon = "<:invisible:1308941489656692807>"
        self.idle_icon = "<:Idle:1308947018550480936>"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages sent by the bot itself
        if message.author == self.bot.user:
            return
        
        # Check if the bot is mentioned
        if self.bot.user in message.mentions:
            # Split the message to get the command
            content = message.content.split()
            if len(content) > 1 and content[1].lower() == 'leave':
                # Check if the user ID matches the owner ID
                if message.author.id == self.owner_id:
                    await message.channel.send("Alright, Jenna. Thanks for the good times here. Goodbye!")
                    await message.guild.leave()
                else:
                    await message.channel.send("You do not have permission to make me leave the server.")

# _________
    @tasks.loop(minutes=5)
    async def update_status_embed(self):
        """Task that updates the status embed every 15 minutes."""
        guild = self.bot.guilds[0]  # Replace with `self.bot.get_guild(ID)` if using multiple guilds
        channel = guild.get_channel(self.channel_id)

        if not channel:
            print(f"Channel with ID {self.channel_id} not found.")
            return

        role = guild.get_role(self.role_id)
        if not role:
            print(f"Role with ID {self.role_id} not found.")
            return

        available_mods = []
        unavailable_mods = []

        for member in role.members:
            if member.status == discord.Status.online:
                available_mods.append(f"{self.online_icon} - {member.display_name}")
            elif member.status == discord.Status.dnd:
                unavailable_mods.append(f"{self.dnd_icon} - {member.display_name}")
            elif member.status == discord.Status.idle:
                available_mods.append(f"{self.idle_icon} - {member.display_name}")
            else:
                # Offline members
                unavailable_mods.append(f"{self.invisible_icon} - {member.display_name}")

        # Create the embed
        embed = discord.Embed(
            title="Moderation Status",
            description="This list updates every 5 minutes.",
            color=discord.Color.green(),
        )
        embed.add_field(name=f"{self.wifi_online} Available Mods", value="\n".join(available_mods) or "None", inline=False)
        embed.add_field(name=f"{self.wifi_offline} Unavailable Mods", value="\n".join(unavailable_mods) or "None", inline=False)

        if self.embed_message:
            try:
                await self.embed_message.edit(embed=embed)
            except discord.NotFound:
                # If the message was deleted, reset it
                self.embed_message = await channel.send(embed=embed)
        else:
            self.embed_message = await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def init_status_embed(self, ctx):
        """Initialize the embed in the target channel."""
        guild = ctx.guild
        role = guild.get_role(self.role_id)
        if not role:
            await ctx.send(f"Role with ID {self.role_id} not found.")
            return

        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            await ctx.send(f"Channel with ID {self.channel_id} not found.")
            return

        # Generate the initial embed
        active_mods = [member.display_name for member in role.members if member.status in (discord.Status.online, discord.Status.idle, discord.Status.dnd)]
        inactive_mods = [member.display_name for member in role.members if member.status == discord.Status.offline]

        embed = discord.Embed(
            title="Moderation Status",
            description="This list updates every 15 minutes.",
            color=discord.Color.blue(),
        )
        embed.add_field(name=f"{self.wifi_online} Available Mods", value="\n".join(active_mods) or "None", inline=False)
        embed.add_field(name=f"{self.wifi_offline} Unavailable Mods", value="\n".join(inactive_mods) or "None", inline=False)
        # Send the embed and save the message for updates
        self.embed_message = await channel.send(embed=embed)
        await ctx.send("Moderation status embed initialized and updates scheduled!")

    @update_status_embed.before_loop
    async def before_update_status_embed(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()


# _______




# Setup function to add the cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
