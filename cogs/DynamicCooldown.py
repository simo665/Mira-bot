import discord
from discord.ext import commands, tasks
from collections import defaultdict
import asyncio
import time

class DynamicSlowMode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_count = defaultdict(int)  # Tracks messages per channel
        self.user_count = defaultdict(set)  # Tracks unique users per channel
        self.last_message_time = defaultdict(float)  # Tracks the last message timestamp for each channel
        self.ignored_channels = set()  # Tracks channels that should be ignored for cooldown adjustments
        self.slow_mode_task.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return

        # Increment message count for the channel
        self.message_count[message.channel.id] += 1
        # Add the user to the set of users for the channel (ensuring uniqueness)
        self.user_count[message.channel.id].add(message.author.id)
        # Update the timestamp of the last message sent in this channel
        self.last_message_time[message.channel.id] = time.time()

    @tasks.loop(seconds=1)
    async def slow_mode_task(self):
        """Adjust slow mode dynamically based on activity."""
        current_time = time.time()
        for channel_id, count in list(self.message_count.items()):
            # Fetch the channel
            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue

            # Ignore channels that already have a specific cooldown set
            if channel_id in self.ignored_channels:
                continue

            # Calculate idle time since the last message
            idle_time = current_time - self.last_message_time[channel_id]
            
            # Calculate number of unique users chatting in the channel
            active_users = len(self.user_count[channel_id])

            # Calculate the cooldown based on active users and message count
            if active_users > 0:
                # The cooldown formula is based on both active users and messages sent
                cooldown = max(1, min(10, (count / active_users) * 0.5))  # 1 second minimum, 10 second maximum

                try:
                    # Apply slow mode
                    await channel.edit(slowmode_delay=int(cooldown))
                 
                except discord.Forbidden:
                    print(f"Missing permissions to edit {channel.name}.")
                except Exception as e:
                    print(f"Error updating slow mode in {channel.name}: {e}")

            # Reset message count and user set after idle time has passed (e.g., 5 seconds of inactivity)
            if idle_time > 5:
                self.message_count[channel_id] = 0
                self.user_count[channel_id].clear()
                print(f"Reset message count in {channel.name} due to inactivity.")

    @slow_mode_task.before_loop
    async def before_slow_mode_task(self):
        """Ensure bot is ready before starting the loop."""
        await self.bot.wait_until_ready()

    @commands.command()
    async def ignore_channel(self, ctx, channel: discord.TextChannel):
        """Command to ignore a channel for slowmode adjustments."""
        self.ignored_channels.add(channel.id)
        await ctx.send(f"{channel.name} will now be ignored for dynamic slowmode adjustments.")

    @commands.command()
    async def unignore_channel(self, ctx, channel: discord.TextChannel):
        """Command to unignore a channel for slowmode adjustments."""
        self.ignored_channels.discard(channel.id)
        await ctx.send(f"{channel.name} will now be included in dynamic slowmode adjustments.")

async def setup(bot):
    await bot.add_cog(DynamicSlowMode(bot))