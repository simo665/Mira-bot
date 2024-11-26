import discord
import json
import os
from discord.ext import commands
from mistralai import Mistral
from config import api_key, knowledge, personality, memory_length

class MistralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = api_key
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=self.api_key)
        self.memory_dir = "/app/user/user_memories"  # Directory for individual user memories
        self.temp_memory = {}  # Temporary memory for recent messages
        self.message_counter = {}  # Message count per user
        self.summary_threshold = 15  # Number of messages before generating a summary
        self.knowledge = knowledge

        # Ensure the memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)
        print(f"Memory directory absolute path: {os.path.abspath(self.memory_dir)}")

    def load_user_memory(self, user_id):
        """Load memory for a specific user from a JSON file."""
        print("I'm inside loading function")
        memory_file = os.path.join(self.memory_dir, f"{user_id}.json")
        print(f"Does the path exist? {os.path.exists(memory_file)}")
        if os.path.exists(memory_file):
            try:
                with open(memory_file, "r") as f:
                    memory = json.load(f)
                    print(f"Memory loaded for user {user_id}: {memory}")
                    return memory
            except Exception as e:
                print(f"Error reading file for user {user_id}: {e}")
        else:
            print(f"Memory file not found for user {user_id}, returning default.")
        return {"summaries": [], "recent_messages": []}
            
    def save_user_memory(self, user_id, memory):
        """Save memory for a specific user to a JSON file."""
        memory_file = os.path.join(self.memory_dir, f"{user_id}.json")
        with open(memory_file, "w") as f:
            json.dump(memory, f, indent=2)
            print(f"Memory for user {user_id} saved successfully.")

    def add_to_temp_memory(self, user_id, message):
        """Add a message to the temporary memory."""
        if user_id not in self.temp_memory:
            self.temp_memory[user_id] = []
        self.temp_memory[user_id].append(message)

    async def generate_summary(self, user_id):
        """Generate a summary of the last 15 messages."""
        user_memory = self.load_user_memory(user_id)
        recent_messages = user_memory["recent_messages"]

        # If there aren't enough messages, skip summarization
        if len(recent_messages) < self.summary_threshold:
            return

        summary_prompt = (
            "Summarize the following conversation in no more than 5 lines. "
            "Focus on key topics and exchanges between the user and the assistant."
        )
        summarization_request = [{"role": "system", "content": summary_prompt}] + recent_messages

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=summarization_request,
            )
            summary = response.choices[0].message.content.strip()

            # Save the summary and clear recent messages
            user_memory["summaries"].append(summary)
            user_memory["recent_messages"] = []
            self.save_user_memory(user_id, user_memory)
            print(f"Summary generated for user {user_id}: {summary}")
        except Exception as e:
            print(f"Error generating summary for user {user_id}: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return

        user_id = str(message.author.id)
        self.add_to_temp_memory(user_id, {"role": "user", "content": message.content})
    
        # Process only if the bot is mentioned
        if self.bot.user in message.mentions:
            print(1)
            user_memory = self.load_user_memory(user_id)
            print(2)
            recent_messages = user_memory["recent_messages"]
            print(3)
            # Add the user's message to recent messages
            recent_messages.append({"role": "user", "content": message.content})
            print(4)
            assistant_message = f"The user's name is {message.author.display_name}. Use this name in replies. "
            assistant_message += self.knowledge
            print("5")

            try:
                print("6")
                async with message.channel.typing():
                    response = self.client.chat.complete(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.personality},
                            {"role": "assistant", "content": assistant_message},
                            *recent_messages,
                        ],
                    )
                ai_reply = response.choices[0].message.content
                print("5")
                # Add assistant reply to recent messages
                recent_messages.append({"role": "assistant", "content": ai_reply})
                user_memory["recent_messages"] = recent_messages
                print("6")
                # Save user memory and track message count
                self.message_counter[user_id] = self.message_counter.get(user_id, 0) + 1
                if self.message_counter[user_id] >= self.summary_threshold:
                    await self.generate_summary(user_id)
                    self.message_counter[user_id] = 0  # Reset counter

                self.save_user_memory(user_id, user_memory)

                # Send the AI's response
                await message.channel.send(ai_reply)
            except Exception as e:
                await message.channel.send("Oops, something went wrong while processing your request.")
                print(f"Error: {e}")

    @commands.command(name="view_summaries")
    async def view_summaries(self, ctx, user_id=None):
        """View summaries for a specific user."""
        if not user_id:
            user_id = str(ctx.author.id)

        user_memory = self.load_user_memory(user_id)
        summaries = user_memory.get("summaries", [])

        if summaries:
            summary_text = "\n\n".join([f"- {summary}" for summary in summaries])
            await ctx.send(f"**Conversation Summaries for User {user_id}:**\n{summary_text}")
        else:
            await ctx.send("No summaries available for this user.")

# Function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(MistralCog(bot))
