import discord
import os
import logging
from datetime import datetime
from src import storage

# Set up file logging
def setup_file_logging(guild_id: int = None):
    """Set up file-based logging"""
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    if guild_id:
        log_file = os.path.join(logs_dir, f"guild_{guild_id}.log")
    else:
        log_file = os.path.join(logs_dir, "bot.log")
    
    # Create logger
    logger = logging.getLogger(f"bot_{guild_id}" if guild_id else "bot")
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    return logger

class BotLogger:
    """Centralized logging system for bot events"""
    
    @staticmethod
    async def get_log_channel(guild: discord.Guild):
        """Get the configured log channel for a guild"""
        cfg = storage.get_config(guild.id)
        log_channel_id = cfg.get("channels", {}).get("logs")
        if log_channel_id:
            return guild.get_channel(log_channel_id)
        return None
    
    @staticmethod
    async def log_ticket_created(guild: discord.Guild, ticket_channel: discord.TextChannel, user: discord.Member, ticket_type: str, ticket_data: dict):
        """Log when a ticket is created"""
        # File logging
        logger = setup_file_logging(guild.id)
        logger.info(f"Ticket created - Type: {ticket_type}, Channel: {ticket_channel.name} (ID: {ticket_channel.id}), User: {user.name}#{user.discriminator} (ID: {user.id})")
        
        log_channel = await BotLogger.get_log_channel(guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="🎫 Ticket Created",
            color=0x2ecc71,  # Green
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Ticket Type", value=ticket_type.replace("_", " ").title(), inline=True)
        embed.add_field(name="Channel", value=ticket_channel.mention, inline=True)
        embed.add_field(name="Opened By", value=f"{user.mention} ({user.id})", inline=False)
        
        # Add ticket-specific details
        if "username" in ticket_data:
            embed.add_field(name="Username", value=ticket_data["username"], inline=True)
        if "price" in ticket_data:
            embed.add_field(name="Price", value=f"${ticket_data['price']:.2f}", inline=True)
        if "amount" in ticket_data:
            embed.add_field(name="Amount", value=f"{ticket_data['amount']:.2f}M", inline=True)
        if "rank" in ticket_data:
            embed.add_field(name="Rank", value=ticket_data["rank"], inline=True)
        if "count" in ticket_data:
            embed.add_field(name="Count", value=str(ticket_data["count"]), inline=True)
        if "payment_method" in ticket_data:
            embed.add_field(name="Payment Method", value=ticket_data["payment_method"], inline=True)
        
        embed.set_footer(text=f"Channel ID: {ticket_channel.id}")
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging ticket creation: {e}")
    
    @staticmethod
    async def log_ticket_closed(guild: discord.Guild, ticket_channel: discord.TextChannel, closed_by: discord.Member, ticket_data: dict = None):
        """Log when a ticket is closed and generate transcript"""
        from src.utils.transcripts import TranscriptGenerator
        
        log_channel = await BotLogger.get_log_channel(guild)
        
        # Generate transcript
        transcript_path = None
        html_transcript_path = None
        try:
            transcript_path = await TranscriptGenerator.generate_transcript(ticket_channel, ticket_data)
            html_transcript_path = await TranscriptGenerator.generate_html_transcript(ticket_channel, ticket_data)
        except Exception as e:
            print(f"Error generating transcript: {e}")
        
        # File logging
        logger = setup_file_logging(guild.id)
        logger.info(f"Ticket closed - Channel: {ticket_channel.name} (ID: {ticket_channel.id}), Closed by: {closed_by.name}#{closed_by.discriminator} (ID: {closed_by.id})")
        
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="🔒 Ticket Closed",
            color=0xe74c3c,  # Red
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Channel", value=ticket_channel.mention, inline=True)
        embed.add_field(name="Closed By", value=f"{closed_by.mention} ({closed_by.id})", inline=True)
        
        if ticket_data:
            if "opened_by" in ticket_data:
                opener = guild.get_member(ticket_data["opened_by"])
                if opener:
                    embed.add_field(name="Opened By", value=f"{opener.mention} ({opener.id})", inline=False)
            if "ticket_type" in ticket_data:
                embed.add_field(name="Ticket Type", value=ticket_data["ticket_type"].replace("_", " ").title(), inline=True)
        
        # Add transcript info
        if transcript_path or html_transcript_path:
            transcript_info = []
            if transcript_path:
                transcript_info.append(f"📄 Text: `{os.path.basename(transcript_path)}`")
            if html_transcript_path:
                transcript_info.append(f"🌐 HTML: `{os.path.basename(html_transcript_path)}`")
            embed.add_field(name="Transcripts Generated", value="\n".join(transcript_info), inline=False)
        
        embed.set_footer(text=f"Channel ID: {ticket_channel.id}")
        
        try:
            # Send embed
            message = await log_channel.send(embed=embed)
            
            # Send transcript files if available
            if transcript_path and os.path.exists(transcript_path):
                try:
                    with open(transcript_path, "rb") as f:
                        transcript_file = discord.File(f, filename=os.path.basename(transcript_path))
                        await log_channel.send(file=transcript_file)
                except Exception as e:
                    print(f"Error sending transcript file: {e}")
            
            if html_transcript_path and os.path.exists(html_transcript_path):
                try:
                    with open(html_transcript_path, "rb") as f:
                        html_file = discord.File(f, filename=os.path.basename(html_transcript_path))
                        await log_channel.send(file=html_file)
                except Exception as e:
                    print(f"Error sending HTML transcript file: {e}")
                    
        except Exception as e:
            print(f"Error logging ticket closure: {e}")
    
    @staticmethod
    async def log_command_execution(guild: discord.Guild, user: discord.Member, command_name: str, channel: discord.TextChannel = None):
        """Log command executions"""
        log_channel = await BotLogger.get_log_channel(guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="⚙️ Command Executed",
            color=0x3498db,  # Blue
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Command", value=f"`/{command_name}`", inline=True)
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
        if channel:
            embed.add_field(name="Channel", value=channel.mention, inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging command: {e}")
    
    @staticmethod
    async def log_error(guild: discord.Guild, error: Exception, context: str = None):
        """Log errors"""
        # File logging
        logger = setup_file_logging(guild.id)
        logger.error(f"Error occurred - Type: {type(error).__name__}, Message: {str(error)}, Context: {context}", exc_info=True)
        
        log_channel = await BotLogger.get_log_channel(guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="❌ Error Occurred",
            color=0xe74c3c,  # Red
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Error Type", value=type(error).__name__, inline=True)
        embed.add_field(name="Error Message", value=str(error)[:1024], inline=False)
        if context:
            embed.add_field(name="Context", value=context[:1024], inline=False)
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging error: {e}")
    
    @staticmethod
    async def log_config_change(guild: discord.Guild, user: discord.Member, config_type: str, old_value: str = None, new_value: str = None):
        """Log configuration changes"""
        # File logging
        logger = setup_file_logging(guild.id)
        logger.info(f"Config changed - Type: {config_type}, User: {user.name}#{user.discriminator} (ID: {user.id}), Old: {old_value}, New: {new_value}")
        
        log_channel = await BotLogger.get_log_channel(guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="⚙️ Configuration Changed",
            color=0xf39c12,  # Orange
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Config Type", value=config_type, inline=True)
        embed.add_field(name="Changed By", value=f"{user.mention} ({user.id})", inline=True)
        if old_value:
            embed.add_field(name="Old Value", value=str(old_value)[:1024], inline=False)
        if new_value:
            embed.add_field(name="New Value", value=str(new_value)[:1024], inline=False)
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging config change: {e}")
    
    @staticmethod
    async def log_vouch_submitted(guild: discord.Guild, user: discord.Member, seller: discord.Member, rating: int):
        """Log when a vouch is submitted"""
        # File logging
        logger = setup_file_logging(guild.id)
        logger.info(f"Vouch submitted - User: {user.name}#{user.discriminator} (ID: {user.id}), Seller: {seller.name}#{seller.discriminator} (ID: {seller.id}), Rating: {rating}")
        
        log_channel = await BotLogger.get_log_channel(guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title="⭐ Vouch Submitted",
            color=0xf1c40f,  # Yellow
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Vouched By", value=f"{user.mention} ({user.id})", inline=True)
        embed.add_field(name="Seller", value=f"{seller.mention} ({seller.id})", inline=True)
        embed.add_field(name="Rating", value="⭐" * rating, inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging vouch: {e}")
    
    @staticmethod
    async def log_mod_action(
        guild: discord.Guild,
        moderator: discord.Member,
        action: str,
        target: discord.Member | discord.User,
        reason: str
    ):
        """Log moderation actions"""
        try:
            logger = setup_file_logging(guild.id)
            logger.info(
                f"Mod action - Action: {action}, Moderator: {moderator.name}#{moderator.discriminator} (ID: {moderator.id}), "
                f"Target: {target.name}#{target.discriminator} (ID: {target.id}), Reason: {reason}"
            )
            
            cfg = storage.get_config(guild.id)
            log_channel_id = cfg.get("channels", {}).get("logs")
            
            if not log_channel_id:
                return
            
            log_channel = guild.get_channel(log_channel_id)
            if not log_channel:
                return
            
            action_emojis = {
                "warn": "⚠️",
                "timeout": "⏰",
                "kick": "👢",
                "ban": "🔨",
                "blacklist": "🚫",
                "unblacklist": "✅"
            }
            
            embed = discord.Embed(
                title=f"{action_emojis.get(action, '🔧')} Moderation Action",
                description=f"**Action:** {action.upper()}\n**Target:** {target.mention} ({target.id})\n**Reason:** {reason}",
                color=0xff9900 if action != "ban" else 0xff0000,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Moderator", value=f"{moderator.mention} ({moderator.id})", inline=False)
            embed.set_footer(text=f"Guild: {guild.name}")
            
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error logging mod action: {e}")

