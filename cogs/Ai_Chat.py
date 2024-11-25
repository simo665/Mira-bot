import discord
import json
import os
from discord.ext import commands, tasks
from mistralai import Mistral
from config import api_key, knowledge, personality, memory_length, save_threshold
import importlib

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
        self.save_threshold = save_threshold  # Save memory after specific number of messages every time 
        self.message_counter = 0
        # customization 
        self.user = None
        self.memory_length = memory_length
        self.personality = personality 
        self.knowledge = knowledge
        self.save_memory_task.start()  # Start periodic memory saving task
        
        
        
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
            
    def increment_message_counter(self):
        """Increment the message counter and save memory if threshold is reached."""
        self.message_counter += 1
        if self.message_counter >= self.save_threshold:
            self.save_memory()
            self.message_counter = 0  # Reset the counter
            
            
    @commands.Cog.listener()
    async def on_message(self, message):
        # AI Assistance
        self.user = message.author.display_name
        assistant = f"The user's name is {self.user}. You can use this name in your replies to personalize them. " 
        assistant += self.knowledge
        # Ignore messages from bots
        if message.author.bot:
            return 

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
                
        increment_message_counter()      
          
        if self.bot.user in message.mentions:
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
        
        
        
# *******  Commands  *******       
    @commands.command(name="sleep")
    @commands.has_permissions(administrator=True)
    async def save_memory_command(self, ctx):
        """Manually save memory to file."""
        self.save_memory()
        await ctx.send("Memory saved manually.")  
        
    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_memory(self, ctx, channel_id=None, user_id=None):
        """Reset memory for a channel or specific user."""
        channel_id = channel_id or str(ctx.channel.id)
        if channel_id in self.memory:
            if user_id:
                user_id = str(user_id)
                if user_id in self.memory[channel_id]:
                    del self.memory[channel_id][user_id]
                    await ctx.send(f"Memory for user {user_id} in channel {channel_id} has been reset.")
                else:
                    await ctx.send("No memory found for that user in this channel.")
            else:
                del self.memory[channel_id]
                await ctx.send(f"Memory for channel {channel_id} has been reset.")
            self.save_memory()
        else:
            await ctx.send("No memory found for this channel.")    
            
            
    @commands.command(name="set_personality")
    @commands.has_permissions(administrator=True)
    async def set_personality(self, ctx, *, new_personality):
        """Change the personality dynamically."""
        self.personality = new_personality
        await ctx.send("Personality has been updated.")
        print(f"New personality: {self.personality}")

    @commands.command(name="reload_personality")
    @commands.has_permissions(administrator=True)
    async def reload_personality(self, ctx):
        """Reload personality from the config file."""
        importlib.reload(config)  # Reload the config module
        self.personality = config.personality  # Update the personality from config
        await ctx.send("Personality has been reloaded from the config file.")
                    
# Function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(MistralCog(bot))
