import discord
from src import storage
from src.utils.helpers import format_price
from src.utils.logging import BotLogger
from datetime import datetime

class VouchModal(discord.ui.Modal, title="Submit Vouch"):
    """Modal for submitting a vouch"""
    def __init__(self, seller: discord.Member | discord.User):
        super().__init__()
        self.seller = seller
    
    product = discord.ui.TextInput(
        label="Product/Service",
        placeholder="What did you purchase? (e.g., Account, Profile, MFA, Coins)",
        required=True,
        max_length=100
    )
    value = discord.ui.TextInput(
        label="Value (USD)",
        placeholder="How much did you pay? (e.g., 50.00)",
        required=True,
        max_length=20
    )
    review = discord.ui.TextInput(
        label="Review",
        placeholder="Your review/feedback about the transaction",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=500
    )
    rating = discord.ui.TextInput(
        label="Rating (1-5)",
        placeholder="Enter a number between 1 and 5",
        required=True,
        max_length=1
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        from src.utils.rate_limit import rate_limiter
        from src.utils.permissions import is_owner
        
        # Check blacklist
        if storage.is_blacklisted(interaction.guild_id, interaction.user.id):
            return await interaction.response.send_message("❌ You are blacklisted from using this bot.", ephemeral=True)
        
        # Rate limiting (5 vouches per 60 seconds, owners bypass)
        if not is_owner(interaction):
            allowed, retry_after = rate_limiter.check_rate_limit(
                interaction.user.id, 
                "vouch", 
                max_uses=5, 
                time_window=60
            )
            if not allowed:
                return await interaction.response.send_message(
                    f"⏳ You're using vouches too quickly. Please wait {retry_after:.1f} seconds.",
                    ephemeral=True
                )
        
        # Prevent self-vouching
        if self.seller.id == interaction.user.id:
            return await interaction.response.send_message("❌ You cannot vouch for yourself.", ephemeral=True)
        
        # Validate rating
        try:
            rating_value = int(self.rating.value)
            if rating_value < 1 or rating_value > 5:
                return await interaction.response.send_message("❌ Rating must be between 1 and 5.", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid rating. Please enter a number between 1 and 5.", ephemeral=True)
        
        # Validate value
        try:
            value_amount = float(self.value.value)
            if value_amount <= 0:
                return await interaction.response.send_message("❌ Value must be greater than 0.", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid value format. Please enter a valid number (e.g., 50.00).", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Get vouch number
        count = storage.get_vouch_count(interaction.guild_id, self.seller.id)
        vouch_number = count + 1
        
        # Record the vouch with full data
        storage.record_vouch_full(
            interaction.guild_id,
            self.seller.id,
            interaction.user.id,
            self.product.value,
            value_amount,
            self.review.value,
            rating_value,
            vouch_number,
            datetime.utcnow().isoformat()
        )
        
        # Create star display (only stars, no text)
        star_display = "⭐" * rating_value
        
        # Create minimal embed matching the image format
        embed = discord.Embed(
            color=0x5865f2,  # Discord blurple
            timestamp=interaction.created_at
        )
        
        # Set author with vouched by
        embed.set_author(
            name=f"Vouched by {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None
        )
        
        # Vouch number and review
        embed.add_field(name=f"Vouch #{vouch_number}", value=self.review.value, inline=False)
        
        # Three columns: Seller, Product ($value), Rating
        embed.add_field(name="Seller", value=self.seller.mention, inline=True)
        embed.add_field(name=f"Product ({format_price(value_amount)})", value=self.product.value, inline=True)
        embed.add_field(name="Rating", value=star_display, inline=True)
        
        # Footer with ID and timestamp
        timestamp_str = datetime.utcnow().strftime("%d/%m/%Y • %I:%M %p")
        embed.set_footer(text=f"ID: {vouch_number - 1} | {timestamp_str}")
        
        # Send to vouch channel if configured
        cfg = storage.get_config(interaction.guild_id)
        vouch_channel_id = cfg.get("channels", {}).get("vouches")
        
        if vouch_channel_id:
            vouch_channel = interaction.guild.get_channel(vouch_channel_id)
            if vouch_channel:
                await vouch_channel.send(embed=embed)
                await interaction.followup.send("✅ Your vouch has been posted!", ephemeral=True)
                # Log vouch submission
                await BotLogger.log_vouch_submitted(interaction.guild, interaction.user, self.seller, rating_value)
            else:
                await interaction.followup.send("⚠️ Vouch channel not found. Please contact an admin.", ephemeral=True)
        else:
            # Send to current channel if no vouch channel configured
            await interaction.channel.send(embed=embed)
            await interaction.followup.send("✅ Vouch posted!", ephemeral=True)
            # Log vouch submission
            await BotLogger.log_vouch_submitted(interaction.guild, interaction.user, self.seller, rating_value)

