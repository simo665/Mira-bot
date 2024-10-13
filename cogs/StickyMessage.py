import discord
from discord.ext import commands
import os

class StickyMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sticky_messages = {}  # Dictionary to store sticky messages by channel ID
        self.sticky_message_objects = {}  # Dictionary to store sticky message objects by channel ID
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

            try:
                # Attempt to delete the previous sticky message if it exists
                if message.channel.id in self.sticky_message_objects:
                    try:
                        await self.sticky_message_objects[message.channel.id].delete()
                    except discord.NotFound:
                        print(f"Previous sticky message in {message.channel.name} was already deleted.")
                    except discord.Forbidden:
                        print(f"Missing permissions to delete messages in {message.channel.name}")

                # Send the sticky message
                self.sticky_message_objects[message.channel.id] = await message.channel.send(sticky_message_content)  
            except discord.Forbidden:
                print(f"Missing permissions to send messages in {message.channel.name}")
            except Exception as e:
                print(f"An error occurred while sending the sticky message: {e}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def stick(self, ctx, *, message):
        """Stick a message to the current channel."""
        if ctx.channel.id in self.sticky_messages:
            await ctx.send("There is already a sticky message in this channel. Use `$unstick` to remove it first.")
            return
        
        self.sticky_messages[ctx.channel.id] = message  # Save the sticky message content
        
        # Check if the bot has permission to send messages
        if ctx.channel.permissions_for(ctx.guild.me).send_messages:
            self.sticky_message_objects[ctx.channel.id] = await ctx.send(message)  # Send the sticky message
            self.save_sticky_messages()  # Save all sticky messages to the file
            await ctx.add_reaction("<a:heart:1294048146682417224>")
        else:
            await ctx.send("I do not have permission to send messages in this channel.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unstick(self, ctx):
        """Remove the sticky message from the current channel."""
        if ctx.channel.id in self.sticky_messages:
            del self.sticky_messages[ctx.channel.id]  # Remove the sticky message
            if ctx.channel.id in self.sticky_message_objects:
                try:
                    await self.sticky_message_objects[ctx.channel.id].delete()  # Delete the sticky message if it exists
                except discord.NotFound:
                    print("Sticky message was already deleted.")
                del self.sticky_message_objects[ctx.channel.id]  # Remove from the objects dictionary
            self.save_sticky_messages()  # Save all sticky messages to the file
            await ctx.add_reaction("<a:heart:1294048146682417224>")
        else:
            await ctx.send("There is no sticky message to remove in this channel.")

async def setup(bot):
    await bot.add_cog(StickyMessage(bot))
