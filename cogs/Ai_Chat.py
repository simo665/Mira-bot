import discord
import os
from discord.ext import commands
from mistralai import Mistral
from config import api_key


class MistralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Mistral AI setup
        self.api_key = api_key
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=self.api_key)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return 
        if message.bot.user in message.mentions:
            try:
                async with message.channel.typing():
                    response = self.client.chat.complete(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You're a funny playful girl! Your name Mira and you love strawberry."},
                            {"role": "user", "content": message.content}
                        ]
                    )

                # Get AI response
                    ai_reply = response.choices[0].message.content

            # Send response to the Discord channel
                await message.channel.send(f"**Mistral AI says:** {ai_reply}")
            except Exception as e:
                # Handle any errors and notify the user
                await message.channel.send("Oops, something went wrong while processing your request.")
            
    @commands.command()
    async def ask(self, ctx, *, question: str):
        """Ask Mistral AI a question and receive a response."""
        try:
            async with ctx.typing():
                response = self.client.chat.complete(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You're a funny playful girl! Your name Mira and you love strawberry."},
                        {"role": "user", "content": question}
                    ]
                )

            # Get AI response
                ai_reply = response.choices[0].message.content

            # Send response to the Discord channel
            await ctx.send(f"**Mistral AI says:** {ai_reply}")

        except Exception as e:
            # Handle errors gracefully
            await ctx.send("An error occurred while communicating with Mistral AI.")
            print(f"Error: {e}")

# Function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(MistralCog(bot))
