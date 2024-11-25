import discord
import json
import os
from discord.ext import commands
from mistralai import Mistral
from config import api_key, knowledge, personality, memory_length

class MistralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Mistral AI setup
        self.api_key = api_key
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=self.api_key)
        # Memory file
        self.memory_file = "user/memory.json"
        self.memory = self.load_memory()
        # customization 
        self.user = None
        self.memory_length = memory_length
        self.personality = personality 
        self.knowledge = knowledge
        
    def load_memory(self):
        """Load memory from a JSON file."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return {}

    def save_memory(self):
        """Save memory to a JSON file."""
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    @commands.Cog.listener()
    async def on_message(self, message):
        # AI Assistance
        self.user = message.author.display_name
        assistant = f"The user's name is {self.user}. You can use this name in your replies to personalize them. " 
        assistant += self.knowledge
        # Ignore messages from bots
        if message.author.bot:
            return 

        # Check if the bot is mentioned
        if self.bot.user in message.mentions:
            # Use channel ID as the top-level key
            channel_id = str(message.channel.id)
            user_id = str(message.author.id)
            # Create channel memory if not present
            if channel_id not in self.memory:
                self.memory[channel_id] = {}
            # Create or fetch user memory within the channel
            if user_id not in self.memory[channel_id]:
                self.memory[channel_id][user_id] = []
            # Add the user's message to their memory
            self.memory[channel_id][user_id].append({"role": "user", "content": message.content})
            # Limit memory to the last `memory_length` messages
            if len(self.memory[channel_id][user_id]) > self.memory_length:
                self.memory[channel_id][user_id].pop(0)
            try:
                async with message.channel.typing():
                    # Send the memory (conversation history) to Mistral AI
                    response = self.client.chat.complete(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.personality},
                            {"role": "assistant", "content": assistant},
                            *self.memory[channel_id][user_id]  # Pass the conversation historic 
                        ]
                    )
                # Get AI response
                ai_reply = response.choices[0].message.content
                # Add the AI's response to the user's memory
                self.memory[channel_id][user_id].append({"role": "assistant", "content": ai_reply})
                # Save memory to file
                self.save_memory()
                # Send the AI's response to the channel
                await message.channel.send(ai_reply)
                
            except Exception as e:
                await message.channel.send("Oops, something went wrong while processing your request.")
                print(f"Error: {e}")
        
# Function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(MistralCog(bot))
