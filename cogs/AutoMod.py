import discord
from discord.ext import commands
import requests
from collections import defaultdict
import os
from config import API, intents

class PerspectiveModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = API
        self.kick_threshold = int(os.getenv("KICK_THRESHOLD", 5))
        self.user_scores = defaultdict(lambda: defaultdict(int))
        self.emoji_map = {
            "TOXICITY": "🧨",
            "INSULT": "👊",
            "IDENTITY_ATTACK": "👤",
            "THREAT": "⚠️",
        }

    def analyze_text(self, text):
        url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
        payload = {
            "comment": {"text": text},
            "languages": ["en"],
            "requestedAttributes": {key: {} for key in self.emoji_map.keys()},
        }
        params = {"key": self.api_key}
        response = requests.post(url, params=params, json=payload)
        return response.json().get("attributeScores", {})

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        user_id = message.author.id
        scores = self.analyze_text(message.content)

        # Evaluate scores and take actions
        should_kick = False
        for attribute, score_data in scores.items():
            score = score_data["summaryScore"]["value"]
            if score > 0.8:  # Threshold for deletion
                self.user_scores[user_id][attribute] += 1
                await message.delete()
                await message.channel.send(
                    f"Message deleted for {attribute.lower()}."
                )
                if self.user_scores[user_id]["TOXICITY"] >= self.kick_threshold:
                    should_kick = True

        # Kick user if threshold is exceeded
        if should_kick:
            member = message.guild.get_member(user_id)
            if member:
                try:
                    await member.kick(reason="Exceeded toxicity threshold")
                    await message.channel.send(
                        f"Kicked {member.mention} for repeated violations."
                    )
                except discord.Forbidden:
                    await message.channel.send(
                        "I don't have permission to kick this user."
                    )

# Setup function to add the cog
async def setup(bot):
    await bot.add_cog(PerspectiveModeration(bot))
