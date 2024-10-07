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
    print(f'Bot is online as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
        
    if message.content == "simo":
        await message.channel.send("Simo the best ❤️")
    if message.content.lower() in ("welcome", "wlc"):
        await message.add_reaction("<a:Love_loading:1281304555904303145>")
        await asyncio.sleep(1.8)
        await message.remove_reaction("<a:Love_loading:1281304555904303145>", bot.user)
        await asyncio.sleep(0.1)
        await message.add_reaction("<a:heartsFlyingR:1281304524304416818>")
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
