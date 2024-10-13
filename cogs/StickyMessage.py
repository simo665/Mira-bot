import discord
from discord.ext import commands
import os

class StickyMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sticky_messages = {}  # Dictionary to store sticky messages by channel ID
        self.sticky_message_file = "sticky_messages.txt"  # File to save the sticky messages

        # Load the sticky messages from the file when the cog is initialized
        self.load_sticky_messages()

    def load_sticky_messages(self):
        """Load the sticky messages from a file."""
        if os.path.exists(self.sticky_message_file):
            with open(self.sticky_message_file, "r") as file:
                for line in file:
                    channel_id, message = line.strip().split("|", 1)
                    self.sticky_messages[int(channel_id)] = message
            print("Loaded sticky messages from file.")

    def save_sticky_messages(self):
        """Save the sticky messages to a file."""
        with open(self.sticky_message_file, "w") as file:
            for channel_id, message in self.sticky_messages.items():
                file.write(f"{channel_id}|{message}\n")
        print("Saved sticky messages to file.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Avoid responding to the bot's own messages and ignore DMs
        if message.author == self.bot.user or isinstance(message.channel, discord.DMChannel):
            return
        
        # If there's a sticky message for this channel, delete and resend it
        if message.channel.id in self.sticky_messages:
            sticky_message_content = self.sticky_messages[message.channel.id]
            sticky_message = await message.channel.send(sticky_message_content)  # Resend the sticky message
            await sticky_message.delete()  # Optionally delete it right away if you want to keep it at the bottom.

    @commands.command()
    async def stick(self, ctx, *, message):
        """Stick a message to the current channel."""
        if ctx.channel.id in self.sticky_messages:
            await ctx.send("There is already a sticky message in this channel. Use `$unstick` to remove it first.")
            return
        
        self.sticky_messages[ctx.channel.id] = message  # Save the sticky message content
        await ctx.send(message)  # Send the sticky message
        self.save_sticky_messages()  # Save all sticky messages to the file
        await ctx.send("Sticky message set!")

    @commands.command()
    async def unstick(self, ctx):
        """Remove the sticky message from the current channel."""
        if ctx.channel.id in self.sticky_messages:
            del self.sticky_messages[ctx.channel.id]  # Remove the sticky message
            self.save_sticky_messages()  # Save all sticky messages to the file
            await ctx.send("Sticky message removed.")
        else:
            await ctx.send("There is no sticky message to remove in this channel.")

async def setup(bot):
    await bot.add_cog(StickyMessage(bot))
