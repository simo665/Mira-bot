
import discord
from discord.ext import commands
import io

class RoleIconCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setroleicon(self, ctx, role: discord.Role):
        """Change the icon of the given role based on an attached image."""
        # Check if there's an image attached
        if not ctx.message.attachments:
            await ctx.send("Please attach an image to set as the role icon.")
            return

        attachment = ctx.message.attachments[0]

        # Ensure the attachment is an image (check for common image extensions)
        if not attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
            await ctx.send("The attached file is not a valid image. Please upload a PNG, JPG, or GIF.")
            return

        try:
            # Fetch the image from the attachment
            image_data = await attachment.read()
            image_file = io.BytesIO(image_data)

            # Update the role's icon
            await role.edit(icon=image_file)
            await ctx.send(f"Role icon updated successfully for {role.name}!")
        except discord.Forbidden:
            await ctx.send("I do not have permission to edit role icons.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred while updating the role icon: {e}")
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}")

    @setroleicon.error
    async def setroleicon_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You must specify a role to change its icon.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Please provide a valid role.")
        else:
            await ctx.send(f"An error occurred: {error}")

async def setup(bot):
    await bot.add_cog(RoleIconCog(bot))