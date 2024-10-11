import discord
from discord.ext import commands
import datetime

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_tickets = {}  # Store user ID and their ticket channel

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if the message is a DM and not from a bot
        if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
            # Ask if the user wants to create a ticket
            await message.channel.send("Hello! Do you want to create a ticket? Reply with 'yes' to proceed.")

            def check(msg):
                return msg.author == message.author and isinstance(msg.channel, discord.DMChannel)

            try:
                # Wait for the user's response
                response = await self.bot.wait_for("message", check=check, timeout=60)
                if response.content.lower() == "yes":
                    await self.create_ticket(message.author)
                else:
                    await message.channel.send("No ticket created. Let me know if you need anything else.")
            except discord.TimeoutError:
                await message.channel.send("Request timed out. Please message again if you need help.")

    async def create_ticket(self, user):
        # Find the category where you want to create the ticket channels
        guild = self.bot.get_guild(1264302631174668299)  # Replace with your server ID
        category = discord.utils.get(guild.categories, name="⇛ 《🎟》Tickets")  # Make sure the category name matches

        # Create a new channel for the ticket
        ticket_channel = await guild.create_text_channel(
            f"ticket-{user.name}",
            category=category
        )

        # Ping the mods role
        mods_role = discord.utils.get(guild.roles, name="Ticket Manager")  # Replace with your moderators role name
        await ticket_channel.send(f"{mods_role.mention} New ticket created by {user.mention}.")

        # Store the ticket info
        self.active_tickets[user.id] = ticket_channel.id

        # Inform the user that the ticket has been created
        await user.send("Your ticket has been created! A moderator will be with you shortly.")

    @commands.Cog.listener()
    async def on_message_ticket(self, message):
        # Handle messages in the ticket channel
        if message.channel.id in self.active_tickets.values() and not message.author.bot:
            user_id = [uid for uid, cid in self.active_tickets.items() if cid == message.channel.id][0]
            user = self.bot.get_user(user_id)
            if user:
                await user.send(f"**{message.author}:** {message.content}")

    @commands.Cog.listener()
    async def on_message_dm(self, message):
        # Handle replies from the user in the DM
        if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
            if message.author.id in self.active_tickets:
                ticket_channel_id = self.active_tickets[message.author.id]
                ticket_channel = self.bot.get_channel(ticket_channel_id)
                if ticket_channel:
                    await ticket_channel.send(f"**{message.author}:** {message.content}")

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
