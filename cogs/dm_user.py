import discord
from discord.ext import commands
import datetime

class dm_user(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_conversations = {}  # Dictionary to store user conversations
        self.first_time_dm = {}  # Dictionary to check if it's the first message from a user

    # Command to send a DM
    @commands.command()
    async def dm(self, ctx, user: discord.User, *, message):
        try:
            # Get the current time
            time = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
            # Send the DM to the user
            await user.send(f"**{ctx.author}:** {message}\n-# This message is not appropriate? [Click to report](https://discord.com/channels/1264302631174668299/1276072321127550987)\n-# {time}")
            await ctx.send(f"Message sent successfully to {user.name}")

            # Check if it's the user's first message
            if user.id not in self.first_time_dm:
                await user.send("You can reply to this message by just sending a message here.")
                self.first_time_dm[user.id] = True

            # Track the conversation
            self.active_conversations[user.id] = ctx.author.id

        except discord.Forbidden:
            await ctx.send(f"Couldn't send a DM to {user.name}. They may have DMs disabled or blocked the bot.")
        except discord.HTTPException:
            await ctx.send("Failed to send the message due to an API error.")

    # Listen for incoming direct messages
    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if it's a direct message and not from a bot
        if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
            recipient_id = self.active_conversations.get(message.author.id)

            # If the user is replying to someone
            if recipient_id:
                recipient = self.bot.get_user(recipient_id)
                if recipient:
                    try:
                        time = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
                        # Forward the reply to the original sender
                        await recipient.send(f"**{message.author}:** {message.content}\n-# To reply, use the `$dm {message.author} (your message here)` command.\n-# {time}")
                        await message.channel.send("Your reply has been forwarded.")
                    except discord.HTTPException:
                        await message.channel.send("Failed to forward the message.")
                else:
                    await message.channel.send("Couldn't find the original user.")
            else:
                if "$dm" not in message.content:
                    await message.channel.send("No active conversation to reply to.")

async def setup(bot):
    await bot.add_cog(dm_user(bot))
