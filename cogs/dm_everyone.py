import discord
from discord.ext import commands
import asyncio
from config import TOKEN, intents

class dm_everyone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)  # Ensure only admins can use it
    async def dm_all(self, ctx, guild_id: int, *, message: str):
        
        save_server=[1264302631174668299, 1282315062756769803] # User will be able to add their server using command later
        
        if guild_id in save_server:
            await ctx.send("You can't use that command on that server.")
            return 
        
        guild = self.bot.get_guild(guild_id)  # Get the guild
        
        if guild is None:  # Check if the guild exists
            await ctx.send("Guild not found. Please provide a valid server ID.")
            return 
        print("Server exist!")
        
        guild_members = len([member for member in guild.members if not member.bot])  # Count non-bot members
        
        success_dm = 0  # Successful direct messages 
        failed_dm = 0  # Failed direct messages 
        loading_emoji = "🕑"  #"<a:loading_circle:1292501983516688518>"
        dots_loading =  "⏳" #"<a:loading_dots:1292502000675586119>"

        # Create an embed for the progress message
        embed = discord.Embed(
            title=f"DM Progress {dots_loading}",
            description=f"Sending DMs to {guild_members} members in progress..\n✅ Successful dms: **{success_dm}**\n❌ Failed dms: **{failed_dm}**",
            color=discord.Color.from_str("#f2f7f2")
        )
        
        
        progress_message = await ctx.send(embed=embed)
        await progress_message.add_reaction(loading_emoji)
        print("Embed sent!")
        
        
        
        skip_users = [1207272606210990112, 716390085896962058]
        non_guild = 1264302631174668299
        
        
        
        for member in guild.members:
            # add the members who has the non guild as a mutual server to the skip list
            if self.bot.get_guild(non_guild) in member.mutual_guilds:
                skip_users.append(member)
                
            if not member.bot:
                try:
                    # check if User in the skip list or not
                    if not member in skip_users:
                        await member.send(message)  # Send message
                        success_dm += 1
                    else:    
                        print(f"{member.name} has been skipped.")
                          
                except discord.Forbidden:
                    failed_dm += 1
                    print(f"Failed to send DM to {member.name}: DMs are disabled.")  # Log the issue
                except Exception as e:
                    failed_dm += 1
                    print(f"An error occurred while sending DM to {member.name}: {e}")  # Log the issue
                # Update embed
                embed.description=f"Sending DMs to {guild_members} members in progress..\n✅ Successful dms: **{success_dm}**\n❌ Failed dms: **{failed_dm}**"
                await progress_message.edit(embed=embed)    
                await asyncio.sleep(3) 
           
        await progress_message.remove_reaction(loading_emoji, self.bot.user)
        embed.title="Finished. ✅"
        embed.description=f"DMs sent to {success_dm} members. Failed to send to {failed_dm} members."
        embed.color=discord.Color.from_str("#05e605")
        await progress_message.edit(embed=embed)    

async def setup(bot):
    await bot.add_cog(dm_everyone(bot))
