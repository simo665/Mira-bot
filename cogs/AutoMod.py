import discord
from discord.ext import commands
import requests
from config import API, intents

class AutoModCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = API

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        text = message.content
        url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
        payload = {
            "comment": {"text": text},
            "languages": ["en"],
            "requestedAttributes": {
                "TOXICITY": {}, "INSULT": {}, "IDENTITY_ATTACK": {}, "THREAT": {}
            }
        }
        params = {"key": self.api_key}
        response = requests.post(url, params=params, json=payload)
        result = response.json()

        # Check for high scores in the results
        for attribute, score in result.get("attributeScores", {}).items():
            if score["summaryScore"]["value"] > 0.8:  # Threshold can be adjusted
                await message.delete()
                await message.channel.send(f"Message deleted due to {attribute.lower()}.")

# Adding the Cog to the bot
async def setup(bot):
    await bot.add_cog(AutoModCog(bot))