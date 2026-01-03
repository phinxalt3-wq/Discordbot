import discord
from discord.ext import commands
from discord import app_commands
from src import storage
from src.utils.logging import BotLogger
from src.tickets.utils import get_ticket
from src.ui.vouch_views import VouchButtonView

class Vouch(commands.Cog):
    """Vouch system for seller reviews"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="vouch", description="Send a vouch request to a buyer in a ticket")
    @app_commands.describe(buyer="The buyer to request a vouch from")
    async def vouch(self, interaction: discord.Interaction, buyer: discord.Member):
        """Send a vouch request message with a button in the ticket"""
        from src.utils.permissions import is_owner, is_staff
        
        # Check if this is a ticket channel
        ticket_data = get_ticket(interaction.guild_id, interaction.channel.id)
        if not ticket_data:
            return await interaction.response.send_message(
                "❌ This command can only be used in ticket channels.",
                ephemeral=True
            )
        
        # Only staff/owner can use this command
        if not is_owner(interaction) and not is_staff(interaction):
            return await interaction.response.send_message(
                "❌ Only staff members can request vouches.",
                ephemeral=True
            )
        
        # Get seller from ticket (opened_by)
        seller_id = ticket_data.get("opened_by")
        if not seller_id:
            return await interaction.response.send_message(
                "❌ Could not determine seller from ticket data.",
                ephemeral=True
            )
        
        seller = interaction.guild.get_member(seller_id) or interaction.client.get_user(seller_id)
        if not seller:
            return await interaction.response.send_message(
                "❌ Seller not found.",
                ephemeral=True
            )
        
        await interaction.response.defer()
        
        # Create embed for vouch request
        embed = discord.Embed(
            title="⭐ Vouch Request",
            description=f"{buyer.mention}, please leave a vouch for {seller.mention} by clicking the button below.",
            color=0x5865f2,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="Transaction Details",
            value=f"**Seller:** {seller.mention}\n**Buyer:** {buyer.mention}",
            inline=False
        )
        embed.set_footer(text="Click the button below to submit your vouch")
        
        # Send message with button
        view = VouchButtonView(seller.id)
        await interaction.channel.send(
            content=buyer.mention,
            embed=embed,
            view=view
        )
        
        await interaction.followup.send("✅ Vouch request sent!", ephemeral=True)
    
    @app_commands.command(name="restore_vouches", description="Restore all vouches to a new channel (Owner only)")
    @app_commands.describe(channel="Channel to restore vouches to")
    async def restore_vouches(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Restore all stored vouches to a new channel"""
        from src.utils.permissions import is_owner
        from datetime import datetime
        
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Get all vouches for this guild
        vouches = storage.get_all_vouches(interaction.guild_id)
        
        if not vouches:
            return await interaction.followup.send("❌ No vouches found to restore.", ephemeral=True)
        
        # Sort by vouch number
        sorted_vouches = sorted(vouches, key=lambda x: x.get('vouch_number', 0))
        
        restored_count = 0
        for vouch_data in sorted_vouches:
            try:
                # Get seller and vouched_by users
                seller_id = vouch_data.get('seller_id')
                vouched_by_id = vouch_data.get('vouched_by_id')
                
                seller = interaction.guild.get_member(seller_id) or interaction.client.get_user(seller_id)
                vouched_by = interaction.guild.get_member(vouched_by_id) or interaction.client.get_user(vouched_by_id)
                
                if not seller or not vouched_by:
                    continue
                
                # Create embed
                star_display = "⭐" * vouch_data.get('rating', 5)
                vouch_number = vouch_data.get('vouch_number', 0)
                product = vouch_data.get('product', 'Unknown')
                value = vouch_data.get('value', 0.0)
                review = vouch_data.get('review', 'No review')
                
                embed = discord.Embed(
                    color=0x5865f2,
                    timestamp=datetime.fromisoformat(vouch_data.get('timestamp', datetime.utcnow().isoformat()))
                )
                
                embed.set_author(
                    name=f"Vouched by {vouched_by.name}",
                    icon_url=vouched_by.display_avatar.url if vouched_by.display_avatar else None
                )
                
                embed.add_field(name=f"Vouch #{vouch_number}", value=review, inline=False)
                embed.add_field(name="Seller", value=seller.mention, inline=True)
                embed.add_field(name=f"Product ({format_price(value)})", value=product, inline=True)
                embed.add_field(name="Rating", value=star_display, inline=True)
                
                timestamp_str = datetime.fromisoformat(vouch_data.get('timestamp', datetime.utcnow().isoformat())).strftime("%d/%m/%Y • %I:%M %p")
                embed.set_footer(text=f"ID: {vouch_number - 1} | {timestamp_str}")
                
                await channel.send(embed=embed)
                restored_count += 1
                
            except Exception as e:
                print(f"Error restoring vouch: {e}")
                continue
        
        await interaction.followup.send(f"✅ Restored {restored_count} vouches to {channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Vouch(bot))
