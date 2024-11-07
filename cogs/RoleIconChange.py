import discord
from discord.ext import commands
import aiohttp

class RoleIconManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ricon")
    @commands.has_permissions(manage_roles=True)
    async def set_role_icon(self, ctx, role: discord.Role, icon_url: str):
        """Set a role icon using an image URL or emoji.
        
        Args:
            role (discord.Role): The role to update.
            icon_url (str): URL of the image or emoji to set as the icon.
        """
        # Check if the server meets the required boost level
        if ctx.guild.premium_tier < 2:
            await ctx.send("This server needs to be at least Boost Level 2 to set role icons.")
            return

        # Validate bot permissions
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send("I need 'Manage Roles' permission to set role icons.")
            return

        # Attempt to set the role icon
        if icon_url.startswith("http"):  # If an image URL is provided
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(icon_url) as response:
                        if response.status == 200:
                            image_data = await response.read()
                            await role.edit(icon=image_data)
                            await ctx.send(f"Role icon updated for {role.name} successfully!")
                        else:
                            await ctx.send("Failed to fetch the image from the provided URL.")
            except Exception as e:
                await ctx.send(f"An error occurred while setting the role icon: {e}")

        else:  # If an emoji is provided
            try:
                emoji = await commands.EmojiConverter().convert(ctx, icon_url)
                if isinstance(emoji, discord.Emoji):  # Check if it's a custom emoji
                    await role.edit(icon=emoji.url)
                    await ctx.send(f"Role icon updated for {role.name} successfully with emoji!")
                else:
                    await ctx.send("Only custom emojis can be used as role icons.")
            except commands.errors.BadArgument:
                await ctx.send("Invalid emoji or URL. Please provide a valid image URL or custom emoji.")

    @set_role_icon.error
    async def set_role_icon_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need 'Manage Roles' permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify both the role and an icon URL or emoji.")
        else:
            await ctx.send(f"An error occurred: {error}")

async def setup(bot):
    await bot.add_cog(RoleIconManager(bot))