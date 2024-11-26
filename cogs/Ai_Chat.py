import discord
import json
import os
from discord.ext import commands
from mistralai import Mistral
from config import api_key, knowledge, personality, memory_length, save_threshold
import asyncio

class MistralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = api_key
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=self.api_key)
        self.memory_dir = "user/user_memories"  # Directory for individual user memories
        self.temp_memory = {}  # Temporary memory for channel context
        self.memory_length = memory_length
        self.personality = personality
        self.knowledge = knowledge
        self.save_threshold = save_threshold
        self.message_counter = {}

        # Ensure the memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)

    def load_user_memory(self, user_id):
        """Load memory for a specific user from a JSON file."""
        memory_file = os.path.join(self.memory_dir, f"{user_id}.json")
        if os.path.exists(memory_file):
            with open(memory_file, "r") as f:
                return json.load(f)
        return []

    def save_user_memory(self, user_id, memory):
        """Save memory for a specific user to a JSON file."""
        memory_file = os.path.join(self.memory_dir, f"{user_id}.json")
        with open(memory_file, "w") as f:
            json.dump(memory, f, indent=2)
            print(f"Memory for user {user_id} saved successfully.")

    def add_to_temp_memory(self, channel_id, message):
        """Add a message to temporary memory for context."""
        if channel_id not in self.temp_memory:
            self.temp_memory[channel_id] = []
        self.temp_memory[channel_id].append(message)
        if len(self.temp_memory[channel_id]) > self.memory_length:
            self.temp_memory[channel_id].pop(0)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return

        channel_id = str(message.channel.id)
        user_id = str(message.author.id)

        # Add message to temporary memory for context
        self.add_to_temp_memory(channel_id, {"role": "user", "content": message.content})

        # Process only if the bot is mentioned
        if self.bot.user in message.mentions:
            user_memory = self.load_user_memory(user_id)

            # Include temporary memory for context
            context_memory = self.temp_memory.get(channel_id, [])
            complete_memory = context_memory + user_memory

            assistant_message = f"The user's name is {message.author.display_name}. You can use this name in your replies to personalize them. "
            assistant_message += self.knowledge

            try:
                async with message.channel.typing():
                    response = self.client.chat.complete(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.personality},
                            {"role": "assistant", "content": assistant_message},
                            *complete_memory
                        ]
                    )
                # Get AI response
                ai_reply = response.choices[0].message.content

                # Save only the interaction with the bot to user memory
                user_memory.append({"role": "user", "content": message.content})
                user_memory.append({"role": "assistant", "content": ai_reply})
                if len(user_memory) > self.memory_length:
                    user_memory.pop(0)

                self.save_user_memory(user_id, user_memory)

                # Send the AI's response
                await message.channel.send(ai_reply)
            except ConnectionError:
                await message.channel.send("There seems to be a network issue. Please try again later.")
            except KeyError as e:
                await message.channel.send("Oops, something went wrong with the data format. Please report this issue.")
            except json.JSONDecodeError:
                await message.channel.send("Received an invalid response from the AI. Please try again later.")
            except Exception as e:
                await message.channel.send("Oops, something went wrong while processing your request.")
                print(f"Error: {e}")

    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_user_memory(self, ctx, user_id=None):
        """Reset memory for a specific user."""
        if user_id:
            memory_file = os.path.join(self.memory_dir, f"{user_id}.json")
            if os.path.exists(memory_file):
                os.remove(memory_file)
                await ctx.send(f"Memory for user {user_id} has been reset.")
            else:
                await ctx.send("No memory found for that user.")
        else:
            await ctx.send("Please specify a user ID to reset their memory.")

    @commands.command(name="save")
    @commands.has_permissions(administrator=True)
    async def save_all_memories(self, ctx):
        """Save temporary memory to individual user files."""
        for user_id, memory in self.temp_memory.items():
            self.save_user_memory(user_id, memory)
        await ctx.send("All memories have been saved.")

# Function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(MistralCog(bot))
