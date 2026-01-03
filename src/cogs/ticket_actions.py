import discord
from discord.ext import commands
from src.ui import (
    SellAccountModal, SellMFAModal,
    BuyCoinsModal, SellCoinsModal
)
from src.tickets import TicketManager, has_staff_privs

class TicketActions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type != discord.InteractionType.component:
            return

        cid = interaction.data.get("custom_id")

        if cid in ("sell_account", "sell_profile", "sell_alt"):
            await interaction.response.send_modal(SellAccountModal(cid))

        elif cid == "sell_mfa":
            await interaction.response.send_modal(SellMFAModal())

        elif cid == "buy_coins":
            await interaction.response.send_modal(BuyCoinsModal())

        elif cid == "sell_coins":
            await interaction.response.send_modal(SellCoinsModal())

        elif cid == "close_ticket":
            if not has_staff_privs(interaction):
                return await interaction.response.send_message("Unauthorized", ephemeral=True)

            await TicketManager.close(interaction)
            await interaction.response.send_message("Ticket closed", ephemeral=True)


async def setup(bot):
    await bot.add_cog(TicketActions(bot))
