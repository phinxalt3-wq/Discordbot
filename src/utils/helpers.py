import discord
from typing import Optional

def create_embed(
    title: str,
    description: Optional[str] = None,
    color: int = 0x2b2d31,
    image_url: Optional[str] = None,
    footer: Optional[str] = None
) -> discord.Embed:
    """Create a standardized embed"""
    embed = discord.Embed(title=title, description=description, color=color)
    
    if image_url:
        embed.set_image(url=image_url)
    
    if footer:
        embed.set_footer(text=footer)
    
    return embed

def format_price(amount: float) -> str:
    """Format price as currency"""
    return f"${amount:.2f}"

def get_skycrypt_link(username: str) -> str:
    """Get SkyCrypt stats link for a username"""
    # Clean username (remove spaces, handle special characters)
    clean_username = username.strip().replace(" ", "")
    return f"https://sky.shiiyu.moe/stats/{clean_username}"

def calculate_coin_price(millions: float, base_price: float) -> float:
    """Calculate total price for coins"""
    return millions * base_price
