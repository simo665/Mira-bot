from dotenv import load_dotenv
import os
import discord 

# Bot requirements 
load_dotenv()
TOKEN=os.getenv('BOT_TOKEN')
api_key=os.environ["MISTRAL_API_KEY"]

intents = discord.Intents.default()
intents.presences = True 
intents.members = True 
intents.message_content = True  
intents.voice_states = True
