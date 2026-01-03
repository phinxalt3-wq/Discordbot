import discord
from src.ui.modals import (
    SellAccountModal, SellProfileModal, SellAltModal,
    SellMFAModal, BuyMFAModal, BuyCoinsModal, SellCoinsModal,
    BuyAccountModal
)
from src import storage
from src.utils.helpers import format_price


class TicketPanel(discord.ui.View):
    """Main ticket panel with all account/profile/alt selling options"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Sell an Account", style=discord.ButtonStyle.danger, custom_id="ticket:sell_account")
    async def sell_account(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SellAccountModal())

    @discord.ui.button(label="Sell a Profile", style=discord.ButtonStyle.danger, custom_id="ticket:sell_profile")
    async def sell_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SellProfileModal())

    @discord.ui.button(label="Sell an Alt", style=discord.ButtonStyle.danger, custom_id="ticket:sell_alt")
    async def sell_alt(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SellAltModal())


class MFAPanel(discord.ui.View):
    """MFA panel with buy and sell buttons"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Buy MFA", style=discord.ButtonStyle.success, custom_id="mfa:buy", row=0)
    async def buy_mfa(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BuyMFAModal())
    
    @discord.ui.button(label="Sell MFA", style=discord.ButtonStyle.danger, custom_id="mfa:sell", row=0)
    async def sell_mfa(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SellMFAModal())


class CoinPanel(discord.ui.View):
    """Coin trading panel with buy/sell buttons"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buy Coins", style=discord.ButtonStyle.success, custom_id="coins:buy")
    async def buy_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BuyCoinsModal())

    @discord.ui.button(label="Sell Coins", style=discord.ButtonStyle.danger, custom_id="coins:sell")
    async def sell_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SellCoinsModal())


class AccountBuyPanel(discord.ui.View):
    """Account buy panel with button to buy accounts"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Click to Buy", style=discord.ButtonStyle.success, custom_id="account:buy")
    async def buy_account(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BuyAccountModal())
