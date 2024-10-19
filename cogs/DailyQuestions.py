import discord
from discord.ext import commands, tasks

class DailyQuestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = [
            "What's your favorite hobby and why?",
            "If you could learn one new skill instantly, what would it be?",
            "What's the best gift you've ever received?",
            "If you could have dinner with any celebrity, who would it be?",
            "What's your most treasured possession?",
            "What is your favorite movie and why?",
            "If you could visit any country, which would it be and why?",
            "What's your favorite childhood memory?",
            "If you could have any superpower, what would it be?",
            "What's the most unusual food you've ever tried?",
            "What is your dream job?",
            "If you won the lottery, what would you do with the money?",
            "What's your favorite way to relax?",
            "If you could change one thing about the world, what would it be?",
            "What is the best book you've ever read?",
            "Who is someone you admire and why?",
            "If you could time travel, where would you go?",
            "What's your favorite season and why?",
            "If you could live anywhere, where would it be?",
            "What's your favorite video game?",
            "What's a talent you have that not many people know about?",
            "What's the most adventurous thing you've ever done?",
            "If you could have any animal as a pet, what would it be?",
            "What's your favorite type of music?",
            "If you could speak any language fluently, which would it be?",
            "What's your favorite holiday and why?",
            "What is one goal you want to achieve this year?",
            "If you could meet any historical figure, who would it be?",
            "What's the most beautiful place you've ever visited?",
            "What's your favorite dessert?",
            "If you could live in a fictional world, which one would you choose?",
            "What is something you wish you knew more about?",
            "What's your favorite sport to play or watch?",
            "If you could have any job for a day, what would it be?",
            "What’s one thing you can't live without?",
            "If you could create a new holiday, what would it celebrate?",
            "What's your favorite animated movie?",
            "What was the last book you read?",
            "If you could go back and relive one day of your life, which day would it be?",
            "What's your favorite way to stay active?",
            "What’s one thing you are grateful for today?",
            "If you could master any instrument, what would it be?",
            "What's your favorite TV show right now?",
            "What's the most interesting documentary you've ever watched?",
            "If you could spend a day with any animal, which one would it be?",
            "What's your go-to comfort food?",
            "If you could have a conversation with your future self, what would you ask?",
            "What’s your favorite thing about your culture?",
            "What's one skill you think everyone should learn?",
            "What's your favorite way to spend time with friends?",
            "What's your dream vacation destination?",
            "What’s one thing you’d like to try but haven’t yet?",
            "If you could instantly become an expert in something, what would it be?",
            "What's your favorite outdoor activity?",
            "What's a book that you think everyone should read?",
            "If you could host a talk show, who would be your first guest?",
            "What's your favorite kind of weather?",
            "What’s one habit you’d like to develop?",
            "If you could swap lives with anyone for a day, who would it be?",
            "What's your favorite quote and why?",
            "If you could have any vehicle, what would it be?",
            "What's your favorite way to spend a rainy day?"
        ]
        self.channel_id = None  # Channel ID will be set using a command
        self.current_question_index = 0
        self.question_poster.start()

    # Task to post a question every 5 hours
    @tasks.loop(hours=5)
    async def question_poster(self):
        if self.channel_id is None:
            return  # Do nothing if the channel is not set

        channel = self.bot.get_channel(self.channel_id)
        if channel is not None and self.questions:
            question = self.questions[self.current_question_index]
            await channel.send(f"**New Question!!:** {question}")
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

async def setup(bot):
    await bot.add_cog(DailyQuestions(bot))