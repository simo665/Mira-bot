import discord
from discord.ext import commands
from utils.roles import get_highest_relevant_role  # Import the function
import asyncio  # For using sleep

class dm_user(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_conversations = {}  # Dictionary to store user conversations
        self.first_time_dm = {}  # Dictionary to check if it's the first message from a user
        self.inactivity_cooldowns = {}  # Track inactivity timers

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

            # Get the highest moderation role for the author
            highest_role = get_highest_relevant_role(member)

            # Format the name with the highest role
            if highest_role:
                author_name = f"{ctx.author.display_name} ({highest_role.name})"
            else:
                await ctx.send("This command is only for moderators.")
                return 

            dm_embed = discord.Embed(color=0xFFB6C1)
            dm_embed.add_field(name=f"{author_name}", value=f"**{message}**")
            dm_embed.add_field(name="This message is not appropriate?", value=f"[Click to report](https://discord.com/channels/1264302631174668299/1276072321127550987) *{ctx.author.name}*")
            dm_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
            await user.send(embed=dm_embed)
            await ctx.send(f"Message sent successfully to {user.name}")

            if user.id not in self.first_time_dm:
                await user.send("You can reply to this message by just sending a message here.")
                self.first_time_dm[user.id] = True
            
            # Track the conversation
            self.active_conversations[user.id] = ctx.author.id
            
            # Reset inactivity timer
            await self.reset_inactivity_timer(user.id)

        except discord.Forbidden:
            await ctx.send(f"Couldn't send a DM to {user.name}. They may have DMs disabled or blocked the bot.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to send the message due to an API error: {e}")

    async def reset_inactivity_timer(self, user_id):
        """Resets the inactivity timer for a user."""
        if user_id in self.inactivity_cooldowns:
            self.inactivity_cooldowns[user_id].cancel()  # Cancel any existing timer

        # Start a new inactivity timer
        self.inactivity_cooldowns[user_id] = self.bot.loop.create_task(self.inactivity_timeout(user_id))

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
            print(f"Conversation with {user_id} closed due to inactivity.")

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
                        dm_back = discord.Embed(color=0x90EE90)
                        dm_back.add_field(name=f"{message.author.display_name}", value=f"**{message.content}**")
                        dm_back.add_field(name="Do this cmd to reply:", value=f"$dm {message.author} (your message here)")
                        dm_back.set_author(name=message.author, icon_url=message.author.avatar.url)
                        await recipient.send(embed=dm_back)
                        await message.channel.send("Your reply has been forwarded.")
                        self.active_conversations[message.author.id] = recipient.id
                        await self.reset_inactivity_timer(recipient.id)  # Reset timer for the recipient
                    except discord.HTTPException:
                        await message.channel.send("Failed to forward the message.")
                else:
                    await message.channel.send("Couldn't find the original user.")
            else:
                if "$dm" not in message.content:
                    await message.channel.send("No active conversation to reply to.")

async def setup(bot):
    await bot.add_cog(dm_user(bot))
