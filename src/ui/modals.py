import discord
from src import storage
from src.utils.helpers import calculate_coin_price, format_price, get_skycrypt_link, get_skycrypt_link
from src.tickets.utils import create_ticket_channel, save_ticket
from src.ui.ticket_views import OpenedTicketView
from src.utils.logging import BotLogger
from src.utils.rate_limit import rate_limiter

async def check_user_permissions(interaction: discord.Interaction) -> tuple[bool, str | None]:
    """Check if user is blacklisted and rate limited. Returns (allowed, error_message)"""
    # Check blacklist
    if storage.is_blacklisted(interaction.guild_id, interaction.user.id):
        return False, "❌ You are blacklisted from using this bot."
    
    # Rate limiting for ticket creation (3 tickets per 5 minutes)
    allowed, retry_after = rate_limiter.check_rate_limit(
        interaction.user.id,
        "create_ticket",
        max_uses=3,
        time_window=300
    )
    if not allowed:
        return False, f"⏳ You're creating tickets too quickly. Please wait {retry_after:.1f} seconds."
    
    return True, None
    
class SellAccountModal(discord.ui.Modal, title="Sell Account"):
    username = discord.ui.TextInput(
        label="Username",
        placeholder="Enter the account username",
        required=True,
        max_length=100
    )
    price = discord.ui.TextInput(
        label="How much you are looking for",
        placeholder="e.g. 50.00",
        required=True,
        max_length=20
    )
    payment = discord.ui.TextInput(
        label="Payment Method",
        placeholder="Crypto only (e.g. Bitcoin, Ethereum, USDT)",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            price_value = float(self.price.value)
            if price_value <= 0:
                return await interaction.response.send_message("❌ Price must be greater than 0!", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid price format! Please enter a valid number (e.g. 50.00)", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Create ticket channel
        channel_name = f"sell-{self.username.value.lower().replace(' ', '-')}"
        try:
            ticket_channel = await create_ticket_channel(
                interaction.guild,
                "sell_account",
                channel_name,
                interaction.user
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error creating sell_account channel: {error_details}")
            return await interaction.followup.send(f"❌ Error creating ticket channel: {str(e)}\n\nPlease check bot permissions and ensure the bot can create channels.", ephemeral=True)
        
        # Create embed
        embed = discord.Embed(
            title="Account Sale",
            description="Thank you for your interest in selling an account. Please wait for a buyer to get to you.",
            color=0xe74c3c,
            timestamp=interaction.created_at
        )
        embed.add_field(name="Username", value=self.username.value, inline=True)
        embed.add_field(name="Price", value=format_price(price_value), inline=True)
        embed.add_field(name="Payment Method", value=self.payment.value, inline=True)
        embed.add_field(name="Skyblock Stats", value=f"[View on SkyCrypt]({get_skycrypt_link(self.username.value)})", inline=False)
        embed.add_field(name="Seller", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        
        # Save ticket data
        ticket_data = {
            "opened_by": interaction.user.id,
            "channel_id": ticket_channel.id,
            "ticket_type": "sell_account",
            "is_open": True,
            "username": self.username.value,
            "price": price_value,
            "payment_method": self.payment.value
        }
        save_ticket(interaction.guild_id, ticket_data)
        
        # Send initial message with view
        cfg = storage.get_config(interaction.guild_id)
        staff_role_id = cfg.get("staff_role")
        ping_content = ""
        if staff_role_id:
            ping_content = f"<@&{staff_role_id}>"
        
        initial_message = await ticket_channel.send(
            content=f"{ping_content} {interaction.user.mention}" if ping_content else interaction.user.mention,
            embed=embed,
            view=OpenedTicketView()
        )
        await initial_message.pin()
        
        # Log ticket creation
        await BotLogger.log_ticket_created(interaction.guild, ticket_channel, interaction.user, "sell_account", ticket_data)
        
        await interaction.followup.send(f"✅ Your ticket has been created! Go to {ticket_channel.mention}", ephemeral=True)


class BuyAccountModal(discord.ui.Modal, title="Buy Account"):
    ign = discord.ui.TextInput(
        label="IGN (In-Game Name)",
        placeholder="Enter the account IGN you want to buy",
        required=True,
        max_length=100
    )
    payment = discord.ui.TextInput(
        label="Payment Method",
        placeholder="Crypto only (e.g. Bitcoin, Ethereum, USDT)",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Create ticket channel
        channel_name = f"buy-{self.ign.value.lower().replace(' ', '-')}"
        try:
            ticket_channel = await create_ticket_channel(
                interaction.guild,
                "buy_account",
                channel_name,
                interaction.user
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error creating buy_account channel: {error_details}")
            return await interaction.followup.send(f"❌ Error creating ticket channel: {str(e)}\n\nPlease check bot permissions and ensure the bot can create channels.", ephemeral=True)
        
        # Create embed
        embed = discord.Embed(
            title="Account Purchase",
            description="Thank you for your interest in buying an account. Please wait for a seller to get to you.",
            color=0x2ecc71,
            timestamp=interaction.created_at
        )
        embed.add_field(name="IGN", value=self.ign.value, inline=True)
        embed.add_field(name="Payment Method", value=self.payment.value, inline=True)
        embed.add_field(name="Buyer", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        
        # Save ticket data
        ticket_data = {
            "opened_by": interaction.user.id,
            "channel_id": ticket_channel.id,
            "ticket_type": "buy_account",
            "is_open": True,
            "ign": self.ign.value,
            "payment_method": self.payment.value
        }
        save_ticket(interaction.guild_id, ticket_data)
        
        # Send initial message with view
        cfg = storage.get_config(interaction.guild_id)
        staff_role_id = cfg.get("staff_role")
        ping_content = ""
        if staff_role_id:
            ping_content = f"<@&{staff_role_id}>"
        
        initial_message = await ticket_channel.send(
            content=f"{ping_content} {interaction.user.mention}" if ping_content else interaction.user.mention,
            embed=embed,
            view=OpenedTicketView()
        )
        await initial_message.pin()
        
        # Log ticket creation
        await BotLogger.log_ticket_created(interaction.guild, ticket_channel, interaction.user, "buy_account", ticket_data)
        
        await interaction.followup.send(f"✅ Your ticket has been created! Go to {ticket_channel.mention}", ephemeral=True)


class SellProfileModal(discord.ui.Modal, title="Sell Profile"):
    username = discord.ui.TextInput(
        label="Username",
        placeholder="Enter the profile username",
        required=True,
        max_length=100
    )
    price = discord.ui.TextInput(
        label="How much you are looking for",
        placeholder="e.g. 50.00",
        required=True,
        max_length=20
    )
    payment = discord.ui.TextInput(
        label="Payment Method",
        placeholder="Crypto only (e.g. Bitcoin, Ethereum, USDT)",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            price_value = float(self.price.value)
            if price_value <= 0:
                return await interaction.response.send_message("❌ Price must be greater than 0!", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid price format! Please enter a valid number (e.g. 50.00)", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Create ticket channel
        channel_name = f"sell-profile-{self.username.value.lower().replace(' ', '-')}"
        try:
            ticket_channel = await create_ticket_channel(
                interaction.guild,
                "sell_profile",
                channel_name,
                interaction.user
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error creating sell_profile channel: {error_details}")
            return await interaction.followup.send(f"❌ Error creating ticket channel: {str(e)}\n\nPlease check bot permissions and ensure the bot can create channels.", ephemeral=True)
        
        # Create embed
        embed = discord.Embed(
            title="Profile Sale",
            description="Thank you for your interest in selling a profile. Please wait for a buyer to get to you.",
            color=0xe74c3c,
            timestamp=interaction.created_at
        )
        embed.add_field(name="Username", value=self.username.value, inline=True)
        embed.add_field(name="Price", value=format_price(price_value), inline=True)
        embed.add_field(name="Payment Method", value=self.payment.value, inline=True)
        embed.add_field(name="Skyblock Stats", value=f"[View on SkyCrypt]({get_skycrypt_link(self.username.value)})", inline=False)
        embed.add_field(name="Seller", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        
        # Save ticket data
        ticket_data = {
            "opened_by": interaction.user.id,
            "channel_id": ticket_channel.id,
            "ticket_type": "sell_profile",
            "is_open": True,
            "username": self.username.value,
            "price": price_value,
            "payment_method": self.payment.value
        }
        save_ticket(interaction.guild_id, ticket_data)
        
        # Send initial message with view
        cfg = storage.get_config(interaction.guild_id)
        staff_role_id = cfg.get("staff_role")
        ping_content = ""
        if staff_role_id:
            ping_content = f"<@&{staff_role_id}>"
        
        initial_message = await ticket_channel.send(
            content=f"{ping_content} {interaction.user.mention}" if ping_content else interaction.user.mention,
            embed=embed,
            view=OpenedTicketView()
        )
        await initial_message.pin()
        
        # Log ticket creation
        await BotLogger.log_ticket_created(interaction.guild, ticket_channel, interaction.user, "sell_profile", ticket_data)
        
        await interaction.followup.send(f"✅ Your ticket has been created! Go to {ticket_channel.mention}", ephemeral=True)


class SellAltModal(discord.ui.Modal, title="Sell Alt"):
    username = discord.ui.TextInput(
        label="Username",
        placeholder="Enter the alt account username",
        required=True,
        max_length=100
    )
    price = discord.ui.TextInput(
        label="How much you are looking for",
        placeholder="e.g. 50.00",
        required=True,
        max_length=20
    )
    payment = discord.ui.TextInput(
        label="Payment Method",
        placeholder="Crypto only (e.g. Bitcoin, Ethereum, USDT)",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Check blacklist
        if storage.is_blacklisted(interaction.guild_id, interaction.user.id):
            return await interaction.response.send_message("❌ You are blacklisted from using this bot.", ephemeral=True)
        
        # Rate limiting for ticket creation
        allowed, retry_after = rate_limiter.check_rate_limit(
            interaction.user.id,
            "create_ticket",
            max_uses=3,
            time_window=300
        )
        if not allowed:
            return await interaction.response.send_message(
                f"⏳ You're creating tickets too quickly. Please wait {retry_after:.1f} seconds.",
                ephemeral=True
            )
        
        try:
            price_value = float(self.price.value)
            if price_value <= 0:
                return await interaction.response.send_message("❌ Price must be greater than 0!", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid price format! Please enter a valid number (e.g. 50.00)", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Create ticket channel
        channel_name = f"sell-alt-{self.username.value.lower().replace(' ', '-')}"
        try:
            ticket_channel = await create_ticket_channel(
                interaction.guild,
                "sell_alt",
                channel_name,
                interaction.user
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error creating sell_alt channel: {error_details}")
            return await interaction.followup.send(f"❌ Error creating ticket channel: {str(e)}\n\nPlease check bot permissions and ensure the bot can create channels.", ephemeral=True)
        
        # Create embed
        embed = discord.Embed(
            title="Alt Account Sale",
            description="Thank you for your interest in selling an alt account. Please wait for a buyer to get to you.",
            color=0xe74c3c,
            timestamp=interaction.created_at
        )
        embed.add_field(name="Username", value=self.username.value, inline=True)
        embed.add_field(name="Price", value=format_price(price_value), inline=True)
        embed.add_field(name="Payment Method", value=self.payment.value, inline=True)
        embed.add_field(name="Skyblock Stats", value=f"[View on SkyCrypt]({get_skycrypt_link(self.username.value)})", inline=False)
        embed.add_field(name="Seller", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        
        # Save ticket data
        ticket_data = {
            "opened_by": interaction.user.id,
            "channel_id": ticket_channel.id,
            "ticket_type": "sell_alt",
            "is_open": True,
            "username": self.username.value,
            "price": price_value,
            "payment_method": self.payment.value
        }
        save_ticket(interaction.guild_id, ticket_data)
        
        # Send initial message with view
        cfg = storage.get_config(interaction.guild_id)
        staff_role_id = cfg.get("staff_role")
        ping_content = ""
        if staff_role_id:
            ping_content = f"<@&{staff_role_id}>"
        
        initial_message = await ticket_channel.send(
            content=f"{ping_content} {interaction.user.mention}" if ping_content else interaction.user.mention,
            embed=embed,
            view=OpenedTicketView()
        )
        await initial_message.pin()
        
        # Log ticket creation
        await BotLogger.log_ticket_created(interaction.guild, ticket_channel, interaction.user, "sell_alt", ticket_data)
        
        await interaction.followup.send(f"✅ Your ticket has been created! Go to {ticket_channel.mention}", ephemeral=True)


class SellMFAModal(discord.ui.Modal, title="Sell an MFA"):
    rank = discord.ui.TextInput(
        label="Rank",
        placeholder="VIP+",
        required=True,
        max_length=10
    )
    count = discord.ui.TextInput(
        label="How many MFA's?",
        placeholder="3",
        required=True,
        max_length=10
    )
    payment = discord.ui.TextInput(
        label="Payment Method",
        placeholder="Crypto only (e.g. Bitcoin, Ethereum, USDT)",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            mfa_count = int(self.count.value)
            if mfa_count <= 0:
                return await interaction.response.send_message("❌ Number of MFAs must be greater than 0!", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid number format! Please enter a valid number.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Normalize rank (handle + in rank)
        rank_input = self.rank.value.strip()
        rank_normalized = rank_input.replace("+", "-plus").upper()
        # Map back to config keys
        rank_map = {"NON": "NON", "VIP": "VIP", "VIP+": "VIP+", "MVP": "MVP", "MVP+": "MVP+"}
        rank_key = rank_map.get(rank_input.upper(), "NON")
        
        cfg = storage.get_config(interaction.guild_id)
        mfa_prices = cfg.get("mfa_prices", {}).get("sell", {})
        price_per_mfa = mfa_prices.get(rank_key, 0.0)
        total_price = price_per_mfa * mfa_count
        
        # Create ticket channel
        rank_safe = rank_normalized
        channel_name = f"sell-{rank_safe}-{mfa_count}"
        try:
            ticket_channel = await create_ticket_channel(
                interaction.guild,
                "sell_mfa",
                channel_name,
                interaction.user
            )
        except Exception as e:
            return await interaction.followup.send(f"❌ Error creating ticket channel: {str(e)}\n\nPlease check bot permissions and ensure the bot can create channels.", ephemeral=True)
        
        # Create embed
        embed = discord.Embed(
            title="MFA Sale",
            description="Thank you for your interest in selling MFAs. Please wait for a seller to get to you.",
            color=0xe74c3c,
            timestamp=interaction.created_at
        )
        embed.add_field(name="Rank", value=rank_input, inline=True)
        embed.add_field(name="Quantity", value=str(mfa_count), inline=True)
        embed.add_field(name="Price per MFA", value=format_price(price_per_mfa), inline=True)
        embed.add_field(name="Total Price", value=format_price(total_price), inline=True)
        embed.add_field(name="Payment Method", value=self.payment.value, inline=True)
        embed.add_field(name="Seller", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        
        # Save ticket data
        ticket_data = {
            "opened_by": interaction.user.id,
            "channel_id": ticket_channel.id,
            "ticket_type": "sell_mfa",
            "is_open": True,
            "rank": rank_key,
            "count": mfa_count,
            "total_price": total_price,
            "payment_method": self.payment.value
        }
        save_ticket(interaction.guild_id, ticket_data)
        
        # Send initial message with view
        staff_role_id = cfg.get("staff_role")
        ping_content = ""
        if staff_role_id:
            ping_content = f"<@&{staff_role_id}>"
        
        initial_message = await ticket_channel.send(
            content=f"{ping_content} {interaction.user.mention}" if ping_content else interaction.user.mention,
            embed=embed,
            view=OpenedTicketView()
        )
        await initial_message.pin()
        
        # Log ticket creation
        await BotLogger.log_ticket_created(interaction.guild, ticket_channel, interaction.user, "sell_mfa", ticket_data)
        
        await interaction.followup.send(f"✅ Your ticket has been created! Go to {ticket_channel.mention} | Total: {format_price(total_price)}", ephemeral=True)


class BuyMFAModal(discord.ui.Modal, title="Buy an MFA"):
    rank_input = discord.ui.TextInput(
        label="Rank",
        placeholder="VIP+",
        required=True,
        max_length=10
    )
    payment = discord.ui.TextInput(
        label="Method of Payment",
        placeholder="Crypto only (e.g. Bitcoin, Ethereum, USDT)",
        required=True,
        max_length=50
    )
    count = discord.ui.TextInput(
        label="How many MFA's?",
        placeholder="3",
        required=True,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Check permissions
        allowed, error_msg = await check_user_permissions(interaction)
        if not allowed:
            return await interaction.response.send_message(error_msg, ephemeral=True)
        
        try:
            mfa_count = int(self.count.value)
            if mfa_count <= 0:
                return await interaction.response.send_message("❌ Number of MFAs must be greater than 0!", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid number format! Please enter a valid number.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Use the rank from the input
        rank_input = self.rank_input.value.strip()
        rank_normalized = rank_input.replace("+", "-plus").upper()
        rank_map = {"NON": "NON", "VIP": "VIP", "VIP+": "VIP+", "MVP": "MVP", "MVP+": "MVP+"}
        rank_key = rank_map.get(rank_input.upper(), "NON")
        
        cfg = storage.get_config(interaction.guild_id)
        mfa_prices = cfg.get("mfa_prices", {}).get("buy", {})
        price_per_mfa = mfa_prices.get(rank_key, 0.0)
        total_price = price_per_mfa * mfa_count
        
        # Create ticket channel
        rank_safe = rank_normalized
        channel_name = f"buy-{rank_safe}-{mfa_count}"
        try:
            ticket_channel = await create_ticket_channel(
                interaction.guild,
                "buy_mfa",
                channel_name,
                interaction.user
            )
        except Exception as e:
            return await interaction.followup.send(f"❌ Error creating ticket channel: {str(e)}\n\nPlease check bot permissions and ensure the bot can create channels.", ephemeral=True)
        
        # Create embed
        embed = discord.Embed(
            title="MFA Purchase",
            description="Thank you for your interest in buying MFAs. Please wait for a seller to get to you.",
            color=0x2ecc71,
            timestamp=interaction.created_at
        )
        embed.add_field(name="Rank", value=rank_input, inline=True)
        embed.add_field(name="Quantity", value=str(mfa_count), inline=True)
        embed.add_field(name="Price per MFA", value=format_price(price_per_mfa), inline=True)
        embed.add_field(name="Total Price", value=format_price(total_price), inline=True)
        embed.add_field(name="Payment Method", value=self.payment.value, inline=True)
        embed.add_field(name="Buyer", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        
        # Save ticket data
        ticket_data = {
            "opened_by": interaction.user.id,
            "channel_id": ticket_channel.id,
            "ticket_type": "buy_mfa",
            "is_open": True,
            "rank": rank_key,
            "count": mfa_count,
            "total_price": total_price,
            "payment_method": self.payment.value
        }
        save_ticket(interaction.guild_id, ticket_data)
        
        # Send initial message with view
        staff_role_id = cfg.get("staff_role")
        ping_content = ""
        if staff_role_id:
            ping_content = f"<@&{staff_role_id}>"
        
        initial_message = await ticket_channel.send(
            content=f"{ping_content} {interaction.user.mention}" if ping_content else interaction.user.mention,
            embed=embed,
            view=OpenedTicketView()
        )
        await initial_message.pin()
        
        # Log ticket creation
        await BotLogger.log_ticket_created(interaction.guild, ticket_channel, interaction.user, "buy_mfa", ticket_data)
        
        await interaction.followup.send(f"✅ Your ticket has been created! Go to {ticket_channel.mention} | Total: {format_price(total_price)}", ephemeral=True)


class BuyCoinsModal(discord.ui.Modal, title="Buy Coins"):
    ign = discord.ui.TextInput(
        label="IGN (In-Game Name)",
        placeholder="Your Minecraft username",
        required=True,
        max_length=100
    )
    amount = discord.ui.TextInput(
        label="How much coins you gonna buy (in millions)",
        placeholder="e.g. 100",
        required=True,
        max_length=20
    )
    payment = discord.ui.TextInput(
        label="Payment Method",
        placeholder="Crypto only (e.g. Bitcoin, Ethereum, USDT)",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            millions = float(self.amount.value)
            if millions <= 0:
                return await interaction.response.send_message("❌ Amount must be greater than 0!", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid amount format! Please enter a valid number (e.g. 100)", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        base_price = cfg.get("coins", {}).get("buy_base_price", 0.0375)
        total_price = calculate_coin_price(millions, base_price)
        
        # Create ticket channel
        amount_safe = str(millions).replace('.', '-')
        channel_name = f"buy-{amount_safe}"
        try:
            ticket_channel = await create_ticket_channel(
                interaction.guild,
                "buy_coins",
                channel_name,
                interaction.user
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error creating buy_coins channel: {error_details}")
            return await interaction.followup.send(f"❌ Error creating ticket channel: {str(e)}\n\nPlease check bot permissions and ensure the bot can create channels.", ephemeral=True)
        
        # Create embed
        embed = discord.Embed(
            title="Coin Purchase",
            description="Thank you for your interest in buying coins. Please wait for a seller to get to you.",
            color=0x2ecc71,
            timestamp=interaction.created_at
        )
        embed.add_field(name="IGN", value=self.ign.value, inline=True)
        embed.add_field(name="Amount", value=f"{millions:.2f}M coins", inline=True)
        embed.add_field(name="Base Price", value=f"{format_price(base_price)}/mil", inline=True)
        embed.add_field(name="Total Price", value=format_price(total_price), inline=True)
        embed.add_field(name="Payment Method", value=self.payment.value, inline=True)
        embed.add_field(name="Buyer", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        
        # Save ticket data
        ticket_data = {
            "opened_by": interaction.user.id,
            "channel_id": ticket_channel.id,
            "ticket_type": "buy_coins",
            "is_open": True,
            "ign": self.ign.value,
            "amount": millions,
            "total_price": total_price,
            "payment_method": self.payment.value
        }
        save_ticket(interaction.guild_id, ticket_data)
        
        # Send initial message with view
        staff_role_id = cfg.get("staff_role")
        ping_content = ""
        if staff_role_id:
            ping_content = f"<@&{staff_role_id}>"
        
        initial_message = await ticket_channel.send(
            content=f"{ping_content} {interaction.user.mention}" if ping_content else interaction.user.mention,
            embed=embed,
            view=OpenedTicketView()
        )
        await initial_message.pin()
        
        # Log ticket creation
        await BotLogger.log_ticket_created(interaction.guild, ticket_channel, interaction.user, "buy_coins", ticket_data)
        
        await interaction.followup.send(f"✅ Your ticket has been created! Go to {ticket_channel.mention} | Total: {format_price(total_price)}", ephemeral=True)


class SellCoinsModal(discord.ui.Modal, title="Sell Coins"):
    ign = discord.ui.TextInput(
        label="IGN (In-Game Name)",
        placeholder="Your Minecraft username",
        required=True,
        max_length=100
    )
    amount = discord.ui.TextInput(
        label="How much coins you gonna sell (in millions)",
        placeholder="e.g. 100",
        required=True,
        max_length=20
    )
    payment = discord.ui.TextInput(
        label="Payment Method",
        placeholder="Crypto only (e.g. Bitcoin, Ethereum, USDT)",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            millions = float(self.amount.value)
            if millions <= 0:
                return await interaction.response.send_message("❌ Amount must be greater than 0!", ephemeral=True)
        except ValueError:
            return await interaction.response.send_message("❌ Invalid amount format! Please enter a valid number (e.g. 100)", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        cfg = storage.get_config(interaction.guild_id)
        base_price = cfg.get("coins", {}).get("sell_base_price", 0.015)
        total_price = calculate_coin_price(millions, base_price)
        
        # Create ticket channel
        amount_safe = str(millions).replace('.', '-')
        channel_name = f"sell-{amount_safe}"
        try:
            ticket_channel = await create_ticket_channel(
                interaction.guild,
                "sell_coins",
                channel_name,
                interaction.user
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error creating sell_coins channel: {error_details}")
            return await interaction.followup.send(f"❌ Error creating ticket channel: {str(e)}\n\nPlease check bot permissions and ensure the bot can create channels.", ephemeral=True)
        
        # Create embed
        embed = discord.Embed(
            title="Coin Sale",
            description="Thank you for your interest in selling coins. Please wait for a seller to get to you.",
            color=0xe74c3c,
            timestamp=interaction.created_at
        )
        embed.add_field(name="IGN", value=self.ign.value, inline=True)
        embed.add_field(name="Amount", value=f"{millions:.2f}M coins", inline=True)
        embed.add_field(name="Base Price", value=f"{format_price(base_price)}/mil", inline=True)
        embed.add_field(name="Total Price", value=format_price(total_price), inline=True)
        embed.add_field(name="Payment Method", value=self.payment.value, inline=True)
        embed.add_field(name="Seller", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")
        
        # Save ticket data
        ticket_data = {
            "opened_by": interaction.user.id,
            "channel_id": ticket_channel.id,
            "ticket_type": "sell_coins",
            "is_open": True,
            "ign": self.ign.value,
            "amount": millions,
            "total_price": total_price,
            "payment_method": self.payment.value
        }
        save_ticket(interaction.guild_id, ticket_data)
        
        # Send initial message with view
        staff_role_id = cfg.get("staff_role")
        ping_content = ""
        if staff_role_id:
            ping_content = f"<@&{staff_role_id}>"
        
        initial_message = await ticket_channel.send(
            content=f"{ping_content} {interaction.user.mention}" if ping_content else interaction.user.mention,
            embed=embed,
            view=OpenedTicketView()
        )
        await initial_message.pin()
        
        # Log ticket creation
        await BotLogger.log_ticket_created(interaction.guild, ticket_channel, interaction.user, "sell_coins", ticket_data)
        
        await interaction.followup.send(f"✅ Your ticket has been created! Go to {ticket_channel.mention} | Total: {format_price(total_price)}", ephemeral=True)
