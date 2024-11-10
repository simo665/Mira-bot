import discord
from discord.ext import commands
import os
import json

class StickyMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sticky_messages = {}
        self.file_path = "user/sticky/sticky_messages.json"
        self.load_sticky_messages()
        self.bot.loop.create_task(self.send_sticky_messages_on_startup())

    def load_sticky_messages(self):
        """Load sticky messages from the file."""
        if not os.path.exists("user/sticky"):
            os.makedirs("user/sticky")

        # Ensure the file exists, and if not, initialize an empty dictionary
        if os.path.isfile(self.file_path):
            try:
                with open(self.file_path, "r") as file:
                    self.sticky_messages = json.load(file)
            except json.JSONDecodeError:
                # Handle case where the file is empty or corrupted
                self.sticky_messages = {}
        else:
            # If the file doesn't exist, initialize it with an empty dictionary
            self.sticky_messages = {}

    def save_sticky_messages(self):
        """Save sticky messages to the file."""
        with open(self.file_path, "w") as file:
            json.dump(self.sticky_messages, file, indent=4)

    async def send_sticky_messages_on_startup(self):
        """Resend sticky messages on bot startup."""
        await self.bot.wait_until_ready()  # Ensure the bot is fully ready
        for channel_id, message_data in self.sticky_messages.items():
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                try:
                    # Send the sticky message and update the message ID
                    sent_message = await channel.send(message_data["content"])
                    self.sticky_messages[channel_id]["message_id"] = sent_message.id
                except discord.Forbidden:
                    print(f"Missing permissions to send message in {channel.name}")
        # Save the updated message IDs after resending
        self.save_sticky_messages()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if str(message.channel.id) in self.sticky_messages:
            try:
                sticky_message_id = self.sticky_messages[str(message.channel.id)]["message_id"]
                sticky_message = await message.channel.fetch_message(sticky_message_id)
                await sticky_message.delete()
            except (discord.NotFound, discord.Forbidden):
                pass

            new_message = await message.channel.send(self.sticky_messages[str(message.channel.id)]["content"])
            self.sticky_messages[str(message.channel.id)]["message_id"] = new_message.id
            self.save_sticky_messages()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def stick(self, ctx, *, message):
        """Stick a message to the bottom of the channel."""
        if str(ctx.channel.id) in self.sticky_messages:
            await ctx.send("There is already a sticky message in this channel. Use `$unstick` to remove it first.")
            return

        new_message = await ctx.send(message)
        self.sticky_messages[str(ctx.channel.id)] = {
            "message_id": new_message.id,
            "content": message
        }
        self.save_sticky_messages()
        await ctx.message.add_reaction("<a:heart:1294048146682417224>")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unstick(self, ctx):
        """Remove the sticky message."""
        if str(ctx.channel.id) in self.sticky_messages:
            try:
                sticky_message_id = self.sticky_messages[str(ctx.channel.id)]["message_id"]
                sticky_message = await ctx.channel.fetch_message(sticky_message_id)
                await sticky_message.delete()
            except (discord.NotFound, discord.Forbidden):
                pass

            del self.sticky_messages[str(ctx.channel.id)]
            self.save_sticky_messages()
            await ctx.message.add_reaction("<a:broken_heart:1294048158766202921>")
        else:
            await ctx.send("There is no sticky message to remove in this channel.")

async def setup(bot):
    await bot.add_cog(StickyMessage(bot))