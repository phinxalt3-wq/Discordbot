import discord
from discord.ext import commands
from discord import app_commands
from src import storage
from src.utils.permissions import is_owner
from src.ui.config_views import ConfigMainView
from src.utils.logging import BotLogger
from typing import Optional

class Owner(commands.Cog):
    """Owner configuration commands"""
    def __init__(self, bot):
        self.bot = bot
    
    config_group = app_commands.Group(name="bot", description="Bot configuration commands (Owner only)")
    
    @config_group.command(name="config", description="Open interactive configuration menu")
    async def config_menu(self, interaction: discord.Interaction):
        """Open the interactive configuration menu with buttons"""
        # Defer immediately to prevent timeout
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        
        # Check permissions after deferring
        if not is_owner(interaction):
            await interaction.followup.send("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔧 Bot Configuration Menu",
            description="Click the buttons below to configure different aspects of the bot.\n\n**All configuration is done through this menu.**",
            color=0x3498db
        )
        embed.add_field(
            name="Available Options",
            value="📋 Channels | 📁 Ticket Categories | 💰 Pricing\n💳 Payment Methods | 🖼️ Banners | 👥 Roles & Owners | 📊 View Config",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, view=ConfigMainView(), ephemeral=True)
    
    @config_group.command(name="invite", description="Generate bot invite link")
    @app_commands.describe(admin="Include administrator permissions (default: false)")
    async def invite(self, interaction: discord.Interaction, admin: bool = False):
        """Generate a bot invite link"""
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Get bot client ID
        app_cfg = storage.load_app_config()
        client_id = app_cfg.get("client_id")
        
        if not client_id:
            return await interaction.followup.send(
                "❌ Bot client ID not configured. Please set it in config.json",
                ephemeral=True
            )
        
        # Build permissions
        permissions = discord.Permissions()
        permissions.update(
            manage_channels=True,
            manage_messages=True,
            send_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            use_external_emojis=True,
            add_reactions=True,
            manage_webhooks=True,
            view_channel=True,
            read_messages=True
        )
        
        if admin:
            permissions.update(administrator=True)
        
        # Generate invite URL
        invite_url = discord.utils.oauth_url(
            client_id=client_id,
            permissions=permissions,
            scopes=["bot", "applications.commands"]
        )
        
        embed = discord.Embed(
            title="🤖 Bot Invite Link",
            description=f"Use this link to invite the bot to your server:",
            color=0x5865f2,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name="Invite Link",
            value=f"[Click here to invite]({invite_url})",
            inline=False
        )
        embed.add_field(
            name="Permissions",
            value="Administrator" if admin else "Standard Bot Permissions",
            inline=True
        )
        embed.set_footer(text="Keep this link private!")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Owner(bot))
