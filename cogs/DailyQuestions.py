import discord
from discord.ext import commands, tasks
import os

class DailyQuestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = self.load_questions()  # Load questions from file
        self.channel_id = None  # Channel ID will be set using a command
        self.current_question_index = 0
        self.question_poster.start()

    def load_questions(self):
        """Loads questions from the file."""
        if not os.path.exists("questions.txt"):
            # Create the file if it doesn't exist
            with open("questions.txt", "w") as f:
                pass
        with open("questions.txt", "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]

    def save_question(self, question):
        """Appends a new question to the file."""
        with open("questions.txt", "a") as f:
            f.write(f"{question}\n")
        self.questions.append(question)

    # Task to post a question every 5 hours
    @tasks.loop(minutes=1)
    async def question_poster(self):
        if self.channel_id is None or not self.questions:
            return  # Do nothing if the channel is not set or there are no questions

        channel = self.bot.get_channel(self.channel_id)
        if channel is not None:
            question = self.questions[self.current_question_index]
            await channel.send(f"**New Question!!** {question}")
            # Update the index to the next question
            self.current_question_index = (self.current_question_index + 1) % len(self.questions)

    @question_poster.before_loop
    async def before_question_poster(self):
        await self.bot.wait_until_ready()

    @commands.command(name="setchannel")
    @commands.has_permissions(manage_channels=True)
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Command to set the channel for posting the hourly questions."""
        self.channel_id = channel.id
        await ctx.send(f"Channel set to {channel.mention} for posting questions.")

    @commands.command(name="showchannel")
    async def show_channel(self, ctx):
        """Shows the current channel where questions are being posted."""
        if self.channel_id:
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                await ctx.send(f"The current channel for questions is {channel.mention}.")
            else:
                await ctx.send("The channel set for questions no longer exists.")
        else:
            await ctx.send("No channel is currently set for questions.")

    @commands.command(name="addquestion")
    @commands.has_permissions(manage_messages=True)
    async def add_question(self, ctx, *, question: str):
        """Adds a new question to the list and saves it to the file."""
        if question:
            self.save_question(question)
            await ctx.send(f"New question added: '{question}'")
        else:
            await ctx.send("Please provide a valid question.")

async def setup(bot):
    await bot.add_cog(DailyQuestions(bot))
