import discord
from discord.ext import commands

class StickyMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sticky_message = None  # Variable to store the sticky message content
        self.sticky_message_content = None  # Variable to store the actual message content

    @commands.Cog.listener()
    async def on_message(self, message):
        # Avoid responding to the bot's own messages
        if message.author == self.bot.user:
            return
        
        # If there's a sticky message, delete and resend it
        if self.sticky_message and self.sticky_message_content:
            await self.sticky_message.delete()  # Delete the previous sticky message
            self.sticky_message = await message.channel.send(self.sticky_message_content)  # Resend the sticky message

    @commands.command()
    async def stick(self, ctx, *, message):
        """Stick a message to the bottom of the channel."""
        if self.sticky_message:
            await ctx.send("There is already a sticky message. Use `$unstick` to remove it first.")
            return
        
        self.sticky_message_content = message  # Save the sticky message content
        self.sticky_message = await ctx.send(message)  # Send the sticky message
        await ctx.send("Sticky message set!")

    @commands.command()
    async def unstick(self, ctx):
        """Remove the sticky message."""
        if self.sticky_message:
            await self.sticky_message.delete()  # Delete the sticky message
            self.sticky_message = None  # Reset the sticky message variable
            self.sticky_message_content = None  # Reset the sticky message content
            await ctx.send("Sticky message removed.")
        else:
            await ctx.send("There is no sticky message to remove.")

async def setup(bot):
    await bot.add_cog(StickyMessage(bot))
