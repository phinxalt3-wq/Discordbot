import os
import sys
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import traceback
import asyncio

# Add parent directory to path if not already present
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src import storage
from src.ui.views import TicketPanel, MFAPanel, CoinPanel, AccountBuyPanel
from src.ui.ticket_views import OpenedTicketView
from src.ui.vouch_views import VouchButtonView
from src.utils.logging import BotLogger

load_dotenv()
app_cfg = storage.load_app_config()

TOKEN = os.getenv("DISCORD_TOKEN") or app_cfg.get("token")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class ShopBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    
    async def setup_hook(self):
        # Add persistent views
        self.add_view(TicketPanel())
        self.add_view(MFAPanel())
        self.add_view(CoinPanel())
        self.add_view(AccountBuyPanel())
        self.add_view(OpenedTicketView())
        
        # Load cogs
        await self.load_extension("src.cogs.owner")
        await self.load_extension("src.cogs.panel")
        await self.load_extension("src.cogs.tickets")
        await self.load_extension("src.cogs.vouch")
        await self.load_extension("src.cogs.pricing")
        await self.load_extension("src.cogs.backup")
        await self.load_extension("src.cogs.moderation")
        await self.load_extension("src.cogs.wallet")
        await self.load_extension("src.cogs.utility")
        await self.load_extension("src.cogs.status")
        await self.load_extension("src.cogs.stock")
        
        # Sync commands globally first to register new commands
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} command(s) globally")
        except Exception as e:
            print(f"⚠️ Error syncing globally: {e}")

bot = ShopBot()

@bot.event
async def on_ready():
    print(f"\n{'='*50}")
    print(f"Bot is ready!")
    print(f"Logged in as: {bot.user} (ID: {bot.user.id})")
    print(f"Connected to {len(bot.guilds)} guild(s)")

    # Sync commands to all guilds (guild-specific, faster)
    print("\nSyncing commands to guilds...")
    try:
        # Wait a bit for commands to be fully registered
        await asyncio.sleep(1)
        
        for guild in bot.guilds:
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ Synced {len(synced)} command(s) to {guild.name} (ID: {guild.id})")
            if synced:
                for cmd in synced:
                    print(f"   - {cmd.name}")
            else:
                print(f"   ⚠️ No commands synced (may need to wait or sync globally)")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")
        traceback.print_exc()

    print(f"{'='*50}\n")

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle command errors and log them"""
    if interaction.guild:
        await BotLogger.log_error(interaction.guild, error, f"Command: {interaction.command.name if interaction.command else 'Unknown'}")
    
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"⏳ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
    elif isinstance(error, app_commands.BotMissingPermissions):
        await interaction.response.send_message("❌ I don't have the required permissions to execute this command.", ephemeral=True)
    else:
        error_msg = f"❌ An error occurred: {str(error)}"
        if len(error_msg) > 2000:
            error_msg = error_msg[:1997] + "..."
        
        try:
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)
        except:
            pass
        
        print(f"Command error: {error}")
        traceback.print_exc()

@bot.event
async def on_error(event, *args, **kwargs):
    """Handle general errors"""
    print(f"Error in event {event}:")
    traceback.print_exc()

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN is not set in .env or config.json")
        sys.exit(1)
    storage.ensure_files()
    bot.run(TOKEN)
