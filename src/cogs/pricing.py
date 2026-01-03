import discord
from discord.ext import commands
from discord import app_commands
from src import storage

class Pricing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="view_prices")
    async def view_prices(self, interaction):
        cfg = storage.get_config(interaction.guild_id)
        p_buy = cfg["mfa_prices"].get("buy", {})
        p_sell = cfg["mfa_prices"].get("sell", {})

        desc = (
            f"Coins\nBuy ${cfg['coins']['buy_base_price']}/mil\n"
            f"Sell ${cfg['coins']['sell_base_price']}/mil\n\n"
            f"MFA Buy Prices\nNON ${p_buy.get('NON', 0)} | VIP ${p_buy.get('VIP', 0)} | VIP+ ${p_buy.get('VIP+', 0)} | MVP ${p_buy.get('MVP', 0)} | MVP+ ${p_buy.get('MVP+', 0)}\n\n"
            f"MFA Sell Prices\nNON ${p_sell.get('NON', 0)} | VIP ${p_sell.get('VIP', 0)} | VIP+ ${p_sell.get('VIP+', 0)} | MVP ${p_sell.get('MVP', 0)} | MVP+ ${p_sell.get('MVP+', 0)}"
        )

        await interaction.response.send_message(
            embed=discord.Embed(title="Pricing", description=desc),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Pricing(bot))
