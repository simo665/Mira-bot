import discord
from discord.ext import commands
from collections import defaultdict
import time

class DynamicCooldown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Tracks messages per channel
        self.channel_activity = defaultdict(list)  
        # Cooldown per channel (starts at 0)
        self.channel_cooldowns = defaultdict(float)  

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return

        channel_id = message.channel.id
        current_time = time.time()

        # Record the message timestamp
        self.channel_activity[channel_id].append(current_time)

        # Remove old messages (older than 1 second)
        self.channel_activity[channel_id] = [
            t for t in self.channel_activity[channel_id] if current_time - t <= 1
        ]

        # Calculate messages per second (MPS)
        mps = len(self.channel_activity[channel_id])

        # Dynamically adjust cooldown (starts from 0 and increases)
        self.channel_cooldowns[channel_id] = mps * 0.5  # 0.5 seconds added per message/sec

    @commands.command()
    async def my_command(self, ctx):
        channel_id = ctx.channel.id
        cooldown_time = self.channel_cooldowns[channel_id]

        # Check if the command is on cooldown
        if hasattr(ctx, "last_used") and time.time() - ctx.last_used < cooldown_time:
            remaining_time = round(cooldown_time - (time.time() - ctx.last_used), 2)
            await ctx.send(f"Command is on cooldown! Try again in {remaining_time} seconds.")
            return

        # Mark the command as used
        ctx.last_used = time.time()
        await ctx.send(f"Command executed! Current cooldown is {cooldown_time:.2f} seconds.")

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(DynamicCooldown(bot))