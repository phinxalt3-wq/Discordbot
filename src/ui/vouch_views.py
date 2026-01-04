import discord
from src.ui.vouch_modal import VouchModal

class VouchButtonView(discord.ui.View):
    """View with button to submit a vouch"""
    def __init__(self, seller_id: int = None):
        super().__init__(timeout=None)
        self.seller_id = seller_id
    
    @discord.ui.button(label="Submit Vouch", style=discord.ButtonStyle.success, custom_id="vouch:submit")
    async def submit_vouch(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open vouch modal when button is clicked"""
        seller_id = self.seller_id
        
        # If no seller_id (after restart), try to get from embed
        if not seller_id:
            if interaction.message and interaction.message.embeds:
                embed = interaction.message.embeds[0]
                # Try to get from Transaction Details field
                for field in embed.fields:
                    if field.name == "Transaction Details":
                        # Value is like "**Seller:** <@123>\n**Buyer:** <@456>"
                        # We can look for the first mention
                        if field.value:
                             # Simple parse for mention <@123> or <@!123>
                            import re
                            match = re.search(r"<@!?(\d+)>", field.value)
                            if match:
                                seller_id = int(match.group(1))
                                break
        
        if not seller_id:
            return await interaction.response.send_message("❌ Could not determine seller from message.", ephemeral=True)

        # Get seller from ID
        seller = interaction.guild.get_member(seller_id) or interaction.client.get_user(seller_id)
        if not seller:
            try:
                seller = await interaction.client.fetch_user(seller_id)
            except:
                pass
        
        if not seller:
            return await interaction.response.send_message("❌ Seller not found.", ephemeral=True)
        
        # Open the vouch modal
        await interaction.response.send_modal(VouchModal(seller))

