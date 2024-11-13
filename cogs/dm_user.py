import discord
from discord.ext import tasks, commands
from discord import app_commands
import asyncio
import json
import os

class DMConversation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_conversations = {}
        self.inactivity_times = {}
        self.used_dm_users = self.load_used_dm_users()
        self.blocked_users = self.load_blocked_users()

    def load_used_dm_users(self):
        if os.path.exists('user/dms_config.json'):
            with open('user/dms_config.json', 'r') as f:
                data = json.load(f)
                return data.get("used_dm_users", {})
        return {}

    def load_blocked_users(self):
        if os.path.exists('user/dms_config.json'):
            with open('user/dms_config.json', 'r') as f:
                data = json.load(f)
                return data.get("blocked_users", {})
        return {}

    def save_blocked_users(self):
        data = {"used_dm_users": self.used_dm_users, "blocked_users": self.blocked_users}
        with open('user/dms_config.json', 'w') as f:
            json.dump(data, f)

    def get_dm_rules(self):
        return """
**Rules:**
1. **Respect privacy**—no harassment or stalking.
2. **No spamming** or excessive messaging.
3. **Keep it respectful**—no bullying or inappropriate behavior.
4. **No threats or abusive language**.
5. **No unsolicited advertising**.
6. **Ensure both users consent** to a conversation.
7. **Do not impersonate others**.
8. **Avoid sharing sensitive personal information**.
9. **No advertising.**
        """

    @app_commands.command(name="start")
    async def start(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user.id in self.blocked_users.get(str(user.id), []):
            await interaction.response.send_message(f"You are blocked by {user.display_name} and cannot start a DM with them.", ephemeral=True)
            return
        elif user.id in self.blocked_users.get(str(interaction.user.id), []):
            await interaction.response.send_message(f"You have blocked {user.display_name}. Unblock them to start a conversation.", ephemeral=True)
            return
        
        if interaction.user.id in self.active_conversations or user.id in self.active_conversations:
            await interaction.response.send_message("Either you or the selected user is already in an active conversation. End it before starting a new one.", ephemeral=True)
            return
        
        if interaction.user.id not in self.used_dm_users:
            embed = discord.Embed(
                title="⚠️ **DM Conversation Rules** ⚠️",
                description=self.get_dm_rules(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            self.used_dm_users[interaction.user.id] = True
            self.save_blocked_users()

        self.active_conversations[interaction.user.id] = user.id
        self.active_conversations[user.id] = interaction.user.id
        self.inactivity_times[interaction.user.id] = asyncio.get_event_loop().time()

        await interaction.response.send_message(f"Conversation started with {user.name}.", ephemeral=True)
        await user.send(f"""
{interaction.user.display_name} has started a conversation with you.
Actions available:
> * 0. Listen to what they will say.
> * 1. Block: `/block`
> * 2. Report if they misbehave: `/report`
> * 3. Close this conversation: `/close`
""", ephemeral=True)

    @app_commands.command(name="close")
    async def close(self, interaction: discord.Interaction):
        user_id = self.active_conversations.get(interaction.user.id)
        
        if user_id:
            user = self.bot.get_user(user_id)
            if user:
                await user.send(f"{interaction.user.display_name} has ended the conversation.")
            await interaction.response.send_message(f"Conversation with {user.name if user else 'user'} has been closed.", ephemeral=True)

            del self.active_conversations[interaction.user.id]
            del self.active_conversations[user_id]
            del self.inactivity_times[interaction.user.id]
            self.delete_saved_files()

        else:
            await interaction.response.send_message("You have no active conversations to close.", ephemeral=True)

    @app_commands.command(name="block")
    async def block(self, interaction: discord.Interaction, user: discord.User = None):
        if user is None and interaction.user.id in self.active_conversations:
            user = self.bot.get_user(self.active_conversations[interaction.user.id])
        if user is None:
            await interaction.response.send_message("Specify a user to block.", ephemeral=True)
            return
        if user.id == interaction.user.id:
            await interaction.response.send_message("You cannot block yourself.", ephemeral=True)
            return

        self.blocked_users.setdefault(str(interaction.user.id), []).append(user.id)
        self.save_blocked_users()
        await interaction.response.send_message(f"{user.display_name} has been blocked successfully.", ephemeral=True)

        if user.id in self.active_conversations and self.active_conversations[user.id] == interaction.user.id:
            await self.close(interaction)

    @app_commands.command(name="report")
    async def report(self, interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            active_conversation = self.active_conversations.get(interaction.user.id)
            if active_conversation:
                user = self.bot.get_user(active_conversation)
                await self.close(interaction)
                await interaction.response.send_message(f"The conversation with {user.display_name} has been closed.", ephemeral=True)
            else:
                await interaction.response.send_message("Please specify a user to report or ensure you have an active conversation.", ephemeral=True)
                return

        embed = discord.Embed(
            title="⚠️ **DM Conversation Rules** ⚠️",
            description=self.get_dm_rules(),
            color=discord.Color.orange()
        )
        await interaction.response.send_message(f"{interaction.user.mention}, please review our rules and confirm if {user.display_name} broke any of them:", embed=embed, ephemeral=True)
        
        report_embed = discord.Embed(
            title=f"To report {user.display_name}",
            description=(
                "**Your report submitted successfully. Follow these steps**:\n"
                "> 1. Take screenshots of the conversation.\n"
                "> 2. Open a ticket.\n"
                "> 3. Send screenshots in the ticket.\n"
                "> 4. Wait for moderators to review your report."
            ),
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=report_embed, ephemeral=True)

    def delete_saved_files(self):
        conversation_file_path = "user/dms/conversation.txt"
        if os.path.exists(conversation_file_path):
            os.remove(conversation_file_path)

async def setup(bot):
    await bot.add_cog(DMConversation(bot))
