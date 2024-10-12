import discord
from discord.ext import commands
import asyncio

class MessagesEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Define the emojis
        loading_heart = "<a:loading_heart:1294048090189332537>"
        red_hearts = "<a:redhearts:1294048122011521064>"

        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return
        
        # Check for specific words in the message content
        if any(word in message.content.lower() for word in ("welcome", "wlc")):
            try:
                # Add the loading heart reaction
                await message.add_reaction(loading_heart)
                await asyncio.sleep(1.8)
                # Remove the loading heart reaction
                await message.remove_reaction(loading_heart, self.bot.user)
                await asyncio.sleep(0.1)
                # Add the red hearts reaction
                await message.add_reaction(red_hearts)
            except Exception as e:
                print(f"An error occurred: {e}")
        
# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(MessagesEvents(bot))
