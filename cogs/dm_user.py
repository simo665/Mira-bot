import discord
from discord.ext import commands
from discord.ext.commands import CommandOnCooldown

class dm_user(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_conversations = {}  # Dictionary to store user conversations
        self.close_cooldown = {}  # Dictionary to manage close command cooldowns

    @commands.command()
    async def dm(self, ctx, user: discord.User, *, message): 
            
        try:
            # Determine the server and member based on whether the command is in DMs or server
            if isinstance(ctx.channel, discord.DMChannel):
                guild = self.bot.get_guild(1264302631174668299)  # Replace with your server ID
                member = guild.get_member(ctx.author.id)
            else:
                guild = ctx.guild
                member = ctx.author
        
            await user.send(message)
            await ctx.send(f"Message sent successfully to {user.name}")
            
            # Track the conversation
            self.active_conversations[user.id] = ctx.author.id

        except discord.Forbidden:
            await ctx.send(f"Couldn't send a DM to {user.name}. They may have DMs disabled or blocked the bot.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to send the message due to an API error: {e}")

    @commands.command()
    async def close(self, ctx, user: discord.User):
        """Close the conversation with a user."""
        if user.id in self.active_conversations:
            del self.active_conversations[user.id]
            await ctx.send(f"Conversation with {user.name} has been closed.")
            await user.send(f"Conversation with {ctx.author} has been closed.")
        else:
            await ctx.send(f"No active conversation found with {user.name}.")

    @close.error
    async def close_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Try again in {int(error.retry_after)} seconds.")
        else:
            await ctx.send("An error occurred while trying to close the conversation.")
    async def inactivity_timeout(self, user_id):
        """Waits for 300 seconds (5 minutes) before closing the conversation due to inactivity."""
        await asyncio.sleep(300)  # Wait for 5 minutes
        await self.close_conversation(user_id)

    async def close_conversation(self, user_id):
        """Closes the conversation with the specified user."""
        if user_id in self.active_conversations:
            del self.active_conversations[user_id]
            del self.inactivity_cooldowns[user_id]  # Remove the cooldown task
            user = self.bot.get_user(user_id)
            if user:
                await user.send("Your conversation has been closed due to inactivity.")         
                
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
                        await recipient.send(f"{message.author.display_name}: {message.content}")
                        self.active_conversations[message.author.id] = recipient.id
                    except discord.HTTPException:
                        await message.channel.send("Failed to forward the message.")
                else:
                    await message.channel.send("Couldn't find the original user.")
            else:
                if self.bot.command_prefix not in message.content:
                    await message.channel.send("No active conversation to reply to.")

async def setup(bot):
    await bot.add_cog(dm_user(bot))
