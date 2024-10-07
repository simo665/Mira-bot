from dotenv import load_dotenv
import os
import discord 

# Bot requirements 
load_dotenv()
TOKEN=os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True  