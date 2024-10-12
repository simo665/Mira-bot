import discord
from discord.ext import commands
from config import TOKEN, intents
import datetime

class dm_user(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_conversations = {} # Dictionary to store user conversations
        self.first_time_dm = {} # Dictionary to check if it's the first message from a user
    # Command to send DM
    @commands.command()
    async def dm(self, ctx, user: discord.User, *, message):
        try:
            # Send DM to the user
            dm_embed = discord.Embed(
                title="Moderation Message",
                color=0xFFB6C1 
            )
            dm_embed.add_field(name=f"{ctx.author.display_name}:", value=message)
            dm_embed.add_field(name=f"This message is not appropriate?", value=f"[Click to report](https://discord.com/channels/1264302631174668299/1276072321127550987) *{ctx.author.name}*")
            dm_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
            await user.send(embed=dm_embed)
            await ctx.send(f"Message sent successfully to {user.name}")
            if user.id not in self.first_time_dm:
                await user.send("You can reply to this message by just sending a message here.")
                self.first_time_dm[user.id] = True
            # Track the conversation
            self.active_conversations[user.id] = ctx.author.id

        except discord.Forbidden:
            await ctx.send(f"Couldn't send a DM to {user.name}. They may have DMs disabled or blocked the bot.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to send the message due to an API error: {e}")

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
                        # Forward the reply to the original sender:
                        dm_back = discord.Embed(
                            title="Moderation Message",
                            color=FF6AFF78 
                            )
                        dm_back.add_field(name=f"{message.author.display_name}:", value=message.content)
                        dm_back.add_field(name=f"Do this cmd to reply:", value=f"$dm {message.author} (your message here)")
                        dm_back.set_author(name=message.author, icon_url=message.author.avatar.url)
                        await recipient.send(embed=dm_back)
                        #await asyncio.sleep(1)
                        await message.channel.send(f"Your reply has been forwarded.")
                        self.active_conversations[user.id] = message.author.id
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
