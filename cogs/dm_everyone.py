import discord
from discord.ext import commands
import asyncio
import random 

class dm_everyone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def dm_all(self, ctx, guild_id: int, *, message: str):
        save_server = [1264302631174668299, 1282315062756769803]
        
        if guild_id in save_server:
            await ctx.send("You can't use that command on that server.")
            return 
        
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await ctx.send("Guild not found. Please provide a valid server ID.")
            return 
        
        guild_members = len([member for member in guild.members if not member.bot])
        success_dm = 0
        failed_dm = 0
        skipped_members = 0
        loading_emoji = "🕑"
        dots_loading = "⏳"
        delay = 0
        skip_users = [929953931143041064]
        non_guild = 1264302631174668299
        batch_count = 0
        
        embed = discord.Embed(
            title=f"DM Progress {dots_loading}",
            description=f"Sending DMs to {guild_members} members in progress..\n✅ Successful DMs: **{success_dm}**\n❌ Failed DMs: **{failed_dm}**\n🐾 Skipped members: **{skipped_members}**\n⏲️ Delay: **{delay}**",
            color=discord.Color.from_str("#f2f7f2")
        )
        
        progress_message = await ctx.send(embed=embed)
        await progress_message.add_reaction(loading_emoji)
        
        for member in guild.members:
            if self.bot.get_guild(non_guild) in member.mutual_guilds:
                skip_users.append(member)
                skipped_members += 1
            
            if not member.bot and member not in skip_users:
                if guild_members <= 50:
                    try:
                        await member.send(message)
                        success_dm += 1
                    except discord.Forbidden:
                        failed_dm += 1
                    except Exception as e:
                        failed_dm += 1
                    
                    embed.description = f"Sending DMs to {guild_members} members in progress..\n✅ Successful DMs: **{success_dm}**\n❌ Failed DMs: **{failed_dm}**\n🐾 Skipped members: **{skipped_members}**\n⏲️ Delay: **{delay}**"
                    await progress_message.edit(embed=embed)
                    delay = 0.5 + (guild_members * 1)/100
                    await asyncio.sleep(delay)
                else:
                    await ctx.send("Large server detected. Sending DMs in batches...")
                    batch_size = 10
                    members_list = [m for m in guild.members if not m.bot]
                    for i in range(0, len(members_list), batch_size):
                        batch = members_list[i:i + batch_size]
                        for member in batch:
                            try:
                                await member.send(message)
                                success_dm += 1
                            except discord.Forbidden:
                                failed_dm += 1
                                continue
                            except Exception as e:
                                failed_dm += 1
                                continue
                            
                            embed.description = f"Sending DMs to {guild_members} members in progress..\n✅ Successful DMs: **{success_dm}**\n❌ Failed DMs: **{failed_dm}**\n🐾 Skipped members: **{skipped_members}**\n⏲️ Delay: **{delay}**\n🔁 Batch: **{batch_count}**"
                            await progress_message.edit(embed=embed)
                            delay = 0.5 + (guild_members * 1)/100
                            await asyncio.sleep(delay)
                        batch_count += 1
                        await asyncio.sleep(random.randint(30, 60))
           
        await progress_message.remove_reaction(loading_emoji, self.bot.user)
        embed.title = "Finished. ✅"
        embed.description = f"DMs sent to {success_dm} members. Failed to send to {failed_dm} members. {skipped_members} have been skipped."
        embed.color = discord.Color.from_str("#05e605")
        await progress_message.edit(embed=embed)    

async def setup(bot):
    await bot.add_cog(dm_everyone(bot))
