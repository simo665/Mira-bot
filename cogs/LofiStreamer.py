import discord
from discord.ext import commands
import asyncio
import requests

class LofiStreamer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.is_playing = False

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
        LOFI_STREAM_URL = 'https://fluxfm.streamabc.net/flx-chillhop-mp3-128-8581707?sABC=671534s2%230%23pq35s4858p08p687on3n1pr3on77ssr0%23fgernzf.syhksz.qr&aw_0_1st.playerid=streams.fluxfm.de&amsparams=playerid:streams.fluxfm.de;skey:1729443058'  # Your streaming URL

        if self.voice_client and self.voice_client.is_connected() and not self.is_playing:
            self.is_playing = True
            
            # Play the audio stream directly
            audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(LOFI_STREAM_URL), volume=0.5)
            self.voice_client.play(audio_source, after=self.after_play)
            await asyncio.sleep(1)  # Small delay to ensure audio starts playing

    def after_play(self, error):
        if error:
            print(f"An error occurred: {error}")
        self.is_playing = False  # Allow replaying after one completes

async def setup(bot):
    await bot.add_cog(LofiStreamer(bot))
