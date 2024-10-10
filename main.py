import discord
from discord.ext import commands
import asyncio
from config import TOKEN, intents
import webserver 
import os

bot = commands.Bot(command_prefix='$', intents=intents)


# variables 
loding_heart = "<a:loading_heart:1294048090189332537>"
red_hearts = "<a:redhearts:1294048122011521064>"
# On ready event
@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if any(word in message.content.lower() for word in ("welcome", "wlc")):
        await message.add_reaction(loading_heart)
        await asyncio.sleep(1.8)
        await message.remove_reaction(loading_heart, bot.user)
        await asyncio.sleep(0.1)
        await message.add_reaction(red_hearts)
    await bot.process_commands(message)


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
