import discord
import json
import os
from discord.ext import commands
from mistralai import Mistral
from config import api_key, knowledge, personality, memory_length, save_threshold
import importlib
import asyncio

class MistralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Mistral AI setup
        self.api_key = api_key
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=self.api_key)
        # Memory Directory
        self.memory_dir = "user/user_memories"
        os.makedirs(self.memory_dir, exist_ok=True)
        self.save_threshold = save_threshold  # Save memory after a specific number of messages
        self.message_counter = {}
        self.memory_length = memory_length
        self.personality = personality
        self.knowledge = knowledge

    def get_user_memory_path(self, user_id):
        """Get the file path for a user's memory."""
        return os.path.join(self.memory_dir, f"{user_id}.json")

    def load_user_memory(self, user_id):
        """Load memory for a specific user."""
        memory_path = self.get_user_memory_path(user_id)
        if os.path.exists(memory_path):
            with open(memory_path, "r") as f:
                return json.load(f)
        return {"summaries": []}

    def save_user_memory(self, user_id, memory):
        """Save memory for a specific user."""
        memory_path = self.get_user_memory_path(user_id)
        with open(memory_path, "w") as f:
            json.dump(memory, f, indent=2)
            print(f"Memory saved for user {user_id}")

    def increment_message_counter(self, user_id):
        """Increment the message counter for a user."""
        self.message_counter[user_id] = self.message_counter.get(user_id, 0) + 1
        return self.message_counter[user_id]

    def reset_message_counter(self, user_id):
        """Reset the message counter for a user."""
        self.message_counter[user_id] = 0

    async def generate_summary(self, user_id, conversation_history):
        """Generate a summary using the AI API."""
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.personality},
                    {"role": "assistant", "content": self.knowledge},
                    {"role": "user", "content": "Summarize this conversation in 5 lines or less:"},
                    {"role": "user", "content": "\n".join(conversation_history)}
                ],
            )
            summary = response.choices[0].message.content
            return summary.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Error: Unable to generate summary."

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return
        
        assistant = f"The user's name is {message.author.display_name}. You can use this name in your replies to personalize them. " 
        assistant += self.knowledge
        server_id = str(message.guild.id)
        user_id = str(message.author.id)
        
        
        # Load user's memory
        user_memory = self.load_user_memory(user_id)

        # Initialize conversation history if not present
        if "conversation" not in user_memory:
            user_memory["conversation"] = []
        

        # Add the new message to the conversation history
        user_memory["conversation"].append(f"{message.author.display_name}: {message.content}")
        
        # Limit conversation history length
        if len(user_memory["conversation"]) > self.memory_length:
            user_memory["conversation"].pop(0)

        # Increment message counter and check threshold
        message_count = self.increment_message_counter(user_id)
        
        if message_count >= self.save_threshold:
            # Generate a summary
            summary = await self.generate_summary(user_id, user_memory["conversation"])
            user_memory["summaries"].append(summary)
            user_memory["conversation"] = []  # Reset conversation history
            self.reset_message_counter(user_id)

        # Save the updated memory
        self.save_user_memory(user_id, user_memory)
        message_count = self.message_counter.get(user_id, 0)
        # If the bot is mentioned, respond
        if self.bot.user in message.mentions:
            print("The bot mentioned!")
            try:
                async with message.channel.typing():
                    # Include memory summaries in the AI input
                    past_summaries = "\n".join(user_memory["summaries"])
                    response = self.client.chat.complete(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.personality},
                            {"role": "assistant", "content": self.knowledge},
                            {"role": "assistant", "content": f"Past summaries:\n{past_summaries}"},
                            {"role": "user", "content": message.content}
                        ],
                    )
                # Get AI response
                ai_reply = response.choices[0].message.content
                await message.channel.send(ai_reply)
            except Exception as e:
                await message.channel.send("Oops, something went wrong!")
                print(f"Error: {e}")

    # Admin commands
    @commands.command(name="sleep")
    @commands.has_permissions(administrator=True)
    async def save_memory_command(self, ctx):
        """Save all user memories to file."""
        await ctx.send("Memory saved manually.")

    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_memory_command(self, ctx, user_id: str):
        """Reset a user's memory."""
        memory_path = self.get_user_memory_path(user_id)
        if os.path.exists(memory_path):
            os.remove(memory_path)
            await ctx.send(f"Memory for user {user_id} has been reset.")
        else:
            await ctx.send("No memory found for this user.")

# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(MistralCog(bot))
