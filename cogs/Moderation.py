import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nick")
    @commands.has_permissions(manage_nicknames=True)  # Requires 'Manage Nicknames' permission
    async def change_nickname(self, ctx, user: discord.Member, *, nickname: str):
        """Changes the nickname of a specified user."""
        try:
            # Attempt to change the user's nickname
            await user.edit(nick=nickname)
            await ctx.send(f"Successfully changed {user.mention}'s nickname to '{nickname}'.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to change this user's nickname.")
        except discord.HTTPException:
            await ctx.send("An error occurred while trying to change the nickname.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
