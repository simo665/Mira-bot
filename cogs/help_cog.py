import discord
from discord.ext import commands

class CustomHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", color=discord.Color.blue())

        # Add commands to the embed manually
        embed.add_field(name="`showtime`", value="Displays the current time and updates every second.", inline=False)
        embed.add_field(name="`stick`", value="Sticks a message to the bottom of the channel.", inline=False)
        embed.add_field(name="`unstick`", value="Removes the sticky message from the channel.", inline=False)

        # Optional: Add commands from the mapping
        for cog, commands in mapping.items():
            if cog is not None:  # Skip NoneType (uncategorized commands)
                command_list = [f"`{command.name}` - {command.help}" for command in commands if command.help]
                command_list_str = "\n".join(command_list) if command_list else "No commands available."
                embed.add_field(name=cog.qualified_name, value=command_list_str, inline=False)

        await self.get_destination().send(embed=embed)

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = CustomHelp()  # Set custom help command

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
