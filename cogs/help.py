import discord
from discord.ext import commands

class CustomHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        """Displays a list of all available commands."""
        embed = discord.Embed(
            title="Bot Commands",
            description="Here are all the commands available in the bot:",
            color=discord.Color.blue()
        )

        for cog_name, cog in self.bot.cogs.items():
            # Get commands in each cog
            commands_list = cog.get_commands()
            commands_description = ""
            for command in commands_list:
                if not command.hidden:
                    commands_description += f"`{ctx.prefix}{command.name}` - {command.help}\n"

            if commands_description:
                embed.add_field(name=f"**{cog_name}**", value=commands_description, inline=False)

        # Adding commands not in cogs
        other_commands = [cmd for cmd in self.bot.commands if not cmd.cog and not cmd.hidden]
        if other_commands:
            other_commands_description = "\n".join(
                [f"`{ctx.prefix}{cmd.name}` - {cmd.help}" for cmd in other_commands]
            )
            embed.add_field(name="**Other Commands**", value=other_commands_description, inline=False)

        embed.set_footer(text=f"Use {ctx.prefix}help <command> for more details on each command.")
        await ctx.send(embed=embed)

async def setup(bot):
    bot.remove_command("help")  # Remove the default help command
    await bot.add_cog(CustomHelp(bot))
