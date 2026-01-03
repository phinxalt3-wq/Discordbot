import discord
from discord.ext import commands
from discord import app_commands
from src import storage
from src.utils.permissions import is_owner, is_staff
from typing import Optional, Literal
import json
import os

class Stock(commands.Cog):
    """Stock management system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_path = os.path.join(storage.DATA_DIR, "stock.json")
        self.ensure_stock_file()
        
    def ensure_stock_file(self):
        if not os.path.exists(self.data_path):
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump({}, f)
                
    def load_stock(self):
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def save_stock(self, data):
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    stock_group = app_commands.Group(name="stock", description="Stock management commands")

    @stock_group.command(name="add", description="Add an item to the stock list")
    @app_commands.describe(
        category="Category of the item (e.g. Accounts, MFA, Coins)",
        item="The item description or name"
    )
    async def add_stock(self, interaction: discord.Interaction, category: str, item: str):
        if not is_staff(interaction) and not is_owner(interaction):
            return await interaction.response.send_message("❌ Unauthorized.", ephemeral=True)
        
        data = self.load_stock()
        guild_id = str(interaction.guild_id)
        
        if guild_id not in data:
            data[guild_id] = {}
            
        # Normalize category
        cat_key = category.strip().title()
        
        if cat_key not in data[guild_id]:
            data[guild_id][cat_key] = []
            
        data[guild_id][cat_key].append(item)
        self.save_stock(data)
        
        await interaction.response.send_message(f"✅ Added to **{cat_key}**: `{item}`", ephemeral=True)

    @stock_group.command(name="remove", description="Remove an item from stock")
    @app_commands.describe(
        category="Category to remove from",
        index="The number of the item to remove (from /stock view)"
    )
    async def remove_stock(self, interaction: discord.Interaction, category: str, index: int):
        if not is_staff(interaction) and not is_owner(interaction):
            return await interaction.response.send_message("❌ Unauthorized.", ephemeral=True)
        
        data = self.load_stock()
        guild_id = str(interaction.guild_id)
        cat_key = category.strip().title()
        
        if guild_id not in data or cat_key not in data[guild_id]:
            return await interaction.response.send_message("❌ Category not found.", ephemeral=True)
            
        items = data[guild_id][cat_key]
        if index < 1 or index > len(items):
            return await interaction.response.send_message("❌ Invalid item number.", ephemeral=True)
            
        removed = items.pop(index - 1)
        
        # Cleanup if empty
        if not items:
            del data[guild_id][cat_key]
            
        self.save_stock(data)
        
        await interaction.response.send_message(f"✅ Removed from **{cat_key}**: `{removed}`", ephemeral=True)

    @stock_group.command(name="clear", description="Clear an entire category")
    async def clear_stock(self, interaction: discord.Interaction, category: str):
        if not is_owner(interaction): # Only owner for clear
             return await interaction.response.send_message("❌ Unauthorized.", ephemeral=True)
             
        data = self.load_stock()
        guild_id = str(interaction.guild_id)
        cat_key = category.strip().title()
        
        if guild_id in data and cat_key in data[guild_id]:
            del data[guild_id][cat_key]
            self.save_stock(data)
            await interaction.response.send_message(f"✅ Cleared category **{cat_key}**.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Category not found.", ephemeral=True)

    @stock_group.command(name="view", description="View current stock (Admin view with IDs)")
    async def view_stock_admin(self, interaction: discord.Interaction):
        if not is_staff(interaction) and not is_owner(interaction):
            return await interaction.response.send_message("❌ Unauthorized.", ephemeral=True)
            
        data = self.load_stock()
        guild_id = str(interaction.guild_id)
        
        if guild_id not in data or not data[guild_id]:
            return await interaction.response.send_message("📦 Stock is empty.", ephemeral=True)
            
        embed = discord.Embed(title="📦 Current Stock (Admin)", color=0x3498db)
        
        for category, items in data[guild_id].items():
            if items:
                # Format with indices for removal
                formatted_items = [f"`{i+1}.` {item}" for i, item in enumerate(items)]
                embed.add_field(name=category, value="\n".join(formatted_items), inline=False)
                
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @stock_group.command(name="list", description="Show public stock list")
    async def public_stock(self, interaction: discord.Interaction):
        data = self.load_stock()
        guild_id = str(interaction.guild_id)
        
        if guild_id not in data or not data[guild_id]:
            return await interaction.response.send_message("📦 Stock is currently empty. Check back later!", ephemeral=True)
            
        embed = discord.Embed(
            title="📦  **Available Stock**",
            description="Use `/ticket` to purchase any of these items.",
            color=0x2ecc71
        )
        
        for category, items in data[guild_id].items():
            if items:
                # Format as bullet points
                formatted_items = [f"• {item}" for item in items]
                embed.add_field(name=f"**{category}**", value="\n".join(formatted_items), inline=False)
        
        if interaction.guild.icon:
            embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stock(bot))