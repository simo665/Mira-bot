import discord
from discord.ext import commands, tasks
import asyncio
import json
import os

class DMConversation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_conversations = {}  # Tracks active conversations between users
        self.inactivity_times = {}  # Tracks last activity time for conversations
        self.blocked_users = self.load_blocked_users()  # Load blocked users from the JSON file

    def load_blocked_users(self):
        """Load the list of blocked users from the JSON file."""
        if os.path.exists('user/dms_config.json'):
            with open('user/dms_config.json', 'r') as file:
                return json.load(file)
        return {}

    def save_blocked_users(self):
        """Save the blocked users list to the JSON file."""
        with open('user/dms_config.json', 'w') as file:
            json.dump(self.blocked_users, file, indent=4)

    @commands.command()
    async def start_dm(self, ctx, user: discord.User):
        """Starts a DM conversation with another user via the bot."""
        # Check if either user is blocked
        if ctx.author.id in self.blocked_users.get(user.id, []):
            await ctx.send(f"You are blocked by {user.name} and cannot start a DM with them.")
            return
        if user.id in self.blocked_users.get(ctx.author.id, []):
            await ctx.send(f"You have blocked {user.name} and cannot start a DM with them.")
            return

        if ctx.author.id in self.active_conversations or user.id in self.active_conversations:
            await ctx.send("Either you or the selected user is already in an active conversation. End it before starting a new one.")
            return

        # Initiate conversation
        self.active_conversations[ctx.author.id] = user.id
        self.active_conversations[user.id] = ctx.author.id
        self.inactivity_times[ctx.author.id] = asyncio.get_event_loop().time()  # Record current time for timeout tracking

        await ctx.send(f"Conversation started with {user.name}.")
        await user.send(f"{ctx.author.display_name} has started a conversation with you. You can now reply here.")

    @commands.command()
    async def close_dm(self, ctx):
        """Ends the current DM conversation."""
        user_id = self.active_conversations.get(ctx.author.id)
        
        if user_id:
            # Notify both users
            user = self.bot.get_user(user_id)
            if user:
                await user.send(f"{ctx.author.display_name} has ended the conversation.")
            await ctx.send(f"Conversation with {user.name if user else 'user'} has been closed.")

            # Remove both users from active conversation tracking
            del self.active_conversations[ctx.author.id]
            del self.active_conversations[user_id]
            del self.inactivity_times[ctx.author.id]

        else:
            await ctx.send("You have no active conversations to close.")

    @commands.command()
    async def block(self, ctx, user: discord.User):
        """Blocks a user from starting a DM conversation."""
        # Make sure the user is not trying to block themselves
        if ctx.author.id == user.id:
            await ctx.send("You cannot block yourself.")
            return

        # Block the user
        if user.id not in self.blocked_users:
            self.blocked_users[user.id] = []

        if ctx.author.id not in self.blocked_users[user.id]:
            self.blocked_users[user.id].append(ctx.author.id)
            self.save_blocked_users()
            await ctx.send(f"You have blocked {user.name}. They can no longer start a DM with you.")
            
            # If there is an active conversation with the blocked user, close it
            if user.id in self.active_conversations and self.active_conversations[user.id] == ctx.author.id:
                await self.close_dm(ctx)
            if ctx.author.id in self.active_conversations and self.active_conversations[ctx.author.id] == user.id:
                # Notify the other user that the conversation is closed due to blocking
                blocked_user = self.bot.get_user(user.id)
                if blocked_user:
                    await blocked_user.send(f"You have been blocked by {ctx.author.name}. The conversation has been closed.")
                await self.close_dm(ctx)
        else:
            await ctx.send(f"You have already blocked {user.name}.")

    @commands.command()
    async def unblock(self, ctx, user: discord.User):
        """Unblocks a user and allows them to start a DM conversation again."""
        # Make sure the user is not trying to unblock themselves
        if ctx.author.id == user.id:
            await ctx.send("You cannot unblock yourself.")
            return

        # Unblock the user
        if user.id in self.blocked_users and ctx.author.id in self.blocked_users[user.id]:
            self.blocked_users[user.id].remove(ctx.author.id)
            self.save_blocked_users()
            await ctx.send(f"You have unblocked {user.name}. They can now start a DM with you.")
        else:
            await ctx.send(f"You have not blocked {user.name}.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handles DM forwarding during active conversations."""
        if isinstance(message.channel, discord.DMChannel) and message.author.id in self.active_conversations:
            recipient_id = self.active_conversations[message.author.id]
            recipient = self.bot.get_user(recipient_id)
            if recipient:
                try:
                    await recipient.send(f"**{message.author.display_name}:** {message.content}")
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
