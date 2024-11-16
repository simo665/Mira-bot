import discord
from discord.ext import commands
import asyncio
import random 

class MessagesEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_bot_id = 1298903550994284566  
        self.keyword = "@staff"
        
        # Emojis 
        loading_heart = "<a:loading_heart:1294048090189332537>"
        red_hearts = "<a:redhearts:1294048122011521064>"
        white_hearts = "<a:whitehearts:1294048164705468517>"
        colorful_heart = "<a:heart:1294048146682417224>"
        cat_jump = "<a:cat_jumping:1294048140277841920>"
        GlitterHeart = "<a:GlitterHeart:1307331284707577908>"
        milkbear = "<a:milkbear:1307331320833249332>"
        black_heart = "<a:black_heart:1307331343054671943>"
        stitch_love = "<a:stitch_love_GT:1307331408192344135>"
        pokemon_love = "<a:pokemon_love:1307331488253218868>"
        Bongo_Cat= "<a:Bongo_Cat:1307331540631556096>"
        Love_Fox = "<a:Love_Fox:1307331624358252584>"
        emojis = [red_hearts, white_hearts, colorful_heart, cat_jump, GlitterHeart, milkbear, black_heart, stitch_love, pokemon_love, Bongo_Cat, Love_Fox]

    @commands.Cog.listener()
    async def on_message(self, message):
  
        
        if message.author == self.bot.user:
            return
        
        if any(word in message.content.lower() for word in ("welcome", "wlc")):
            try:
                emoji = random.choice(emojis)
                await message.add_reaction(loading_heart)
                await asyncio.sleep(1.8)
                await message.remove_reaction(loading_heart, self.bot.user)
                await asyncio.sleep(0.1)
                await message.add_reaction(emoji)
                await asyncio.sleeo(0.5)
                if emoji == milkbear:
                    await message.channel.send(milkbear)
                if emoji == cat_jump:
                    await message.channel.send(cat_jump)
            except Exception as e:
                print(f"An error occurred: {e}")

        if message.author.id == self.target_bot_id and self.keyword in message.content:
            await message.channel.send("<@&1282336485596467242>, please assist with this. Take a moment to catch up on the conversation to understand the situation fully.")

    @commands.command()
    async def send(self, ctx, *, message: str):
        """Send a message on the channel"""
        await ctx.send(message)
        # Delete the command message after sending
        await ctx.message.delete()
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def sendc(self, ctx, channel: discord.TextChannel, *, message):
        """Send a message in a specific channel"""
        if channel:
            await channel.send(message)
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❌")



# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(MessagesEvents(bot))
    
