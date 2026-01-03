import discord
from src import storage

def is_owner(interaction: discord.Interaction) -> bool:
    """Check if user is a bot owner or guild owner"""
    app_cfg = storage.load_app_config()
    guild_cfg = storage.get_config(interaction.guild_id)
    
    # Check global owner
    if app_cfg.get("owner_id") and interaction.user.id == app_cfg["owner_id"]:
        return True
    
    # Check guild owners
    if interaction.user.id in guild_cfg.get("owners", []):
        return True
    
    # Check if user is guild owner
    if interaction.guild and interaction.user.id == interaction.guild.owner_id:
        return True
    
    return False

def is_staff(interaction: discord.Interaction) -> bool:
    """Check if user has staff role"""
    guild_cfg = storage.get_config(interaction.guild_id)
    staff_role_id = guild_cfg.get("staff_role")
    
    if not staff_role_id:
        return False
    
    if interaction.user.guild_permissions.administrator:
        return True
    
    return any(role.id == staff_role_id for role in interaction.user.roles)

def has_staff_privs(interaction: discord.Interaction) -> bool:
    """Check if user has staff privileges (alias for is_staff)"""
    return is_staff(interaction)
