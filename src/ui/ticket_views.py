import discord
from datetime import datetime
import asyncio
from src import storage
from src.tickets.utils import get_ticket, close_ticket
from src.tickets.permissions import is_owner, has_staff_privs
from src.utils.logging import BotLogger

class OpenedTicketView(discord.ui.View):
    """View for opened tickets with close button"""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="ticket:close")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close the ticket"""
        # Check permissions
        if not has_staff_privs(interaction) and not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to close tickets.", ephemeral=True)
        
        ticket = get_ticket(interaction.guild_id, interaction.channel.id)
        if not ticket:
            return await interaction.response.send_message("❌ This is not a ticket channel.", ephemeral=True)
        
        if not ticket.get("is_open", True):
            return await interaction.response.send_message("❌ This ticket is already closed.", ephemeral=True)
        
        await interaction.response.defer()
        
        # Mark ticket as closed
        close_ticket(interaction.guild_id, interaction.channel.id)
        
        # Update channel permissions to make it read-only
        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            send_messages=False,
            read_messages=False,
            view_channel=False
        )
        
        # Allow ticket opener and staff to still view but not send
        opener = interaction.guild.get_member(ticket["opened_by"])
        if opener:
            await interaction.channel.set_permissions(
                opener,
                send_messages=False,
                read_messages=True,
                view_channel=True
            )
        
        # Create close embed
        close_embed = discord.Embed(
            title="Ticket Closed",
            description="This ticket has been closed.",
            color=discord.Color.orange()
        )
        close_embed.add_field(name="Closed By", value=interaction.user.mention, inline=False)
        
        await interaction.followup.send(embed=close_embed)
        
        # Update ticket data with closed timestamp and user
        ticket["closed_at"] = datetime.utcnow().isoformat()
        ticket["closed_by"] = interaction.user.id
        
        # Save updated ticket data
        from src.tickets.utils import save_ticket
        save_ticket(interaction.guild_id, ticket)
        
        # Log ticket closure (this will also generate transcript)
        await BotLogger.log_ticket_closed(interaction.guild, interaction.channel, interaction.user, ticket)
        
        # Delete channel after a short delay
        await interaction.followup.send("❌ Deleting ticket in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason="Ticket closed")
        except Exception as e:
            await interaction.followup.send(f"❌ Error deleting channel: {e}", ephemeral=True)

