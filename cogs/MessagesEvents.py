import discord
from discord.ext import commands
import asyncio

class MessagesEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

       # Appeals support Bot ping
        self.bot = bot
        self.target_bot_id = 1298903550994284566  
        self.keyword = "@staff" 

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


       

#______________________________________________

        # Check if the message is from the specific bot
        if message.author.id == self.target_bot_id:
            # Check if the message contains the keyword
            if self.keyword in message.content:
                # Send a response to the same channel
                await message.channel.send("<@&1282336485596467242>, please assist with this. Take a moment to catch up on the conversation to understand the situation fully.")

#_____________________________________________
    
    @commands.has_permissions(manage_messages=True)
    async def send(self, ctx, channel: discord.TextChannel, *, message: str=None):
        if not message:
            await ctx.send("Please include a message to use this command.")
            return
        await channel.send(message)
        await ctx.send(f"Message sent to {channel.mention}")


    


# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(MessagesEvents(bot))
