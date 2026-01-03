import discord
from src.ui.vouch_modal import VouchModal

class VouchButtonView(discord.ui.View):
    """View with button to submit a vouch"""
    def __init__(self, seller_id: int):
        super().__init__(timeout=None)
        self.seller_id = seller_id
    
    @discord.ui.button(label="Submit Vouch", style=discord.ButtonStyle.success, custom_id="vouch:submit")
    async def submit_vouch(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open vouch modal when button is clicked"""
        # Get seller from stored ID
        seller = interaction.guild.get_member(self.seller_id) or interaction.client.get_user(self.seller_id)
        if not seller:
            return await interaction.response.send_message("❌ Seller not found.", ephemeral=True)
        
        # Open the vouch modal
        await interaction.response.send_modal(VouchModal(seller))

