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
        self.loading_heart = "<a:loading_heart:1294048090189332537>"
        self.red_hearts = "<a:redhearts:1294048122011521064>"
        self.white_hearts = "<a:whitehearts:1294048164705468517>"
        self.colorful_heart = "<a:heart:1294048146682417224>"
        self.cat_jump = "<a:cat_jumping:1294048140277841920>"
        self.GlitterHeart = "<a:GlitterHeart:1307331284707577908>"
        self.milkbear = "<a:milkbear:1307331320833249332>"
        self.black_heart = "<a:black_heart:1307331343054671943>"
        self.stitch_love = "<a:stitch_love_GT:1307331408192344135>"
        self.pokemon_love = "<a:pokemon_love:1307331488253218868>"
        self.Bongo_Cat = "<a:Bongo_Cat:1307331540631556096>"
        self.Love_Fox = "<a:Love_Fox:1307331624358252584>"
        self.emojis = [
            self.red_hearts, self.white_hearts, self.colorful_heart, self.cat_jump,
            self.GlitterHeart, self.milkbear, self.black_heart, self.stitch_love,
            self.pokemon_love, self.Bongo_Cat, self.Love_Fox
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if any(word in message.content.lower() for word in ("welcome", "wlc")):
            try:
                emoji = random.choice(self.emojis)
                await message.add_reaction(self.loading_heart)
                await asyncio.sleep(1.8)
                await message.remove_reaction(self.loading_heart, self.bot.user)
                await asyncio.sleep(0.1)
                await message.add_reaction(emoji)
                await asyncio.sleep(0.5)
                if emoji == self.milkbear:
                    await message.channel.send(self.milkbear)
                if emoji == self.cat_jump:
                    await message.channel.send(self.cat_jump)
            except Exception as e:
                print(f"An error occurred: {e}")

        if message.author.id == self.target_bot_id and self.keyword in message.content:
            await message.channel.send(
                "<@&1282336485596467242>, please assist with this. Take a moment to catch up on the conversation to understand the situation fully."
            )

    @commands.command()
    async def send(self, ctx, *, message: str):
        """Send a message on the channel"""
        await ctx.send(message)
        await ctx.message.delete()  # Delete the command message after sending

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
