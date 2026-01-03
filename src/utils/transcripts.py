import discord
import os
import json
from datetime import datetime
from typing import List, Optional
from src import storage
from src.tickets.utils import get_ticket


class TranscriptGenerator:
    """Generate transcripts for ticket conversations"""
    
    @staticmethod
    def get_transcripts_dir(guild_id: int) -> str:
        """Get the transcripts directory for a guild"""
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "transcripts")
        guild_dir = os.path.join(base_dir, str(guild_id))
        os.makedirs(guild_dir, exist_ok=True)
        return guild_dir
    
    @staticmethod
    async def generate_transcript(channel: discord.TextChannel, ticket_data: dict = None) -> Optional[str]:
        """Generate a transcript file for a ticket channel"""
        try:
            # Get ticket data if not provided
            if not ticket_data:
                ticket_data = get_ticket(channel.guild.id, channel.id)
            
            # Create transcript content
            transcript_lines = []
            transcript_lines.append("=" * 80)
            transcript_lines.append(f"TICKET TRANSCRIPT")
            transcript_lines.append("=" * 80)
            transcript_lines.append("")
            
            # Ticket information
            if ticket_data:
                transcript_lines.append(f"Ticket Type: {ticket_data.get('ticket_type', 'Unknown').replace('_', ' ').title()}")
                transcript_lines.append(f"Ticket ID: {channel.id}")
                transcript_lines.append(f"Channel: {channel.name}")
                transcript_lines.append(f"Guild: {channel.guild.name} (ID: {channel.guild.id})")
                
                opener_id = ticket_data.get('opened_by')
                if opener_id:
                    opener = channel.guild.get_member(opener_id)
                    if opener:
                        transcript_lines.append(f"Opened By: {opener.name}#{opener.discriminator} (ID: {opener.id})")
                    else:
                        transcript_lines.append(f"Opened By: Unknown User (ID: {opener_id})")
                
                opened_at = ticket_data.get('opened_at')
                if opened_at:
                    transcript_lines.append(f"Opened At: {opened_at}")
                
                transcript_lines.append(f"Status: {'Open' if ticket_data.get('is_open', True) else 'Closed'}")
                transcript_lines.append("")
                
                # Ticket-specific details
                if 'username' in ticket_data:
                    transcript_lines.append(f"Username: {ticket_data['username']}")
                if 'ign' in ticket_data:
                    transcript_lines.append(f"IGN: {ticket_data['ign']}")
                if 'price' in ticket_data:
                    transcript_lines.append(f"Price: ${ticket_data['price']:.2f}")
                if 'total_price' in ticket_data:
                    transcript_lines.append(f"Total Price: ${ticket_data['total_price']:.2f}")
                if 'amount' in ticket_data:
                    transcript_lines.append(f"Amount: {ticket_data['amount']:.2f}M")
                if 'rank' in ticket_data:
                    transcript_lines.append(f"Rank: {ticket_data['rank']}")
                if 'count' in ticket_data:
                    transcript_lines.append(f"Count: {ticket_data['count']}")
                if 'payment_method' in ticket_data:
                    transcript_lines.append(f"Payment Method: {ticket_data['payment_method']}")
                
                transcript_lines.append("")
            
            transcript_lines.append("=" * 80)
            transcript_lines.append("CONVERSATION LOG")
            transcript_lines.append("=" * 80)
            transcript_lines.append("")
            
            # Fetch all messages
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                messages.append(message)
            
            # Format messages
            for message in messages:
                # Skip system messages
                if message.type != discord.MessageType.default:
                    continue
                
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                author = f"{message.author.name}#{message.author.discriminator}"
                
                # Message header
                transcript_lines.append(f"[{timestamp}] {author} (ID: {message.author.id})")
                
                # Message content
                if message.content:
                    transcript_lines.append(f"  {message.content}")
                
                # Attachments
                if message.attachments:
                    for attachment in message.attachments:
                        transcript_lines.append(f"  [Attachment: {attachment.filename}] {attachment.url}")
                
                # Embeds
                if message.embeds:
                    for embed in message.embeds:
                        if embed.title:
                            transcript_lines.append(f"  [Embed: {embed.title}]")
                        if embed.description:
                            transcript_lines.append(f"  {embed.description}")
                
                # Reactions
                if message.reactions:
                    reactions = []
                    for reaction in message.reactions:
                        users = [str(user) async for user in reaction.users()]
                        reactions.append(f"{reaction.emoji} ({', '.join(users[:5])}{'...' if len(users) > 5 else ''})")
                    if reactions:
                        transcript_lines.append(f"  [Reactions: {', '.join(reactions)}]")
                
                transcript_lines.append("")
            
            transcript_lines.append("=" * 80)
            transcript_lines.append(f"End of Transcript - Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            transcript_lines.append("=" * 80)
            
            # Save transcript to file
            transcript_content = "\n".join(transcript_lines)
            transcripts_dir = TranscriptGenerator.get_transcripts_dir(channel.guild.id)
            
            # Create filename with timestamp
            timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            ticket_type = ticket_data.get('ticket_type', 'unknown') if ticket_data else 'unknown'
            filename = f"{ticket_type}_{channel.id}_{timestamp_str}.txt"
            filepath = os.path.join(transcripts_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(transcript_content)
            
            return filepath
            
        except Exception as e:
            print(f"Error generating transcript: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    async def generate_html_transcript(channel: discord.TextChannel, ticket_data: dict = None) -> Optional[str]:
        """Generate an HTML transcript for a ticket channel"""
        try:
            # Get ticket data if not provided
            if not ticket_data:
                ticket_data = get_ticket(channel.guild.id, channel.id)
            
            html_parts = []
            html_parts.append("<!DOCTYPE html>")
            html_parts.append("<html>")
            html_parts.append("<head>")
            html_parts.append("<meta charset='UTF-8'>")
            html_parts.append("<title>Ticket Transcript</title>")
            html_parts.append("<style>")
            html_parts.append("""
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #2f3136;
                    color: #dcddde;
                    padding: 20px;
                    line-height: 1.6;
                }
                .header {
                    background-color: #202225;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .header h1 {
                    margin: 0;
                    color: #ffffff;
                }
                .info {
                    background-color: #36393f;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .info-item {
                    margin: 5px 0;
                }
                .message {
                    background-color: #36393f;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 5px;
                    border-left: 3px solid #5865f2;
                }
                .message-header {
                    color: #ffffff;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .message-content {
                    color: #dcddde;
                    margin-left: 10px;
                }
                .timestamp {
                    color: #72767d;
                    font-size: 0.9em;
                }
                .attachment {
                    color: #5865f2;
                    margin-left: 10px;
                }
                .embed {
                    background-color: #2f3136;
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 3px;
                    border-left: 3px solid #5865f2;
                }
            """)
            html_parts.append("</style>")
            html_parts.append("</head>")
            html_parts.append("<body>")
            
            # Header
            html_parts.append("<div class='header'>")
            html_parts.append("<h1>Ticket Transcript</h1>")
            html_parts.append("</div>")
            
            # Ticket information
            html_parts.append("<div class='info'>")
            if ticket_data:
                html_parts.append(f"<div class='info-item'><strong>Ticket Type:</strong> {ticket_data.get('ticket_type', 'Unknown').replace('_', ' ').title()}</div>")
                html_parts.append(f"<div class='info-item'><strong>Ticket ID:</strong> {channel.id}</div>")
                html_parts.append(f"<div class='info-item'><strong>Channel:</strong> {channel.name}</div>")
                html_parts.append(f"<div class='info-item'><strong>Guild:</strong> {channel.guild.name}</div>")
                
                opener_id = ticket_data.get('opened_by')
                if opener_id:
                    opener = channel.guild.get_member(opener_id)
                    if opener:
                        html_parts.append(f"<div class='info-item'><strong>Opened By:</strong> {opener.name}#{opener.discriminator}</div>")
                    else:
                        html_parts.append(f"<div class='info-item'><strong>Opened By:</strong> Unknown User (ID: {opener_id})</div>")
                
                html_parts.append(f"<div class='info-item'><strong>Status:</strong> {'Open' if ticket_data.get('is_open', True) else 'Closed'}</div>")
            html_parts.append("</div>")
            
            # Messages
            html_parts.append("<h2>Conversation Log</h2>")
            
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                messages.append(message)
            
            for message in messages:
                if message.type != discord.MessageType.default:
                    continue
                
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                author = f"{message.author.name}#{message.author.discriminator}"
                
                html_parts.append("<div class='message'>")
                html_parts.append(f"<div class='message-header'>")
                html_parts.append(f"<span class='timestamp'>{timestamp}</span> - <strong>{author}</strong>")
                html_parts.append("</div>")
                
                if message.content:
                    # Escape HTML and preserve line breaks
                    content = message.content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                    html_parts.append(f"<div class='message-content'>{content}</div>")
                
                if message.attachments:
                    for attachment in message.attachments:
                        html_parts.append(f"<div class='attachment'>📎 <a href='{attachment.url}'>{attachment.filename}</a></div>")
                
                if message.embeds:
                    for embed in message.embeds:
                        html_parts.append("<div class='embed'>")
                        if embed.title:
                            html_parts.append(f"<strong>{embed.title}</strong><br>")
                        if embed.description:
                            html_parts.append(f"{embed.description}")
                        html_parts.append("</div>")
                
                html_parts.append("</div>")
            
            html_parts.append(f"<div style='margin-top: 20px; color: #72767d; text-align: center;'>")
            html_parts.append(f"Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            html_parts.append("</div>")
            
            html_parts.append("</body>")
            html_parts.append("</html>")
            
            # Save HTML transcript
            html_content = "\n".join(html_parts)
            transcripts_dir = TranscriptGenerator.get_transcripts_dir(channel.guild.id)
            
            timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            ticket_type = ticket_data.get('ticket_type', 'unknown') if ticket_data else 'unknown'
            filename = f"{ticket_type}_{channel.id}_{timestamp_str}.html"
            filepath = os.path.join(transcripts_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            return filepath
            
        except Exception as e:
            print(f"Error generating HTML transcript: {e}")
            import traceback
            traceback.print_exc()
            return None

