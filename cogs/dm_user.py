import discord
from discord.ext import commands, tasks
import asyncio
import json
import os

class DMConversation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_conversations = {}
        self.inactivity_times = {}
        self.used_dm_users = self.load_used_dm_users()
        self.blocked_users = self.load_blocked_users()

    def load_used_dm_users(self):
        """Loads users who have already used the DM feature."""
        if os.path.exists('user/dms_config.json'):
            with open('user/dms_config.json', 'r') as f:
                data = json.load(f)
                return data.get("used_dm_users", {})
        return {}

    def load_blocked_users(self):
        """Loads blocked users from the JSON file."""
        if os.path.exists('user/dms_config.json'):
            with open('user/dms_config.json', 'r') as f:
                data = json.load(f)
                return data.get("blocked_users", {})
        return {}

    def save_blocked_users(self):
        """Saves the blocked users to the JSON file."""
        data = {"used_dm_users": self.used_dm_users, "blocked_users": self.blocked_users}
        with open('user/dms_config.json', 'w') as f:
            json.dump(data, f)

    @commands.command()
    async def start_dm(self, ctx, user: discord.User):
        """Starts a DM conversation with another user via the bot."""
        
        # Check if the other user has blocked the initiator
        if ctx.author.id in self.blocked_users.get(str(user.id), []):
            await ctx.send(f"You are blocked by {user.display_name} and cannot start a DM with them.")
            return
        elif user.id in self.blocked_users.get(str(ctx.author.id), []):
            await ctx.send(f"You have blocked {user.display_name}. Unblock them to start a conversation.")
            return
        
        # Ensure users are not already in active conversations
        if ctx.author.id in self.active_conversations or user.id in self.active_conversations:
            await ctx.send("Either you or the selected user is already in an active conversation. End it before starting a new one.")
            return
        
        # Send DM rules if this is the user's first time using the feature
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
            self.save_blocked_users()

        # Start the conversation
        self.active_conversations[ctx.author.id] = user.id
        self.active_conversations[user.id] = ctx.author.id
        self.inactivity_times[ctx.author.id] = asyncio.get_event_loop().time()

        await ctx.send(f"Conversation started with {user.name}.")
        await user.send(f"""
{ctx.author.display_name} has started a conversation with you.
Actions available:
> * 0. Listen to what they will say.
> * 1. Block: `m!block`
> * 2. Report if they misbehave: `m!report @username` (block them first with `!block @username`)
> * 3. Close this conversation: `m!close_dm` (they can reopen it later)
""")

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
    async def block(self, ctx, user: discord.User = None):
        """Blocks a user, preventing them from starting a DM with the command user."""
        if user is None and ctx.author.id in self.active_conversations:
            user = self.bot.get_user(self.active_conversations[ctx.author.id])
        if user is None:
            await ctx.send("Specify a user to block.")
            return
        if user.id == ctx.author.id:
            await ctx.send("You cannot block yourself.")
            return

        self.blocked_users.setdefault(str(ctx.author.id), []).append(user.id)
        self.save_blocked_users()
        await ctx.send(f"{user.name} has been blocked. `m!unblock @username` to unblock.")

        # Close the conversation if blocking an active conversation partner
        if user.id in self.active_conversations and self.active_conversations[user.id] == ctx.author.id:
            await self.close_dm(ctx)

    @commands.command()
    async def unblock(self, ctx, user: discord.User = None):
        """Unblocks a user, allowing them to start a DM with the command user."""
        if user is None and ctx.author.id in self.active_conversations:
            user = self.bot.get_user(self.active_conversations[ctx.author.id])
        if user is None:
            await ctx.send("Specify a user to unblock.")
            return

        if str(ctx.author.id) in self.blocked_users and user.id in self.blocked_users[str(ctx.author.id)]:
            self.blocked_users[str(ctx.author.id)].remove(user.id)
            self.save_blocked_users()
            await ctx.send(f"{user.display_name} has been unblocked.")
        else:
            await ctx.send(f"{user.display_name} was not blocked.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handles DM forwarding during active conversations."""
        if isinstance(message.channel, discord.DMChannel) and message.author.id in self.active_conversations:
            recipient_id = self.active_conversations[message.author.id]
            recipient = self.bot.get_user(recipient_id)
            if recipient:
                try:
                    await recipient.send(f"**{message.author.display_name}:** {message.content}")
                    self.inactivity_times[message.author.id] = asyncio.get_event_loop().time()
                except discord.HTTPException:
                    await message.channel.send("Failed to forward the message.")
            else:
                await message.channel.send("The user is unavailable.")

    @tasks.loop(seconds=60)
    async def check_inactivity(self):
        """Checks for inactive conversations and closes them if inactive for over 5 minutes."""
        now = asyncio.get_event_loop().time()
        timeout_duration = 3600
        to_close = []

        for user_id, last_active in self.inactivity_times.items():
            if now - last_active > timeout_duration:
                to_close.append(user_id)

        for user_id in to_close:
            recipient_id = self.active_conversations.get(user_id)
            if recipient_id:
                user = self.bot.get_user(user_id)
                recipient = self.bot.get_user(recipient_id)
                if user:
                    await user.send("Your conversation has been closed due to inactivity.")
                if recipient:
                    await recipient.send("Your conversation has been closed due to inactivity.")
                
                del self.active_conversations[user_id]
                del self.active_conversations[recipient_id]
                del self.inactivity_times[user_id]

    @commands.Cog.listener()
    async def on_ready(self):
        """Starts the inactivity check loop when the bot is ready."""
        self.check_inactivity.start()

async def setup(bot):
    await bot.add_cog(DMConversation(bot))
