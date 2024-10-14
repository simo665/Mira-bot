import discord
from discord.ext import commands, tasks
import time

class TimeDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message = None
        self.update_duration = 60  # Time in seconds for how long the updates should run
        self.start_time = None

    def get_formatted_timestamp(self):
        current_timestamp = int(time.time())
        return f"<t:{current_timestamp}:T>"

    @commands.command(name="showtime")
    async def showtime(self, ctx):
        if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.message.delete()
        self.message = await ctx.send(self.get_formatted_timestamp())
        self.start_time = time.time()  # Record the start time
        self.update_time.start()

    @tasks.loop(seconds=1)
    async def update_time(self):
        if self.message:
            try:
                # Stop updating if the duration has passed
                if time.time() - self.start_time >= self.update_duration:
                    self.update_time.stop()
                    return

                await self.message.edit(content=self.get_formatted_timestamp())
            except discord.NotFound:
                self.update_time.stop()  # Stop if the message was deleted

    @update_time.before_loop
    async def before_update_time(self):
        await self.bot.wait_until_ready()

    @commands.command(name="stop")
    async def stop(self, ctx):
        """Stops the time update."""
        self.update_time.stop()
        await ctx.message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(TimeDisplay(bot))
