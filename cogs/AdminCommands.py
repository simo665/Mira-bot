import discord
from discord.ext import commands

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Your user ID as the bot owner
        self.owner_id = 1276601420652482643

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages sent by the bot itself
        if message.author == self.bot.user:
            return
        
        # Check if the bot is mentioned
        if self.bot.user in message.mentions:
            # Split the message to get the command
            content = message.content.split()
            if len(content) > 1 and content[1].lower() == 'leave':
                # Check if the user ID matches the owner ID
                if message.author.id == self.owner_id:
                    await message.channel.send("Alright, Jenna. Thanks for the good times here. Goodbye!")
                    await message.guild.leave()
                else:
                    await message.channel.send("You do not have permission to make me leave the server.")

# Setup function to add the cog to the bot
async setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
