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
        self.used_dm_users = self.load_used_dm_users()  # Load users who have used DM feature

    def load_used_dm_users(self):
        """Loads users who have already used the DM feature."""
        if os.path.exists('user/dms_config.json'):
            with open('user/dms_config.json', 'r') as f:
                return json.load(f)
        return {}

    def save_used_dm_users(self):
        """Saves the list of users who have used the DM feature."""
        with open('user/dms_config.json', 'w') as f:
            json.dump(self.used_dm_users, f)

    @commands.command()
    async def start_dm(self, ctx, user: discord.User):
        """Starts a DM conversation with another user via the bot."""
        
        # Ensure users are not already in active conversations
        if ctx.author.id in self.active_conversations or user.id in self.active_conversations:
            await ctx.send("Either you or the selected user is already in an active conversation. End it before starting a new one.")
            return
        
        # If the user hasn't used the DM feature before, show the rules
        if ctx.author.id not in self.used_dm_users:
            embed = discord.Embed(
                title="⚠️ **DM Conversation Rules** ⚠️",
                description=(
                    "1. **Respect privacy**—no harassment or stalking.\n"
                    "2. **No spamming** or excessive messaging.\n"
                    "3. **Keep it respectful**—no bullying or inappropriate behavior.\n"
                    "4. **No threats or abusive language**.\n"
                    "5. **No unsolicited advertising**.\n"
                    "6. **Ensure both users consent** to a conversation.\n"
                    "7. **Do not impersonate others**.\n"
                    "8. **Avoid sharing sensitive personal information**.\n"
                    "9. **Conversations will end** after 5 minutes of inactivity.\n"
                    "10. **Report any misuse** to server staff.\n\n"
                    "🚫 Violating these rules may result in suspension or banning from this feature."
                ),
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            self.used_dm_users[ctx.author.id] = True
            self.save_used_dm_users()

        # Initiate the conversation
        self.active_conversations[ctx.author.id] = user.id
        self.active_conversations[user.id] = ctx.author.id
        self.inactivity_times[ctx.author.id] = asyncio.get_event_loop().time()  # Record current time for timeout tracking

        await ctx.send(f"Conversation started with {user.name}.")
        await user.send(f"{ctx.author.display_name} has started a conversation with you. You can now reply here.\n-# User id: {ctx.author.id}. Click here to [report user](https://discord.com/channels/1264302631174668299/1264350097118859294/1276088742414647417)")

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
