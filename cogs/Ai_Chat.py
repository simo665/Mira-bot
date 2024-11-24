import discord
import json
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

        # Memory file
        self.memory_file = "user/memory.json"
        self.memory = self.load_memory()
        
        self.memory_length = 10
        self.personality = "You're a cute little girl, you're totally a human, act and answer like a human, keep your answers shorts"
        

    def load_memory(self):
        """Load memory from a JSON file."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return {}

    def save_memory(self):
        """Save memory to a JSON file."""
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return 

        # Check if the bot is mentioned
        if self.bot.user in message.mentions:
            # Use the channel ID as the memory key
            memory_key = str(message.channel.id)  # Convert to string for JSON compatibility

            # Create or fetch memory for the channel
            if memory_key not in self.memory:
                self.memory[memory_key] = []

            # Add the user's message to the memory
            self.memory[memory_key].append({"role": "user", "content": message.content})

            # Limit memory to the last 5 messages
            if len(self.memory[memory_key]) > self.memory_length:
                self.memory[memory_key].pop(0)

            try:
                async with message.channel.typing():
                    # Send the memory (conversation history) to Mistral AI
                    response = self.client.chat.complete(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.personality},
                            *self.memory[memory_key],  # Pass the conversation history
                        ]
                    )

                # Get AI response
                ai_reply = response.choices[0].message.content

                # Add the AI's response to the memory
                self.memory[memory_key].append({"role": "assistant", "content": ai_reply})

                # Save memory to file
                self.save_memory()

                # Send the AI's response to the channel
                await message.channel.send(f"**Mistral AI says:** {ai_reply}")

            except Exception as e:
                await message.channel.send("Oops, something went wrong while processing your request.")
                print(f"Error: {e}")
        
        # Ensure other bot commands are processed
        await self.bot.process_commands(message)

# Function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(MistralCog(bot))
