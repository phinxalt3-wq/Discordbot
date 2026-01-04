import discord
from discord.ext import commands
from discord import app_commands
from src.ui.views import TicketPanel, MFAPanel, CoinPanel, AccountBuyPanel
from src import storage
from src.utils.permissions import is_owner
from src.utils.helpers import format_price
from datetime import datetime

class Panels(commands.Cog):
    """Commands to send shop panels"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ticket_panel", description="Send the ticket panel")
    async def ticket_panel(self, interaction: discord.Interaction):
        if not is_owner(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        cfg = storage.get_config(interaction.guild_id)
        banner_url = cfg.get("images", {}).get("ticket_banner")
        
        embed = discord.Embed(
            title="🎫  **Support & Sales Tickets**",
            description="Welcome to our support system! Please choose the appropriate category below to open a ticket.",
            color=0x2b2d31, # Dark Discord theme color
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📋  **Available Options**",
            value=(
                "> **Sell Account**\n"
                "> Sell your Minecraft account securely.\n\n"
                "> **Sell Profile**\n"
                "> Sell your Skyblock profile.\n\n"
                "> **Sell Alt**\n"
                "> Sell generic alt accounts."
            ),
            inline=False
        )
        
        if banner_url:
            embed.set_image(url=banner_url)
        
        embed.set_footer(text="Hypixel Account Shop • Secure & Fast", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        await interaction.response.send_message(embed=embed, view=TicketPanel())
    
    @app_commands.command(name="mfa_panel", description="Send the MFA panel")
    async def mfa_panel(self, interaction: discord.Interaction):
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        banner_url = cfg.get("images", {}).get("mfa_banner")
        
        # Get prices with fallback to defaults
        mfa_prices = cfg.get("mfa_prices", {})
        if not isinstance(mfa_prices, dict):
            mfa_prices = {}
        
        buy_prices = mfa_prices.get("buy", {})
        sell_prices = mfa_prices.get("sell", {})
        
        # Fallback to defaults if empty
        if not buy_prices:
            app_cfg = storage.load_app_config()
            defaults = app_cfg.get("defaults", {}).get("mfa_prices", {})
            buy_prices = defaults.get("buy", {"NON": 7.0, "VIP": 8.0, "VIP+": 9.5, "MVP": 11.0, "MVP+": 17.0})
        
        if not sell_prices:
            app_cfg = storage.load_app_config()
            defaults = app_cfg.get("defaults", {}).get("mfa_prices", {})
            sell_prices = defaults.get("sell", {"NON": 6.0, "VIP": 7.0, "VIP+": 8.5, "MVP": 10.0, "MVP+": 15.0})
        
        embed = discord.Embed(
            title="🔐  **MFA Market**",
            description="Buy or Sell Hypixel MFAs (Mail Full Access) instantly.",
            color=0x2b2d31,
            timestamp=datetime.utcnow()
        )
        
        # Helper to format prices
        def format_rank_price(prices, rank):
            price = prices.get(rank, 0.0)
            return f"${price:.2f}"

        ranks = ["NON", "VIP", "VIP+", "MVP", "MVP+"]
        
        # Build price table using inline fields for better mobile support
        rank_col = []
        buy_col = []
        sell_col = []
        
        for rank in ranks:
            buy = format_rank_price(buy_prices, rank)
            sell = format_rank_price(sell_prices, rank)
            
            rank_col.append(f"**{rank}**")
            buy_col.append(buy)
            sell_col.append(sell)

        embed.add_field(name="Rank", value="\n".join(rank_col), inline=True)
        embed.add_field(name="Buy Price", value="\n".join(buy_col), inline=True)
        embed.add_field(name="Sell Price", value="\n".join(sell_col), inline=True)
        
        if banner_url:
            embed.set_image(url=banner_url)
        
        embed.set_footer(text="Hypixel Account Shop • Best Rates", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        await interaction.response.send_message(embed=embed, view=MFAPanel())
    
    @app_commands.command(name="coin_panel", description="Send the coin trading panel")
    async def coin_panel(self, interaction: discord.Interaction):
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        banner_url = cfg.get("images", {}).get("coin_banner")
        buy_price = cfg.get("coins", {}).get("buy_base_price", 0.0375)
        sell_price = cfg.get("coins", {}).get("sell_base_price", 0.015)
        
        embed = discord.Embed(
            title="🪙  **Skyblock Coins**",
            description="Safest place to Buy & Sell Skyblock Coins.",
            color=0x2b2d31,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📉  **Buy Coins**",
            value=f"```diff\n+ Price: ${buy_price:.4f}/mil\n```",
            inline=True
        )
        
        embed.add_field(
            name="📈  **Sell Coins**",
            value=f"```diff\n- Price: ${sell_price:.4f}/mil\n```",
            inline=True
        )
        
        embed.add_field(name="\u200b", value="\u200b", inline=True) # Spacer for mobile
        
        if banner_url:
            embed.set_image(url=banner_url)
        
        embed.set_footer(text="Hypixel Account Shop • Instant Delivery", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        await interaction.response.send_message(embed=embed, view=CoinPanel())
    
    @app_commands.command(name="acbuy_panel", description="Send the account buy panel")
    async def acbuy_panel(self, interaction: discord.Interaction):
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        embed = discord.Embed(
            title="🛒  **Buy Accounts**",
            description="Looking for a specific account? Click below to start a purchase request.",
            color=0x2ecc71,
            timestamp=datetime.utcnow()
        )
        
        embed.set_footer(text="Hypixel Account Shop", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        await interaction.response.send_message(embed=embed, view=AccountBuyPanel())

async def setup(bot):
    await bot.add_cog(Panels(bot))
