import discord
from discord.ext import commands, tasks
import time

class TimeDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_time_task = None  # Initialize the task variable

    # Function to get the current timestamp in Discord's format
    def get_formatted_timestamp(self):
        current_timestamp = int(time.time())
        return f"<t:{current_timestamp}:T>"

    # Command to display the time
    @commands.command(name="showtime")
    async def showtime(self, ctx):
        # Send the initial message with the current time
        message = await ctx.send(self.get_formatted_timestamp())

        # Start the task to update the message every second
        if self.update_time_task is None or not self.update_time_task.is_running():
            self.update_time_task = self.update_time(message)
            self.update_time_task.start()

    # Task to update the time every second
    @tasks.loop(seconds=1)
    async def update_time(self, message):
        try:
            await message.edit(content=self.get_formatted_timestamp())
        except discord.NotFound:
            # Stop the loop if the message was deleted or the channel is unavailable
            self.update_time_task.stop()

    # Stop the task if the cog is unloaded
    @update_time.before_loop
    async def before_update_time(self):
        await self.bot.wait_until_ready()

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(TimeDisplay(bot))
