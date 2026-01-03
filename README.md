# Discord Hypixel Account Shop Bot

A comprehensive Discord bot for managing a Hypixel account shop with ticket systems, MFA trading, coin trading, and vouch system.

## Features

### 🎫 Ticket System
- **Sell Account**: Users can submit tickets to sell accounts with username, price, and payment method
- **Sell Profile**: Submit tickets to sell profiles
- **Sell Alt**: Submit tickets to sell alt accounts

### 🔐 MFA Panel
- Interactive panel with buttons for each rank (NON, VIP, VIP+, MVP, MVP+)
- Dropdown menu for rank selection
- Automatic price calculation based on configured prices
- Users specify quantity and payment method

### 💰 Coin Trading
- **Buy Coins**: Calculate total price based on configured rate per million coins
- **Sell Coins**: Users can sell coins with automatic price calculation
- IGN (In-Game Name) tracking

### ⭐ Vouch System
- Complete vouch system matching the format shown
- Tracks seller statistics (total vouches, average rating)
- Star rating display (1-5 stars)
- Automatic posting to configured vouch channel

### 🔧 Owner Configuration (`/bot` commands)
- `/bot config` - **NEW!** Open interactive configuration menu with buttons
- `/bot set_channels` - Configure ticket and vouch channels
- `/bot set_staff_role` - Set the staff role
- `/bot add_owner` - Add guild owners
- `/bot set_mfa_prices` - Configure MFA prices for each rank
- `/bot set_coin_prices` - Set coin buy/sell prices
- `/bot set_payment_methods` - Configure accepted payment methods
- `/bot set_ticket_banner` - Set banner image for ticket panel
- `/bot set_mfa_banner` - Set banner image for MFA panel
- `/bot set_coin_banner` - Set banner image for coin panel
- `/bot view_config` - View current configuration

### 📊 Panel Commands
- `/ticket_panel` - Send the ticket panel with all buttons
- `/mfa_panel` - Send the MFA panel with rank buttons and dropdown
- `/coin_panel` - Send the coin trading panel

## Installation

1. **Install Python 3.8 or higher**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot:**
   - Edit `.env` file and add your Discord bot token:
     ```
     DISCORD_TOKEN="your_bot_token_here"
     ```
   
   - Or edit `config.json`:
     ```json
     {
       "token": "your_bot_token_here",
       "client_id": "your_client_id",
       "owner_id": your_user_id
     }
     ```

4. **Run the bot:**
   ```bash
   python src/bot.py
   ```

## Setup Instructions

1. **Invite the bot to your server** with the following permissions:
   - Send Messages
   - Embed Links
   - Read Message History
   - Use Slash Commands
   - Manage Channels (optional, for ticket system)

2. **Configure the bot using `/bot` commands:**
   ```
   /bot set_channels tickets:#tickets-channel vouches:#vouches-channel
   /bot set_staff_role @Staff
   /bot set_mfa_prices non:7.0 vip:8.0 vip_plus:9.5 mvp:11.0 mvp_plus:17.0
   /bot set_coin_prices buy_price:0.0375 sell_price:0.015
   ```

3. **Send the panels:**
   ```
   /ticket_panel
   /mfa_panel
   /coin_panel
   ```

4. **Users can now:**
   - Click buttons to open tickets
   - Select MFA ranks and submit orders
   - Buy/sell coins with automatic price calculation
   - Leave vouches using `/vouch`

## Configuration

### Default Prices
- **MFA Prices:**
  - NON: $7.00
  - VIP: $8.00
  - VIP+: $9.50
  - MVP: $11.00
  - MVP+: $17.00

- **Coin Prices:**
  - Buy: $0.0375 per million
  - Sell: $0.015 per million

### Payment Methods
Default: PayPal, Crypto, UPI

All configurations can be changed using the `/bot` commands.

## File Structure

```
bot/
├── src/
│   ├── cogs/
│   │   ├── owner.py          # Owner configuration commands
│   │   ├── panel.py          # Panel commands
│   │   ├── tickets.py        # Ticket system
│   │   └── vouch.py          # Vouch system
│   ├── ui/
│   │   ├── modals.py         # All modal forms
│   │   └── views.py          # All button panels
│   ├── utils/
│   │   ├── permissions.py    # Permission checks
│   │   └── helpers.py        # Helper functions
│   ├── bot.py                # Main bot file
│   └── storage.py            # Data management
├── data/
│   ├── guilds.json           # Guild configurations
│   └── vouches.json          # Vouch data
├── config.json               # Bot configuration
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Vouch Command Usage

```
/vouch seller:@User product:"Hypixel Account" value:50.00 review:"Great seller!" rating:5
```

## Support

For issues or questions, contact the bot owner.

## Credits

Developed for Skyuub's Slave - Hypixel Account Shop
