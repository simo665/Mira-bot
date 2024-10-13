import discord
from discord.ext import commands, tasks
import time

class TimeDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message = None  # Store the message to update

    # Function to get the current timestamp in Discord's format
    def get_formatted_timestamp(self):
        current_timestamp = int(time.time())
        return f"<t:{current_timestamp}:T>"

    # Command to display the time
    @commands.command(name="showtime")
    async def showtime(self, ctx):
        # Send the initial message with the current time
        self.message = await ctx.send(self.get_formatted_timestamp())
        self.update_time.start()  # Start the loop

    # Task to update the time every second
    @tasks.loop(seconds=1)
    async def update_time(self):
        if self.message:
            try:
                await self.message.edit(content=self.get_formatted_timestamp())
            except discord.NotFound:
                self.update_time.stop()  # Stop if the message was deleted

    # Stop the task if the cog is unloaded
    @update_time.before_loop
    async def before_update_time(self):
        await self.bot.wait_until_ready()

    # Stop the update loop when the command is finished
    @commands.command(name="stop")
    async def stop(self, ctx):
        """Stops the time update."""
        self.update_time.stop()
        await ctx.send("Time updates stopped.")

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(TimeDisplay(bot))
