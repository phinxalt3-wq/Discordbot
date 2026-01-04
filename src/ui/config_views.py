import discord
from src import storage
from src.utils.helpers import format_price
from src.utils.logging import BotLogger
from typing import Optional

class ConfigMainView(discord.ui.View):
    """Main configuration menu with buttons"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📋 Channels", style=discord.ButtonStyle.primary, row=0)
    async def channels_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🔧 **Channel Configuration**\n\nClick the buttons below to configure channels:",
            view=ChannelConfigView(),
            ephemeral=True
        )
    
    @discord.ui.button(label="📁 Ticket Categories", style=discord.ButtonStyle.primary, row=0)
    async def categories_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "📁 **Ticket Category Configuration**\n\nClick the buttons below to set categories for ticket types:",
            view=TicketCategoryConfigView(),
            ephemeral=True
        )
    
    @discord.ui.button(label="💰 Pricing", style=discord.ButtonStyle.primary, row=0)
    async def pricing_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "💰 **Pricing Configuration**\n\nClick the buttons below to configure prices:",
            view=PricingConfigView(),
            ephemeral=True
        )
    
    @discord.ui.button(label="💳 Payment Methods", style=discord.ButtonStyle.primary, row=0)
    async def payment_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PaymentMethodsModal())
    
    @discord.ui.button(label="🖼️ Banners", style=discord.ButtonStyle.primary, row=1)
    async def banner_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🖼️ **Banner Configuration**\n\nClick the buttons below to set banner images:",
            view=BannerConfigView(),
            ephemeral=True
        )
    
    @discord.ui.button(label="👥 Roles & Owners", style=discord.ButtonStyle.primary, row=1)
    async def roles_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "👥 **Roles & Owners Configuration**\n\nClick the buttons below:",
            view=RolesConfigView(),
            ephemeral=True
        )
    
    @discord.ui.button(label="📊 View Config", style=discord.ButtonStyle.success, row=1)
    async def view_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        cfg = storage.get_config(interaction.guild_id)
        
        embed = discord.Embed(title="🔧 Bot Configuration", color=0x3498db)
        
        # Channels
        ticket_ch = f"<#{cfg['channels']['tickets']}>" if cfg['channels']['tickets'] else "Not set"
        vouch_ch = f"<#{cfg['channels']['vouches']}>" if cfg['channels']['vouches'] else "Not set"
        log_ch = f"<#{cfg['channels']['logs']}>" if cfg['channels'].get('logs') else "Not set"
        embed.add_field(name="Channels", value=f"Tickets: {ticket_ch}\nVouches: {vouch_ch}\nLogs: {log_ch}", inline=False)
        
        # Staff Role
        staff = f"<@&{cfg['staff_role']}>" if cfg['staff_role'] else "Not set"
        embed.add_field(name="Staff Role", value=staff, inline=False)
        
        # Owners
        owners_list = [f"<@{oid}>" for oid in cfg.get('owners', [])]
        owners_str = ", ".join(owners_list) if owners_list else "None"
        embed.add_field(name="Owners", value=owners_str, inline=False)
        
        # MFA Prices
        mfa_prices = "\n".join([f"[{rank}]: ${price:.2f}" for rank, price in cfg['mfa_prices'].items()])
        embed.add_field(name="MFA Prices", value=mfa_prices, inline=True)
        
        # Coin Prices
        coin_prices = f"Buy: ${cfg['coins']['buy_base_price']:.4f}/mil\nSell: ${cfg['coins']['sell_base_price']:.4f}/mil"
        embed.add_field(name="Coin Prices", value=coin_prices, inline=True)
        
        # Payment Methods
        payments = ", ".join(cfg['payments'])
        embed.add_field(name="Payment Methods", value=payments, inline=False)
        
        # Banners
        banners = []
        if cfg.get('images', {}).get('ticket_banner'):
            banners.append("✅ Ticket")
        else:
            banners.append("❌ Ticket")
        if cfg.get('images', {}).get('mfa_banner'):
            banners.append("✅ MFA")
        else:
            banners.append("❌ MFA")
        if cfg.get('images', {}).get('coin_banner'):
            banners.append("✅ Coin")
        else:
            banners.append("❌ Coin")
        embed.add_field(name="Banners", value=" | ".join(banners), inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ChannelConfigView(discord.ui.View):
    """Channel configuration view"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Set Tickets Channel", style=discord.ButtonStyle.primary, row=0)
    async def set_tickets(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChannelSelectModal("tickets", "Tickets"))
    
    @discord.ui.button(label="Set Vouches Channel", style=discord.ButtonStyle.primary, row=0)
    async def set_vouches(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChannelSelectModal("vouches", "Vouches"))
    
    @discord.ui.button(label="Set Logs Channel", style=discord.ButtonStyle.primary, row=1)
    async def set_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChannelSelectModal("logs", "Logs"))
    
    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.secondary, row=2)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔧 Bot Configuration Menu",
            description="Click the buttons below to configure different aspects of the bot.",
            color=0x3498db
        )
        embed.add_field(
            name="Available Options",
            value="📋 Channels | 📁 Ticket Categories | 💰 Pricing\n💳 Payment Methods | 🖼️ Banners | 👥 Roles & Owners | 📊 View Config",
            inline=False
        )
        await interaction.response.edit_message(embed=embed, view=ConfigMainView())


class ChannelSelectModal(discord.ui.Modal):
    """Modal for selecting a channel"""
    def __init__(self, channel_type: str, display_name: str):
        super().__init__(title=f"Set {display_name} Channel")
        self.channel_type = channel_type
        self.display_name = display_name
    
    channel_id = discord.ui.TextInput(
        label="Channel ID or Mention",
        placeholder="Paste channel ID or mention the channel",
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Try to extract channel ID from mention or use as-is
        channel_input = self.channel_id.value.strip()
        channel_id = None
        
        # Check if it's a mention
        if channel_input.startswith("<#") and channel_input.endswith(">"):
            channel_id = int(channel_input[2:-1])
        else:
            # Try to parse as ID
            try:
                channel_id = int(channel_input)
            except ValueError:
                return await interaction.followup.send("❌ Invalid channel format! Please provide a channel ID or mention.", ephemeral=True)
        
        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            return await interaction.followup.send("❌ Channel not found! Please check the channel ID.", ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        old_value = cfg["channels"].get(self.channel_type)
        cfg["channels"][self.channel_type] = channel.id
        storage.set_config(interaction.guild_id, cfg)
        
        # Log configuration change (but don't log to logs channel if it's being set)
        if self.channel_type == "logs" and channel.id != old_value:
            print(f"Logs channel set to: {channel.name} (ID: {channel.id})")
        else:
            await BotLogger.log_config_change(
                interaction.guild,
                interaction.user,
                f"{self.display_name} Channel",
                str(old_value) if old_value else "None",
                str(channel.id)
            )
        
        await interaction.followup.send(f"✅ {self.display_name} channel set to {channel.mention}", ephemeral=True)


class TicketCategoryConfigView(discord.ui.View):
    """View for selecting a ticket category to configure"""
    def __init__(self):
        super().__init__(timeout=None)
        
        # Add select menu for categories
        self.add_item(TicketCategorySelect())

    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.secondary, row=1)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔧 Bot Configuration Menu",
            description="Click the buttons below to configure different aspects of the bot.",
            color=0x3498db
        )
        embed.add_field(
            name="Available Options",
            value="📋 Channels | 📁 Ticket Categories | 💰 Pricing\n💳 Payment Methods | 🖼️ Banners | 👥 Roles & Owners | 📊 View Config",
            inline=False
        )
        await interaction.response.edit_message(embed=embed, view=ConfigMainView())


class TicketCategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Sell Account", value="sell_account", emoji="🎫", description="Configure Sell Account tickets"),
            discord.SelectOption(label="Sell Profile", value="sell_profile", emoji="📋", description="Configure Sell Profile tickets"),
            discord.SelectOption(label="Sell Alt", value="sell_alt", emoji="🔑", description="Configure Sell Alt tickets"),
            discord.SelectOption(label="Sell MFA", value="sell_mfa", emoji="🔐", description="Configure Sell MFA tickets"),
            discord.SelectOption(label="Buy Coins", value="buy_coins", emoji="💰", description="Configure Buy Coins tickets"),
            discord.SelectOption(label="Sell Coins", value="sell_coins", emoji="💵", description="Configure Sell Coins tickets"),
            discord.SelectOption(label="Buy Account", value="buy_account", emoji="🛒", description="Configure Buy Account tickets"),
            discord.SelectOption(label="Buy MFA", value="buy_mfa", emoji="🔐", description="Configure Buy MFA tickets"),
        ]
        super().__init__(placeholder="Select a category to configure...", min_values=1, max_values=1, options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        category_key = self.values[0]
        cfg = storage.get_config(interaction.guild_id)
        category_data = cfg["ticket_categories"].get(category_key, {})
        
        embed = discord.Embed(
            title=f"🔧 Configure: {category_data.get('name', category_key.replace('_', ' ').title())}",
            description=f"Current Settings for **{category_key}**",
            color=category_data.get('color', 0x3498db)
        )
        
        status = "✅ Enabled" if category_data.get('enabled', True) else "❌ Disabled"
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Name", value=category_data.get('name', 'N/A'), inline=True)
        embed.add_field(name="Emoji", value=category_data.get('emoji', '❓'), inline=True)
        embed.add_field(name="Description", value=category_data.get('description', 'N/A'), inline=False)
        
        await interaction.response.edit_message(embed=embed, view=CategoryEditView(category_key))


class CategoryEditView(discord.ui.View):
    def __init__(self, category_key):
        super().__init__(timeout=None)
        self.category_key = category_key

    @discord.ui.button(label="Toggle Status", style=discord.ButtonStyle.primary, row=0)
    async def toggle_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        cfg = storage.get_config(interaction.guild_id)
        current_status = cfg["ticket_categories"][self.category_key].get("enabled", True)
        new_status = not current_status
        cfg["ticket_categories"][self.category_key]["enabled"] = new_status
        storage.set_config(interaction.guild_id, cfg)
        
        status_str = "Enabled" if new_status else "Disabled"
        
        # Log change
        await BotLogger.log_config_change(
            interaction.guild,
            interaction.user,
            f"Ticket Category: {self.category_key} Status",
            "Enabled" if current_status else "Disabled",
            status_str
        )
        
        await interaction.response.send_message(f"✅ Category **{self.category_key}** is now **{status_str}**.", ephemeral=True)
        
        # Refresh the view
        await self.refresh_embed(interaction)

    @discord.ui.button(label="Edit Details", style=discord.ButtonStyle.secondary, row=0)
    async def edit_details(self, interaction: discord.Interaction, button: discord.ui.Button):
        cfg = storage.get_config(interaction.guild_id)
        data = cfg["ticket_categories"].get(self.category_key, {})
        await interaction.response.send_modal(CategoryEditModal(self.category_key, data))

    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.secondary, row=1)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="📁 **Ticket Category Configuration**\n\nClick the buttons below to set categories for ticket types:",
            embed=None,
            view=TicketCategoryConfigView()
        )

    async def refresh_embed(self, interaction: discord.Interaction):
        cfg = storage.get_config(interaction.guild_id)
        category_data = cfg["ticket_categories"].get(self.category_key, {})
        
        embed = discord.Embed(
            title=f"🔧 Configure: {category_data.get('name', self.category_key.replace('_', ' ').title())}",
            description=f"Current Settings for **{self.category_key}**",
            color=category_data.get('color', 0x3498db)
        )
        
        status = "✅ Enabled" if category_data.get('enabled', True) else "❌ Disabled"
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Name", value=category_data.get('name', 'N/A'), inline=True)
        embed.add_field(name="Emoji", value=category_data.get('emoji', '❓'), inline=True)
        embed.add_field(name="Description", value=category_data.get('description', 'N/A'), inline=False)
        
        if interaction.response.is_done():
             await interaction.message.edit(embed=embed, view=self)
        else:
             await interaction.response.edit_message(embed=embed, view=self)


class CategoryEditModal(discord.ui.Modal):
    def __init__(self, category_key, current_data):
        super().__init__(title=f"Edit {current_data.get('name', category_key)}")
        self.category_key = category_key
        
        self.name_input = discord.ui.TextInput(
            label="Name",
            default=current_data.get("name", ""),
            required=True,
            max_length=50
        )
        self.add_item(self.name_input)
        
        self.emoji_input = discord.ui.TextInput(
            label="Emoji",
            default=current_data.get("emoji", ""),
            required=True,
            max_length=50
        )
        self.add_item(self.emoji_input)
        
        self.desc_input = discord.ui.TextInput(
            label="Description",
            default=current_data.get("description", ""),
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=100
        )
        self.add_item(self.desc_input)

    async def on_submit(self, interaction: discord.Interaction):
        cfg = storage.get_config(interaction.guild_id)
        old_data = cfg["ticket_categories"].get(self.category_key, {}).copy()
        
        cfg["ticket_categories"][self.category_key]["name"] = self.name_input.value
        cfg["ticket_categories"][self.category_key]["emoji"] = self.emoji_input.value
        cfg["ticket_categories"][self.category_key]["description"] = self.desc_input.value
        
        storage.set_config(interaction.guild_id, cfg)
        
        # Log change
        await BotLogger.log_config_change(
            interaction.guild,
            interaction.user,
            f"Ticket Category: {self.category_key} Details",
            f"Name: {old_data.get('name')}, Emoji: {old_data.get('emoji')}",
            f"Name: {self.name_input.value}, Emoji: {self.emoji_input.value}"
        )
        
        await interaction.response.send_message("✅ Category details updated!", ephemeral=True)


class PricingConfigView(discord.ui.View):
    """Pricing configuration view"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Configure MFA Buy Prices", style=discord.ButtonStyle.primary, row=0)
    async def mfa_buy_prices(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MFABuyPricesModal())
    
    @discord.ui.button(label="Configure MFA Sell Prices", style=discord.ButtonStyle.primary, row=0)
    async def mfa_sell_prices(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MFASellPricesModal())
    
    @discord.ui.button(label="Configure Coin Prices", style=discord.ButtonStyle.primary, row=0)
    async def coin_prices(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CoinPricesModal())
    
    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.secondary, row=1)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔧 Bot Configuration Menu",
            description="Click the buttons below to configure different aspects of the bot.",
            color=0x3498db
        )
        embed.add_field(
            name="Available Options",
            value="📋 Channels | 📁 Ticket Categories | 💰 Pricing\n💳 Payment Methods | 🖼️ Banners | 👥 Roles & Owners | 📊 View Config",
            inline=False
        )
        await interaction.response.edit_message(embed=embed, view=ConfigMainView())


class MFABuyPricesModal(discord.ui.Modal, title="Configure MFA Buy Prices"):
    non = discord.ui.TextInput(
        label="NON Buy Price",
        placeholder="e.g. 7.0",
        required=False,
        max_length=10
    )
    vip = discord.ui.TextInput(
        label="VIP Buy Price",
        placeholder="e.g. 8.0",
        required=False,
        max_length=10
    )
    vip_plus = discord.ui.TextInput(
        label="VIP+ Buy Price",
        placeholder="e.g. 9.5",
        required=False,
        max_length=10
    )
    mvp = discord.ui.TextInput(
        label="MVP Buy Price",
        placeholder="e.g. 11.0",
        required=False,
        max_length=10
    )
    mvp_plus = discord.ui.TextInput(
        label="MVP+ Buy Price",
        placeholder="e.g. 17.0",
        required=False,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        if "mfa_prices" not in cfg or not isinstance(cfg["mfa_prices"], dict):
            cfg["mfa_prices"] = {"buy": {}, "sell": {}}
        if "buy" not in cfg["mfa_prices"]:
            cfg["mfa_prices"]["buy"] = {}
        
        old_prices = cfg["mfa_prices"].get("buy", {}).copy()
        
        if self.non.value:
            try:
                cfg["mfa_prices"]["buy"]["NON"] = float(self.non.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid price for NON! Please enter a valid number.", ephemeral=True)
        
        if self.vip.value:
            try:
                cfg["mfa_prices"]["buy"]["VIP"] = float(self.vip.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid price for VIP! Please enter a valid number.", ephemeral=True)
        
        if self.vip_plus.value:
            try:
                cfg["mfa_prices"]["buy"]["VIP+"] = float(self.vip_plus.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid price for VIP+! Please enter a valid number.", ephemeral=True)
        
        if self.mvp.value:
            try:
                cfg["mfa_prices"]["buy"]["MVP"] = float(self.mvp.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid price for MVP! Please enter a valid number.", ephemeral=True)
        
        if self.mvp_plus.value:
            try:
                cfg["mfa_prices"]["buy"]["MVP+"] = float(self.mvp_plus.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid price for MVP+! Please enter a valid number.", ephemeral=True)
        
        storage.set_config(interaction.guild_id, cfg)
        
        # Log configuration change
        await BotLogger.log_config_change(
            interaction.guild,
            interaction.user,
            "MFA Buy Prices",
            str(old_prices),
            str(cfg["mfa_prices"]["buy"])
        )
        
        price_list = "\n".join([f"• [{rank}]: ${price:.2f}" for rank, price in cfg["mfa_prices"]["buy"].items()])
        await interaction.followup.send(f"✅ MFA buy prices updated:\n{price_list}", ephemeral=True)


class MFASellPricesModal(discord.ui.Modal, title="Configure MFA Sell Prices"):
    non = discord.ui.TextInput(
        label="NON Sell Price",
        placeholder="e.g. 6.0",
        required=False,
        max_length=10
    )
    vip = discord.ui.TextInput(
        label="VIP Sell Price",
        placeholder="e.g. 7.0",
        required=False,
        max_length=10
    )
    vip_plus = discord.ui.TextInput(
        label="VIP+ Sell Price",
        placeholder="e.g. 8.5",
        required=False,
        max_length=10
    )
    mvp = discord.ui.TextInput(
        label="MVP Sell Price",
        placeholder="e.g. 10.0",
        required=False,
        max_length=10
    )
    mvp_plus = discord.ui.TextInput(
        label="MVP+ Sell Price",
        placeholder="e.g. 15.0",
        required=False,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        if "mfa_prices" not in cfg or not isinstance(cfg["mfa_prices"], dict):
            cfg["mfa_prices"] = {"buy": {}, "sell": {}}
        if "sell" not in cfg["mfa_prices"]:
            cfg["mfa_prices"]["sell"] = {}
        
        old_prices = cfg["mfa_prices"].get("sell", {}).copy()
        
        if self.non.value:
            try:
                cfg["mfa_prices"]["sell"]["NON"] = float(self.non.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid price for NON! Please enter a valid number.", ephemeral=True)
        
        if self.vip.value:
            try:
                cfg["mfa_prices"]["sell"]["VIP"] = float(self.vip.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid price for VIP! Please enter a valid number.", ephemeral=True)
        
        if self.vip_plus.value:
            try:
                cfg["mfa_prices"]["sell"]["VIP+"] = float(self.vip_plus.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid price for VIP+! Please enter a valid number.", ephemeral=True)
        
        if self.mvp.value:
            try:
                cfg["mfa_prices"]["sell"]["MVP"] = float(self.mvp.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid price for MVP! Please enter a valid number.", ephemeral=True)
        
        if self.mvp_plus.value:
            try:
                cfg["mfa_prices"]["sell"]["MVP+"] = float(self.mvp_plus.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid price for MVP+! Please enter a valid number.", ephemeral=True)
        
        storage.set_config(interaction.guild_id, cfg)
        
        # Log configuration change
        await BotLogger.log_config_change(
            interaction.guild,
            interaction.user,
            "MFA Sell Prices",
            str(old_prices),
            str(cfg["mfa_prices"]["sell"])
        )
        
        price_list = "\n".join([f"• [{rank}]: ${price:.2f}" for rank, price in cfg["mfa_prices"]["sell"].items()])
        await interaction.followup.send(f"✅ MFA sell prices updated:\n{price_list}", ephemeral=True)


class CoinPricesModal(discord.ui.Modal, title="Configure Coin Prices"):
    buy_price = discord.ui.TextInput(
        label="Buy Price (per million)",
        placeholder="e.g. 0.0375",
        required=False,
        max_length=20
    )
    sell_price = discord.ui.TextInput(
        label="Sell Price (per million)",
        placeholder="e.g. 0.015",
        required=False,
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        old_buy = cfg["coins"]["buy_base_price"]
        old_sell = cfg["coins"]["sell_base_price"]
        
        if self.buy_price.value:
            try:
                cfg["coins"]["buy_base_price"] = float(self.buy_price.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid buy price! Please enter a valid number.", ephemeral=True)
        
        if self.sell_price.value:
            try:
                cfg["coins"]["sell_base_price"] = float(self.sell_price.value)
            except ValueError:
                return await interaction.followup.send("❌ Invalid sell price! Please enter a valid number.", ephemeral=True)
        
        storage.set_config(interaction.guild_id, cfg)
        
        # Log configuration change
        await BotLogger.log_config_change(
            interaction.guild,
            interaction.user,
            "Coin Prices",
            f"Buy: {old_buy}, Sell: {old_sell}",
            f"Buy: {cfg['coins']['buy_base_price']}, Sell: {cfg['coins']['sell_base_price']}"
        )
        
        await interaction.followup.send(
            f"✅ Coin prices updated:\n"
            f"• Buy price: ${cfg['coins']['buy_base_price']:.4f}/mil\n"
            f"• Sell price: ${cfg['coins']['sell_base_price']:.4f}/mil",
            ephemeral=True
        )


class PaymentMethodsModal(discord.ui.Modal, title="Configure Payment Methods"):
    methods = discord.ui.TextInput(
        label="Payment Methods (comma-separated)",
        placeholder="e.g. PayPal, Crypto, UPI, Venmo",
        required=True,
        max_length=200
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        payment_list = [m.strip() for m in self.methods.value.split(",")]
        cfg = storage.get_config(interaction.guild_id)
        old_methods = cfg["payments"].copy()
        cfg["payments"] = payment_list
        storage.set_config(interaction.guild_id, cfg)
        
        # Log configuration change
        await BotLogger.log_config_change(
            interaction.guild,
            interaction.user,
            "Payment Methods",
            ", ".join(old_methods),
            ", ".join(payment_list)
        )
        
        methods_str = ", ".join(payment_list)
        await interaction.followup.send(f"✅ Payment methods updated: {methods_str}", ephemeral=True)


class BannerConfigView(discord.ui.View):
    """Banner configuration view"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Set Ticket Banner", style=discord.ButtonStyle.primary, row=0)
    async def ticket_banner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BannerModal("ticket_banner", "Ticket"))
    
    @discord.ui.button(label="Set MFA Banner", style=discord.ButtonStyle.primary, row=0)
    async def mfa_banner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BannerModal("mfa_banner", "MFA"))
    
    @discord.ui.button(label="Set Coin Banner", style=discord.ButtonStyle.primary, row=1)
    async def coin_banner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BannerModal("coin_banner", "Coin"))
    
    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.secondary, row=2)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔧 Bot Configuration Menu",
            description="Click the buttons below to configure different aspects of the bot.",
            color=0x3498db
        )
        embed.add_field(
            name="Available Options",
            value="📋 Channels | 📁 Ticket Categories | 💰 Pricing\n💳 Payment Methods | 🖼️ Banners | 👥 Roles & Owners | 📊 View Config",
            inline=False
        )
        await interaction.response.edit_message(embed=embed, view=ConfigMainView())


class BannerModal(discord.ui.Modal):
    """Modal for setting banner URLs"""
    def __init__(self, banner_type: str, display_name: str):
        super().__init__(title=f"Set {display_name} Banner")
        self.banner_type = banner_type
        self.display_name = display_name
    
    url = discord.ui.TextInput(
        label="Image URL",
        placeholder="https://example.com/image.png",
        required=True,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        storage.set_images(interaction.guild_id, **{self.banner_type: self.url.value})
        
        # Log configuration change
        await BotLogger.log_config_change(
            interaction.guild,
            interaction.user,
            f"{self.display_name} Banner",
            "Not set",
            self.url.value
        )
        
        await interaction.followup.send(f"✅ {self.display_name} banner image updated.", ephemeral=True)


class RolesConfigView(discord.ui.View):
    """Roles and owners configuration view"""
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Set Staff Role", style=discord.ButtonStyle.primary, row=0)
    async def staff_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RoleSelectModal("staff_role", "Staff Role"))
    
    @discord.ui.button(label="Add Owner", style=discord.ButtonStyle.primary, row=0)
    async def add_owner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddOwnerModal())
    
    @discord.ui.button(label="Remove Owner", style=discord.ButtonStyle.danger, row=1)
    async def remove_owner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RemoveOwnerModal())
    
    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.secondary, row=2)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔧 Bot Configuration Menu",
            description="Click the buttons below to configure different aspects of the bot.",
            color=0x3498db
        )
        embed.add_field(
            name="Available Options",
            value="📋 Channels | 📁 Ticket Categories | 💰 Pricing\n💳 Payment Methods | 🖼️ Banners | 👥 Roles & Owners | 📊 View Config",
            inline=False
        )
        await interaction.response.edit_message(embed=embed, view=ConfigMainView())


class RoleSelectModal(discord.ui.Modal):
    """Modal for selecting a role"""
    def __init__(self, role_type: str, display_name: str):
        super().__init__(title=f"Set {display_name}")
        self.role_type = role_type
        self.display_name = display_name
    
    role_id = discord.ui.TextInput(
        label="Role ID or Mention",
        placeholder="Paste role ID or mention the role",
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Try to extract role ID from mention or use as-is
        role_input = self.role_id.value.strip()
        role_id = None
        
        # Check if it's a mention
        if role_input.startswith("<@&") and role_input.endswith(">"):
            role_id = int(role_input[3:-1])
        else:
            # Try to parse as ID
            try:
                role_id = int(role_input)
            except ValueError:
                return await interaction.followup.send("❌ Invalid role format! Please provide a role ID or mention.", ephemeral=True)
        
        role = interaction.guild.get_role(role_id)
        if not role:
            return await interaction.followup.send("❌ Role not found! Please check the role ID.", ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        old_role = cfg.get("staff_role")
        storage.set_staff_role(interaction.guild_id, role.id)
        
        # Log configuration change
        await BotLogger.log_config_change(
            interaction.guild,
            interaction.user,
            "Staff Role",
            str(old_role) if old_role else "None",
            str(role.id)
        )
        
        await interaction.followup.send(f"✅ Staff role set to {role.mention}", ephemeral=True)


class AddOwnerModal(discord.ui.Modal, title="Add Owner"):
    user_id = discord.ui.TextInput(
        label="User ID or Mention",
        placeholder="Paste user ID or mention the user",
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Try to extract user ID from mention or use as-is
        user_input = self.user_id.value.strip()
        user_id = None
        
        # Check if it's a mention
        if user_input.startswith("<@") and user_input.endswith(">"):
            user_id = int(user_input[2:-1])
        else:
            # Try to parse as ID
            try:
                user_id = int(user_input)
            except ValueError:
                return await interaction.followup.send("❌ Invalid user format! Please provide a user ID or mention.", ephemeral=True)
        
        user = interaction.guild.get_member(user_id) or interaction.client.get_user(user_id)
        if not user:
            return await interaction.followup.send("❌ User not found! Please check the user ID.", ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        old_owners = cfg.get("owners", []).copy()
        storage.add_owner(interaction.guild_id, user.id)
        cfg = storage.get_config(interaction.guild_id)  # Refresh to get updated owners
        
        # Log configuration change
        await BotLogger.log_config_change(
            interaction.guild,
            interaction.user,
            "Owners",
            str(old_owners),
            str(cfg.get("owners", []))
        )
        
        await interaction.followup.send(f"✅ {user.mention} has been added as an owner.", ephemeral=True)


class RemoveOwnerModal(discord.ui.Modal, title="Remove Owner"):
    user_id = discord.ui.TextInput(
        label="User ID or Mention",
        placeholder="Paste user ID or mention the user",
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Try to extract user ID from mention or use as-is
        user_input = self.user_id.value.strip()
        user_id = None
        
        # Check if it's a mention
        if user_input.startswith("<@") and user_input.endswith(">"):
            user_id = int(user_input[2:-1])
        else:
            # Try to parse as ID
            try:
                user_id = int(user_input)
            except ValueError:
                return await interaction.followup.send("❌ Invalid user format! Please provide a user ID or mention.", ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        owners = cfg.get("owners", [])
        
        if user_id not in owners:
            return await interaction.followup.send("❌ This user is not an owner.", ephemeral=True)
        
        owners.remove(user_id)
        cfg["owners"] = owners
        storage.set_config(interaction.guild_id, cfg)
        
        user = interaction.guild.get_member(user_id) or interaction.client.get_user(user_id)
        user_mention = user.mention if user else f"<@{user_id}>"
        
        # Log configuration change
        await BotLogger.log_config_change(
            interaction.guild,
            interaction.user,
            "Owners",
            str(cfg.get("owners", []) + [user_id]),
            str(cfg.get("owners", []))
        )
        
        await interaction.followup.send(f"✅ {user_mention} has been removed as an owner.", ephemeral=True)
