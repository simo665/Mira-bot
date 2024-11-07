import discord
from discord.ext import commands
import aiohttp
from io import BytesIO
from PIL import Image
import requests

class RoleIconManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_role_icon")
    @commands.has_permissions(manage_roles=True)
    async def set_role_icon(self, ctx, role: discord.Role, icon_url: str):
        """Set a role icon using an image URL.
        
        Args:
            role (discord.Role): The role to update.
            icon_url (str): URL of the image to set as the icon.
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

                            # Check the image size (should be below 256 KB)
                            if len(image_data) > 256 * 1024:
                                await ctx.send("The image is too large. Please use an image under 256 KB.")
                                return

                            # Check the image dimensions using PIL
                            image = Image.open(BytesIO(image_data))
                            width, height = image.size
                            if width > 512 or height > 512:
                                await ctx.send("The image dimensions are too large. Please use an image with dimensions of 512x512 or smaller.")
                                return

                            # If the image is valid, set it as the role's icon
                            await role.edit(icon=image_data)
                            await ctx.send(f"Role icon updated for {role.name} successfully!")
                        else:
                            await ctx.send("Failed to fetch the image from the provided URL.")
            except Exception as e:
                await ctx.send(f"An error occurred while setting the role icon: {e}")

    @set_role_icon.error
    async def set_role_icon_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need 'Manage Roles' permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify both the role and an image URL.")
        else:
            await ctx.send(f"An error occurred: {error}")

async def setup(bot):
    await bot.add_cog(RoleIconManager(bot))