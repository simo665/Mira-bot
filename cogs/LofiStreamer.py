import discord
from discord.ext import commands
import yt_dlp as youtube_dl  # Changed from youtube_dl to yt_dlp
import asyncio

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

YTDL_OPTIONS = {
    'format': 'bestaudio',
    'quiet': True,
}

ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

# A list of stable Lofi URLs (Replace with reliable URLs as needed)
LOFI_PLAYLIST = [
    'https://www.youtube.com/watch?v=jfKfPfyJRdk',  # Lofi Girl Stream
    'https://www.youtube.com/watch?v=DWcJFNfaw9c',  # Another Lofi Stream
    'https://www.youtube.com/watch?v=5qap5aO4i9A'   # Additional Lofi Stream
]

class LofiStreamer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.current_index = 0

    @commands.command(name='join', help='Join the voice channel and start streaming Lofi.')
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            try:
                self.voice_client = await channel.connect()
                await ctx.send(f"Joined {channel}. Streaming Lofi playlist...")
                await self.play_lofi()
            except Exception as e:
                print(f"An error occurred when connecting: {e}")
                await ctx.send("An error occurred when connecting to the voice channel.")
        else:
            await ctx.send("You need to be in a voice channel to use this command.")
            
    @commands.command(name='leave', help='Disconnect the bot from the voice channel.')
    async def leave(self, ctx):
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect()
            self.voice_client = None
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    async def play_lofi(self):
        while self.voice_client and self.voice_client.is_connected():
            try:
                # Get the current Lofi URL from the playlist
                current_url = LOFI_PLAYLIST[self.current_index]
                info = ytdl.extract_info(current_url, download=False)
                url = info['url']

                # Play the current URL
                self.voice_client.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after=self.after_play)
                
                # Wait until the bot stops playing
                while self.voice_client.is_playing() or self.voice_client.is_paused():
                    await asyncio.sleep(1)

                # Move to the next song in the playlist
                self.current_index = (self.current_index + 1) % len(LOFI_PLAYLIST)

            except Exception as e:
                print(f"An error occurred: {e}")
                # Move to the next track if an error occurs
                self.current_index = (self.current_index + 1) % len(LOFI_PLAYLIST)
                await asyncio.sleep(10)  # Wait before retrying

    def after_play(self, error):
        if error:
            print(f"An error occurred: {error}")
        # No additional actions needed here since play_lofi() loops automatically

async def setup(bot):
    await bot.add_cog(LofiStreamer(bot))
