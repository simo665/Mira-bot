import discord
from discord.ext import commands, tasks
import asyncio

class DMConversation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_conversations = {}  # Tracks active conversations between users
        self.inactivity_times = {}  # Tracks last activity time for conversations

    @commands.command()
    async def start_dm(self, ctx, user: discord.User):
        """Starts a DM conversation with another user via the bot."""
        if ctx.author.id in self.active_conversations or user.id in self.active_conversations:
            await ctx.send("Either you or the selected user is already in an active conversation. End it before starting a new one.")
            return

        # Initiate conversation
        self.active_conversations[ctx.author.id] = user.id
        self.active_conversations[user.id] = ctx.author.id
        self.inactivity_times[ctx.author.id] = asyncio.get_event_loop().time()  # Record current time for timeout tracking

        await ctx.send(f"Conversation started with {user.name}.")
        await user.send(f"{ctx.author.name} has started a conversation with you. You can now reply here.")

    @commands.command()
    async def close_dm(self, ctx):
        """Ends the current DM conversation."""
        user_id = self.active_conversations.get(ctx.author.id)
        
        if user_id:
            # Notify both users
            user = self.bot.get_user(user_id)
            if user:
                await user.send(f"{ctx.author.name} has ended the conversation.")
            await ctx.send(f"Conversation with {user.name if user else 'user'} has been closed.")

            # Remove both users from active conversation tracking
            del self.active_conversations[ctx.author.id]
            del self.active_conversations[user_id]
            del self.inactivity_times[ctx.author.id]

        else:
            await ctx.send("You have no active conversations to close.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handles DM forwarding during active conversations."""
        if isinstance(message.channel, discord.DMChannel) and message.author.id in self.active_conversations:
            recipient_id = self.active_conversations[message.author.id]
            recipient = self.bot.get_user(recipient_id)
            if recipient:
                try:
                    await recipient.send(f"{message.author.name}: {message.content}")
                    self.inactivity_times[message.author.id] = asyncio.get_event_loop().time()  # Reset inactivity timer
                except discord.HTTPException:
                    await message.channel.send("Failed to forward the message.")
            else:
                await message.channel.send("The user is unavailable.")

    @tasks.loop(seconds=60)
    async def check_inactivity(self):
        """Checks for inactive conversations and closes them if inactive for over 5 minutes."""
        now = asyncio.get_event_loop().time()
        timeout_duration = 300  # 5 minutes in seconds
        to_close = []

        for user_id, last_active in self.inactivity_times.items():
            if now - last_active > timeout_duration:
                to_close.append(user_id)

        for user_id in to_close:
            recipient_id = self.active_conversations.get(user_id)
            if recipient_id:
                # Notify both users about the timeout closure
                user = self.bot.get_user(user_id)
                recipient = self.bot.get_user(recipient_id)
                if user:
                    await user.send("Your conversation has been closed due to inactivity.")
                if recipient:
                    await recipient.send("Your conversation has been closed due to inactivity.")
                
                # Clean up the conversation and inactivity tracking
                del self.active_conversations[user_id]
                del self.active_conversations[recipient_id]
                del self.inactivity_times[user_id]

    @commands.Cog.listener()
    async def on_ready(self):
        """Starts the inactivity check loop when the bot is ready."""
        self.check_inactivity.start()

async def setup(bot):
    await bot.add_cog(DMConversation(bot))
