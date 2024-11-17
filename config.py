from dotenv import load_dotenv
import os
import discord 

# Bot requirements 
load_dotenv()
TOKEN=os.getenv('BOT_TOKEN')
API=os.getenv('AI_API')

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True  
intents.voice_states = True
