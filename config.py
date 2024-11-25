from dotenv import load_dotenv
import os
import discord 

# Bot requirements 
load_dotenv()
TOKEN=os.getenv('BOT_TOKEN') # Bot token 
api_key=os.environ["MISTRAL_API_KEY"] # Ai API
# Bot Intents
intents = discord.Intents.default() 
intents.presences = True 
intents.members = True 
intents.message_content = True  
intents.voice_states = True

# Ai bot configs
personality = "You're a little naughty girl, you write informally like a human, your replies always short" # bot personality details 
knowledge = "" # Include here what you want the bot to know about.. 
memory_length = 10
