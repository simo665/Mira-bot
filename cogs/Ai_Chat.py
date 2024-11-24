import discord
from discord.ext import commands
from mistralai import Mistral

class MistralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Mistral AI setup
        self.api_key = os.environ["MISTRAL_API_KEY"]
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=self.api_key)

    @commands.command()
    async def ask(self, ctx, *, question: str):
        """Ask Mistral AI a question and receive a response."""
        try:
            # Interact with Mistral AI
            response = self.client.chat.complete(
                model=self.model,
                messages=[
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
