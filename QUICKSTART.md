# Quick Start Guide

## Running the Bot

1. **Make sure you have Python 3.8+ installed**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your bot token in `.env`:**
   ```
   DISCORD_TOKEN="YOUR_BOT_TOKEN_HERE"
   ```

4. **Run the bot:**
   ```bash
   python src/bot.py
   ```

## First Time Setup

Once your bot is online and in your server:

### 1. Configure Channels
```
/bot set_channels tickets:#ticket-channel vouches:#vouch-channel
```

### 2. Add Yourself as Owner (if needed)
```
/bot add_owner @YourUsername
```

### 3. Set Staff Role
```
/bot set_staff_role @Staff
```

### 4. Configure Prices (Optional - defaults are already set)
```
/bot set_mfa_prices non:7.0 vip:8.0 vip_plus:9.5 mvp:11.0 mvp_plus:17.0
/bot set_coin_prices buy_price:0.0375 sell_price:0.015
```

### 5. Send the Panels
In your desired channels, run:
```
/ticket_panel
/mfa_panel
/coin_panel
```

## Using the Bot

### For Users:

**Opening a Ticket:**
- Click "Sell an Account", "Sell a Profile", or "Sell an Alt" button
- Fill out the modal with username, price, and payment method

**Selling MFAs:**
- Click the rank button or use the dropdown in the MFA panel
- Enter quantity and payment method
- Price is automatically calculated

**Trading Coins:**
- Click "Buy Coins" or "Sell Coins" in the coin panel
- Enter your IGN and amount in millions
- Price is automatically calculated

**Leaving a Vouch:**
```
/vouch seller:@SellerUsername product:"Account" value:50 review:"Great service!" rating:5
```

### For Owners:

**View Current Config:**
```
/bot view_config
```

**Update Prices:**
```
/bot set_mfa_prices mvp:12.0
/bot set_coin_prices buy_price:0.04
```

**Set Banner Images:**
```
/bot set_ticket_banner https://example.com/image.png
/bot set_mfa_banner https://example.com/image.png
/bot set_coin_banner https://example.com/image.png
```

**Update Payment Methods:**
```
/bot set_payment_methods PayPal,Crypto,CashApp,Venmo
```

## Features Overview

✅ **Ticket System** - Users submit tickets for selling accounts/profiles/alts
✅ **MFA Panel** - Interactive buttons and dropdown for MFA trading
✅ **Coin Trading** - Automatic price calculation for buying/selling coins
✅ **Vouch System** - Track seller reputation with ratings and reviews
✅ **Owner Config** - Full configuration through Discord commands
✅ **Persistent Views** - Buttons work even after bot restart
✅ **Multi-Guild** - Works across multiple servers with separate configs

## Troubleshooting

**Commands not showing up?**
- Make sure the bot has "Use Application Commands" permission
- Wait a few minutes for Discord to sync commands
- Try kicking and re-inviting the bot

**Buttons not working?**
- Make sure the bot is online
- Persistent views are enabled by default

**Vouch not posting to channel?**
- Check that you've set the vouch channel with `/bot set_channels`
- Make sure the bot has permission to send messages in that channel

## Support

For issues or feature requests, contact the bot owner.

## What's Included

- ✅ Complete ticket submission system
- ✅ MFA trading with rank buttons and dropdown
- ✅ Coin trading with automatic calculations
- ✅ Full vouch system with statistics
- ✅ Comprehensive configuration commands
- ✅ Banner image support for all panels
- ✅ Permission system (owners, staff)
- ✅ Multi-guild support
- ✅ Persistent buttons (survive restarts)
- ✅ Data persistence (JSON storage)

Enjoy your new Hypixel Account Shop bot! 🎮
