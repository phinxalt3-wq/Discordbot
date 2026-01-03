import discord
from discord.ext import commands, tasks
from discord import app_commands
from src import storage
from datetime import datetime
import asyncio
import random

class Status(commands.Cog):
    """Status rotator to market the shop"""
    
    def __init__(self, bot):
        self.bot = bot
        self.status_task.start()
        
    def cog_unload(self):
        self.status_task.cancel()
        
    @tasks.loop(seconds=10)
    async def status_task(self):
        """Rotate through marketing statuses"""
        try:
            # Get data for dynamic statuses
            guild_count = len(self.bot.guilds)
            
            # Simple list of statuses
            # In a real app, these could be configurable
            statuses = [
                discord.Activity(type=discord.ActivityType.watching, name=f"{guild_count} Servers"),
                discord.Activity(type=discord.ActivityType.playing, name="Hypixel Account Shop"),
                discord.Activity(type=discord.ActivityType.listening, name="Ticket Requests"),
                discord.Activity(type=discord.ActivityType.watching, name="Stock Updates"),
                discord.Activity(type=discord.ActivityType.playing, name="Best Rates in Market 💸"),
                discord.Activity(type=discord.ActivityType.watching, name="Your Tickets 🎫")
            ]
            
            # Choose one randomly or sequentially (using random here for variety)
            new_status = random.choice(statuses)
            
            await self.bot.change_presence(activity=new_status, status=discord.Status.online)
            
        except Exception as e:
            print(f"Error in status task: {e}")

    @status_task.before_loop
    async def before_status_task(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Status(bot))
