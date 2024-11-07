import discord
from discord.ext import commands
import aiohttp

class RoleIconChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ricon")
    @commands.has_permissions(manage_roles=True)  # Ensure only users with 'manage_roles' permission can use this
    async def change_role_icon(self, ctx, role: discord.Role, icon: str):
        """
        Changes the icon of a role using an emoji or image URL.
        Usage: !change_role_icon @Role <emoji or image URL>
        """
        # If it's an emoji
        if icon.startswith("<:") or icon.startswith("<a:"):
            # Try to set it as an emoji icon
            emoji_id = int(icon.split(":")[-1][:-1])
            emoji = self.bot.get_emoji(emoji_id)
            if emoji:
                await role.edit(icon=emoji)
                await ctx.send(f"Role icon changed successfully to {emoji}!")
            else:
                await ctx.send("Couldn't find the emoji. Please try another one.")
        
        # If it's an image URL
        elif icon.startswith("http"):
            async with aiohttp.ClientSession() as session:
                async with session.get(icon) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        await role.edit(icon=image_data)
                        await ctx.send("Role icon changed successfully!")
                    else:
                        await ctx.send("Failed to fetch image from the URL. Please check the link.")

        # Invalid input
        else:
            await ctx.send("Please provide a valid emoji or image URL.")

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(RoleIconChanger(bot))