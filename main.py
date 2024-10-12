import discord
from discord.ext import commands
import asyncio
from config import TOKEN, intents
import webserver 
import os

bot = commands.Bot(command_prefix='$', intents=intents)

# On ready event
@bot.event
async def on_ready():
    print(f'{bot.user} is online')


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
