import discord
from discord.ext import commands, tasks
from collections import defaultdict
import asyncio

class DynamicSlowMode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_count = defaultdict(int)  # Tracks messages per channel
        self.slow_mode_task.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Increment message count for the channel
        self.message_count[message.channel.id] += 1

    @tasks.loop(seconds=1)
    async def slow_mode_task(self):
        """Adjust slow mode dynamically based on activity."""
        for channel_id, count in list(self.message_count.items()):
            # Fetch the channel
            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue

            # Calculate new slow mode delay
            cooldown = min(max(count * 0.5, 0), 10)  # Formula: 0.5 seconds per message, capped at 10 seconds

            try:
                # Apply slow mode
                await channel.edit(slowmode_delay=int(cooldown))
                print(f"Set slow mode in {channel.name} to {cooldown} seconds.")
            except discord.Forbidden:
                print(f"Missing permissions to edit {channel.name}.")
            except Exception as e:
                print(f"Error updating slow mode in {channel.name}: {e}")

            # Reset message count for the channel
            self.message_count[channel_id] = 0

    @commands.command(name="exempts")
    @commands.has_permissions(manage_channels=True)
    async def exempt_roles(self, ctx, role: discord.Role):
        """Add a role to the slow mode exemption list."""
        if role.id not in self.bot.slow_mode_exempt_roles:
            self.bot.slow_mode_exempt_roles.append(role.id)
            await ctx.send(f"Added {role.name} to slow mode exemptions.")
        else:
            await ctx.send(f"{role.name} is already exempt.")

    @slow_mode_task.before_loop
    async def before_slow_mode_task(self):
        """Ensure bot is ready before starting the loop."""
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(DynamicSlowMode(bot))