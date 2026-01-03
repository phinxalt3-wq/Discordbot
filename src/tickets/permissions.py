import discord
from src.utils.permissions import is_owner as _is_owner, is_staff as _is_staff

def is_owner(interaction: discord.Interaction) -> bool:
    """Check if user is a bot owner or guild owner"""
    return _is_owner(interaction)

def has_staff_privs(interaction: discord.Interaction) -> bool:
    """Check if user has staff privileges (alias for is_staff)"""
    return _is_staff(interaction)

