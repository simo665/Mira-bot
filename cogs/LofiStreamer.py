import discord
from discord.ext import commands
import asyncio

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Replace with your direct lofi audio stream URL
LOFI_STREAM_URL = 'https://fluxfm.streamabc.net/flx-chillhop-mp3-128-8581707?sABC=671534s2%230%23pq35s4858p08p687on3n1pr3on77ssr0%23fgernzf.syhksz.qr&aw_0_1st.playerid=streams.fluxfm.de&amsparams=playerid:streams.fluxfm.de;skey:1729443058'  # Example URL

class LofiStreamer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None

    @commands.command(name='join', help='Join the voice channel and start streaming Lofi.')
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            try:
                self.voice_client = await channel.connect()
                await ctx.send(f"Joined {channel}. Streaming Lofi...")
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
                # Play the direct audio stream URL
                self.voice_client.play(discord.FFmpegPCMAudio(LOFI_STREAM_URL, **FFMPEG_OPTIONS))

                # Wait until the bot stops playing
                while self.voice_client.is_playing():
                    await asyncio.sleep(1)

            except Exception as e:
                print(f"An error occurred: {e}")
                await asyncio.sleep(10)  # Wait before retrying

async def setup(bot):
    await bot.add_cog(LofiStreamer(bot))
