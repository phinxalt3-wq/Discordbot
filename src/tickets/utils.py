import discord
from src import storage

def get_category_for_ticket_type(guild, ticket_type: str):
    """Get the category channel for a ticket type"""
    cfg = storage.get_config(guild.id)
    # Try to get category from ticket_categories config
    category_id = cfg.get("ticket_categories", {}).get(ticket_type, {}).get("category_id")
    if category_id:
        category = guild.get_channel(category_id)
        if category and isinstance(category, discord.CategoryChannel):
            return category
    
    # Fallback: try to get from channels config
    # For now, we'll create channels without a category if none is set
    return None

async def create_ticket_channel(guild: discord.Guild, ticket_type: str, channel_name: str, user: discord.Member):
    """Create a ticket channel with proper permissions"""
    cfg = storage.get_config(guild.id)
    
    # Get category
    category = get_category_for_ticket_type(guild, ticket_type)
    
    # Get staff role
    staff_role_id = cfg.get("staff_role")
    staff_role = guild.get_role(staff_role_id) if staff_role_id else None
    
    # Create permission overwrites
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
        guild.me: discord.PermissionOverwrite(
            read_messages=True, 
            send_messages=True, 
            view_channel=True,
            manage_channels=True,
            manage_messages=True
        ),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True),
    }
    
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)
    
    # Create channel
    try:
        if category and len(category.channels) < 50:
            channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)
        else:
            channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        return channel
    except discord.Forbidden:
        raise Exception(f"Bot doesn't have permission to create channels. Please ensure the bot has 'Manage Channels' permission.")
    except discord.HTTPException as e:
        raise Exception(f"Discord API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error creating channel: {str(e)}")

def save_ticket(guild_id: int, ticket_data: dict):
    """Save ticket data to JSON storage"""
    import json
    import os
    from datetime import datetime
    
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    TICKETS_PATH = os.path.join(DATA_DIR, "tickets.json")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if os.path.exists(TICKETS_PATH):
        with open(TICKETS_PATH, "r", encoding="utf-8") as f:
            tickets = json.load(f)
    else:
        tickets = {}
    
    guild_key = str(guild_id)
    if guild_key not in tickets:
        tickets[guild_key] = {}
    
    # Add opened_at timestamp if not present
    if "opened_at" not in ticket_data:
        ticket_data["opened_at"] = datetime.utcnow().isoformat()
    
    channel_id = str(ticket_data["channel_id"])
    tickets[guild_key][channel_id] = ticket_data
    
    with open(TICKETS_PATH, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2)

def get_ticket(guild_id: int, channel_id: int):
    """Get ticket data from JSON storage"""
    import json
    import os
    
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    TICKETS_PATH = os.path.join(DATA_DIR, "tickets.json")
    
    if not os.path.exists(TICKETS_PATH):
        return None
    
    with open(TICKETS_PATH, "r", encoding="utf-8") as f:
        tickets = json.load(f)
    
    guild_key = str(guild_id)
    channel_key = str(channel_id)
    
    if guild_key in tickets and channel_key in tickets[guild_key]:
        return tickets[guild_key][channel_key]
    
    return None

def close_ticket(guild_id: int, channel_id: int):
    """Mark a ticket as closed"""
    import json
    import os
    
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    TICKETS_PATH = os.path.join(DATA_DIR, "tickets.json")
    
    if not os.path.exists(TICKETS_PATH):
        return
    
    with open(TICKETS_PATH, "r", encoding="utf-8") as f:
        tickets = json.load(f)
    
    guild_key = str(guild_id)
    channel_key = str(channel_id)
    
    if guild_key in tickets and channel_key in tickets[guild_key]:
        tickets[guild_key][channel_key]["is_open"] = False
        
        with open(TICKETS_PATH, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=2)

