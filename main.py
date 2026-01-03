import sys
import os

# Add the current directory to sys.path so we can import src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import storage
from src.bot import bot, TOKEN

if __name__ == "__main__":
    storage.ensure_files()
    if not TOKEN:
        print("Error: DISCORD_TOKEN is not set in .env or config.json")
        sys.exit(1)
    
    print("Starting bot...")
    bot.run(TOKEN)