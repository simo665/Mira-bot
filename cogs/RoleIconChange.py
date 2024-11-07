import discord
from discord.ext import commands
import aiohttp

class RoleIconManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="set_role_icon")
    @commands.has_permissions(manage_roles=True)
    async def set_role_icon(self, ctx, role: discord.Role):
        """Set a role icon using an image attachment."""
        
        # Check if the server meets the required boost level
        if ctx.guild.premium_tier < 2:
            await ctx.send("This server needs to be at least Boost Level 2 to set role icons.")
            return

        # Validate bot permissions
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send("I need 'Manage Roles' permission to set role icons.")
            return

        # Check if the message contains any attachments
        if not ctx.message.attachments:
            await ctx.send("Please attach an image to use as the role icon.")
            return

        # Get the first attachment
        attachment = ctx.message.attachments[0]
        
        # Check if the attachment is an image (based on the file extension)
        if not attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
            await ctx.send("The attached file is not a valid image. Please attach a PNG, JPG, JPEG, or GIF file.")
            return

        # Check if the image size is within the limit (256 KB)
        if attachment.size > 262144:  # 256 KB in bytes
            await ctx.send("The image is too large. Please provide an image smaller than 256 KB.")
            return

        # Download the image
        try:
            image_data = await attachment.read()

            # Attempt to set the role icon
            await role.edit(icon=image_data)
            await ctx.send(f"Role icon updated successfully for {role.name}!")

        except Exception as e:
            await ctx.send(f"An error occurred while setting the role icon: {e}")

    @set_role_icon.error
    async def set_role_icon_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need 'Manage Roles' permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the role and attach an image.")
        else:
            await ctx.send(f"An error occurred: {error}")

async def setup(bot):
    await bot.add_cog(RoleIconManager(bot))