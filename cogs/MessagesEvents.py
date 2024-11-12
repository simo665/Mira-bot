import discord
from discord.ext import commands
import asyncio

class MessagesEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_bot_id = 1298903550994284566  
        self.keyword = "@staff"

    @commands.Cog.listener()
    async def on_message(self, message):
        loading_heart = "<a:loading_heart:1294048090189332537>"
        red_hearts = "<a:redhearts:1294048122011521064>"

        if message.author == self.bot.user:
            return
        
        if any(word in message.content.lower() for word in ("welcome", "wlc")):
            try:
                await message.add_reaction(loading_heart)
                await asyncio.sleep(1.8)
                await message.remove_reaction(loading_heart, self.bot.user)
                await asyncio.sleep(0.1)
                await message.add_reaction(red_hearts)
            except Exception as e:
                print(f"An error occurred: {e}")

        if message.author.id == self.target_bot_id and self.keyword in message.content:
            await message.channel.send("<@&1282336485596467242>, please assist with this. Take a moment to catch up on the conversation to understand the situation fully.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def send(self, ctx, Channel: discord.TextChannel = None, *, message: str):
        """Send a message to a specific channel or the current channel if none is specified."""
        target_channel = Channel or ctx.channel
        await target_channel.send(message)
        # Delete the command message after sending
        await ctx.message.delete()

# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(MessagesEvents(bot))
