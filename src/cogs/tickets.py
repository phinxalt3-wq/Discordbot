import discord
from discord import app_commands
from discord.ext import commands
from src import storage
from src.tickets.utils import get_ticket, close_ticket
from src.utils.logging import BotLogger
from src.utils.permissions import has_staff_privs, is_owner

class Tickets(commands.Cog):
    """Ticket management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="close", description="Close the current ticket")
    async def close(self, interaction: discord.Interaction):
        # Check if channel is a ticket
        ticket_data = get_ticket(interaction.guild_id, interaction.channel.id)
        if not ticket_data or not ticket_data.get("is_open", False):
            await interaction.response.send_message("❌ This is not an open ticket channel.", ephemeral=True)
            return
        
        # Check permissions (only staff or ticket opener can close)
        is_staff = has_staff_privs(interaction)
        is_opener = str(interaction.user.id) == str(ticket_data.get("opened_by"))
        
        if not (is_staff or is_opener):
            await interaction.response.send_message("❌ You don't have permission to close this ticket.", ephemeral=True)
            return
        
        await interaction.response.send_message("🔒 Closing ticket...", ephemeral=False)
        
        # Log closing and generate transcript
        try:
            await BotLogger.log_ticket_closed(interaction.guild, interaction.channel, interaction.user, ticket_data)
        except Exception as e:
            print(f"Error logging ticket close: {e}")
        
        # Mark as closed in DB
        close_ticket(interaction.guild_id, interaction.channel.id)
        
        # Delete channel
        try:
            await interaction.channel.delete(reason=f"Ticket closed by {interaction.user.name}")
        except Exception as e:
            print(f"Error deleting channel: {e}")
            await interaction.followup.send(f"❌ Error deleting channel: {e}", ephemeral=True)

    @app_commands.command(name="add", description="Add a user to the ticket")
    @app_commands.describe(user="User to add to the ticket")
    async def add(self, interaction: discord.Interaction, user: discord.Member):
        # Check if channel is a ticket
        ticket_data = get_ticket(interaction.guild_id, interaction.channel.id)
        if not ticket_data or not ticket_data.get("is_open", False):
            await interaction.response.send_message("❌ This is not an open ticket channel.", ephemeral=True)
            return
        
        # Check permissions (only staff)
        if not has_staff_privs(interaction):
            await interaction.response.send_message("❌ Only staff can add users to tickets.", ephemeral=True)
            return
        
        try:
            await interaction.channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)
            await interaction.response.send_message(f"✅ Added {user.mention} to the ticket.", ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error adding user: {e}", ephemeral=True)

    @app_commands.command(name="remove", description="Remove a user from the ticket")
    @app_commands.describe(user="User to remove from the ticket")
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
        # Check if channel is a ticket
        ticket_data = get_ticket(interaction.guild_id, interaction.channel.id)
        if not ticket_data or not ticket_data.get("is_open", False):
            await interaction.response.send_message("❌ This is not an open ticket channel.", ephemeral=True)
            return
        
        # Check permissions (only staff)
        if not has_staff_privs(interaction):
            await interaction.response.send_message("❌ Only staff can remove users from tickets.", ephemeral=True)
            return
            
        try:
            await interaction.channel.set_permissions(user, overwrite=None)
            await interaction.response.send_message(f"✅ Removed {user.mention} from the ticket.", ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error removing user: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))