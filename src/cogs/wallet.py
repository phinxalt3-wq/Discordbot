import discord
from discord.ext import commands
from discord import app_commands
from src import storage
from src.utils.permissions import is_owner

class Wallet(commands.Cog):
    """Crypto wallet address management"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ltcaddy", description="Add or update a crypto wallet address (Owner only)")
    @app_commands.describe(
        crypto_type="Type of cryptocurrency (e.g., BTC, ETH, LTC, USDT)",
        address="The wallet address"
    )
    async def ltcaddy(
        self,
        interaction: discord.Interaction,
        crypto_type: str,
        address: str
    ):
        """Add or update a crypto wallet address"""
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        # Basic validation
        if len(address) < 10:
            return await interaction.response.send_message("❌ Invalid wallet address. Address is too short.", ephemeral=True)
        
        if len(address) > 200:
            return await interaction.response.send_message("❌ Invalid wallet address. Address is too long.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Store wallet
        storage.add_wallet(interaction.guild_id, crypto_type, address)
        
        embed = discord.Embed(
            title="✅ Wallet Address Added",
            description=f"**{crypto_type.upper()}** wallet address has been saved.",
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Address", value=f"`{address}`", inline=False)
        embed.set_footer(text=f"Added by {interaction.user.name}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="wallet", description="View a crypto wallet address")
    @app_commands.describe(crypto_type="Type of cryptocurrency (e.g., BTC, ETH, LTC, USDT)")
    async def wallet(self, interaction: discord.Interaction, crypto_type: str):
        """View a crypto wallet address"""
        address = storage.get_wallet(interaction.guild_id, crypto_type)
        
        if not address:
            return await interaction.response.send_message(
                f"❌ No {crypto_type.upper()} wallet address found. Use `/ltcaddy` to add one.",
                ephemeral=True
            )
        
        embed = discord.Embed(
            title=f"{crypto_type.upper()} Wallet Address",
            description=f"`{address}`",
            color=0x3498db,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Hypixel Account Shop")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="wallets", description="View all stored wallet addresses (Owner only)")
    async def wallets(self, interaction: discord.Interaction):
        """View all stored wallet addresses"""
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        all_wallets = storage.get_all_wallets(interaction.guild_id)
        
        if not all_wallets:
            return await interaction.followup.send("❌ No wallet addresses stored.", ephemeral=True)
        
        embed = discord.Embed(
            title="📋 Stored Wallet Addresses",
            color=0x3498db,
            timestamp=discord.utils.utcnow()
        )
        
        for crypto_type, address in all_wallets.items():
            embed.add_field(name=crypto_type, value=f"`{address}`", inline=False)
        
        embed.set_footer(text=f"Total: {len(all_wallets)} wallets")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="remove_wallet", description="Remove a crypto wallet address (Owner only)")
    @app_commands.describe(crypto_type="Type of cryptocurrency to remove")
    async def remove_wallet(self, interaction: discord.Interaction, crypto_type: str):
        """Remove a crypto wallet address"""
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        if storage.remove_wallet(interaction.guild_id, crypto_type):
            await interaction.response.send_message(
                f"✅ {crypto_type.upper()} wallet address removed.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ No {crypto_type.upper()} wallet address found.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Wallet(bot))

