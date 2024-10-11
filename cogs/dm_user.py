import discord
from discord.ext import commands
from config import TOKEN, intents
import datetime
import os

class dm_user(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_conversations = {}  # Dictionary to store user conversations
        self.first_time_dm = {}  # Dictionary to check if it's the first message from a user
        
        # Ensure logs directory exists
        self.logs_dir = 'logs'
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    def log_conversation(self, user_id, author_id, message):
        # File path for the user's log file
        log_file = os.path.join(self.logs_dir, f"user_{user_id}.txt")
        time = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        
        # Log the message to the user's log file
        with open(log_file, 'a') as f:
            f.write(f"[{time}] {author_id}: {message}\n")

    @commands.command()
    async def dm(self, ctx, user: discord.User, *, message):
        try:
            # Send DM to the user
            time = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
            await user.send(f"**{ctx.author}:** {message}\n-# This message is not appropriate? [Click to report](https://discord.com/channels/1264302631174668299/1276072321127550987)\n-# {time}")
            await ctx.send(f"Message sent successfully to {user.name}")
            
            if user.id not in self.first_time_dm:
                await user.send("You can reply to this message by just sending a message here.")
                self.first_time_dm[user.id] = True

            # Track the conversation and log it
            self.active_conversations[user.id] = ctx.author.id
            self.log_conversation(user.id, ctx.author.id, message)

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
                        await recipient.send(f"**{message.author}:** {message.content}\n-# do this cmd to reply `$dm {message.author} (your message here)`. {time}")
                        await message.channel.send(f"Your reply has been forwarded.")
                        
                        # Log the reply
                        self.log_conversation(message.author.id, recipient_id, message.content)
                    except discord.HTTPException:
                        await message.channel.send("Failed to forward the message.")
                else:
                    await message.channel.send("Couldn't find the original user.")
            else:
                if not "$dm" in message.content:
                    await message.channel.send("No active conversation to reply to.")
                else:
                    pass 

async def setup(bot):
    await bot.add_cog(dm_user(bot))
