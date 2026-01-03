import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import uuid
from datetime import datetime
from src.utils.permissions import is_owner

class Backup(commands.Cog):
    """Channel backup and restore commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def get_backups_dir(self):
        """Get the backups directory"""
        backups_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "backups")
        os.makedirs(backups_dir, exist_ok=True)
        return backups_dir
    
    @app_commands.command(name="backupchannel", description="Backup all messages from a channel (Owner only)")
    @app_commands.describe(channel="Channel to backup")
    async def backup_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Backup all messages from a channel"""
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Generate unique backup code
        backup_code = str(uuid.uuid4())[:8].upper()
        
        # Fetch all messages
        messages_data = []
        try:
            async for message in channel.history(limit=None, oldest_first=True):
                # Skip system messages
                if message.type != discord.MessageType.default:
                    continue
                
                message_data = {
                    "id": message.id,
                    "author": {
                        "id": message.author.id,
                        "name": message.author.name,
                        "discriminator": message.author.discriminator,
                        "avatar_url": str(message.author.display_avatar.url) if message.author.display_avatar else None,
                        "bot": message.author.bot
                    },
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                    "attachments": [
                        {
                            "filename": att.filename,
                            "url": att.url,
                            "size": att.size,
                            "content_type": att.content_type
                        }
                        for att in message.attachments
                    ],
                    "embeds": [
                        {
                            "title": embed.title,
                            "description": embed.description,
                            "color": embed.color.value if embed.color else None,
                            "fields": [
                                {
                                    "name": field.name,
                                    "value": field.value,
                                    "inline": field.inline
                                }
                                for field in embed.fields
                            ],
                            "footer": embed.footer.text if embed.footer else None,
                            "image": embed.image.url if embed.image else None,
                            "thumbnail": embed.thumbnail.url if embed.thumbnail else None
                        }
                        for embed in message.embeds
                    ],
                    "reactions": [
                        {
                            "emoji": str(reaction.emoji),
                            "count": reaction.count
                        }
                        for reaction in message.reactions
                    ]
                }
                messages_data.append(message_data)
        except Exception as e:
            return await interaction.followup.send(f"❌ Error fetching messages: {str(e)}", ephemeral=True)
        
        # Save backup
        backup_data = {
            "backup_code": backup_code,
            "guild_id": channel.guild.id,
            "guild_name": channel.guild.name,
            "channel_id": channel.id,
            "channel_name": channel.name,
            "backup_timestamp": datetime.utcnow().isoformat(),
            "backed_up_by": interaction.user.id,
            "message_count": len(messages_data),
            "messages": messages_data
        }
        
        backups_dir = self.get_backups_dir()
        backup_file = os.path.join(backups_dir, f"{backup_code}.json")
        
        try:
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            return await interaction.followup.send(f"❌ Error saving backup: {str(e)}", ephemeral=True)
        
        embed = discord.Embed(
            title="✅ Channel Backed Up",
            description=f"Successfully backed up {len(messages_data)} messages from {channel.mention}",
            color=0x2ecc71
        )
        embed.add_field(name="Backup Code", value=f"`{backup_code}`", inline=False)
        embed.add_field(name="Channel", value=channel.mention, inline=True)
        embed.add_field(name="Messages", value=str(len(messages_data)), inline=True)
        embed.set_footer(text="Use /restorechannel with this code to restore the messages")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="restorechannel", description="Restore messages from a backup using webhooks (Owner only)")
    @app_commands.describe(
        backup_code="The backup code from /backupchannel",
        channel="Channel to restore messages to"
    )
    async def restore_channel(self, interaction: discord.Interaction, backup_code: str, channel: discord.TextChannel):
        """Restore messages from a backup using webhooks"""
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        # Load backup
        backups_dir = self.get_backups_dir()
        backup_file = os.path.join(backups_dir, f"{backup_code.upper()}.json")
        
        if not os.path.exists(backup_file):
            return await interaction.followup.send(f"❌ Backup code `{backup_code}` not found.", ephemeral=True)
        
        try:
            with open(backup_file, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
        except Exception as e:
            return await interaction.followup.send(f"❌ Error loading backup: {str(e)}", ephemeral=True)
        
        messages = backup_data.get("messages", [])
        if not messages:
            return await interaction.followup.send("❌ No messages found in backup.", ephemeral=True)
        
        # Create webhook for the channel
        try:
            webhook = await channel.create_webhook(name="Message Restore")
        except Exception as e:
            return await interaction.followup.send(f"❌ Error creating webhook: {str(e)}\n\nMake sure the bot has 'Manage Webhooks' permission.", ephemeral=True)
        
        restored_count = 0
        failed_count = 0
        
        # Restore messages
        for msg_data in messages:
            try:
                author_data = msg_data.get("author", {})
                author_name = author_data.get("name", "Unknown")
                author_avatar = author_data.get("avatar_url")
                
                # Prepare content
                content = msg_data.get("content", "")
                
                # Prepare embeds
                embeds = []
                for embed_data in msg_data.get("embeds", []):
                    embed = discord.Embed(
                        title=embed_data.get("title"),
                        description=embed_data.get("description"),
                        color=embed_data.get("color"),
                        timestamp=datetime.fromisoformat(msg_data.get("timestamp", datetime.utcnow().isoformat()))
                    )
                    
                    for field in embed_data.get("fields", []):
                        embed.add_field(
                            name=field.get("name", ""),
                            value=field.get("value", ""),
                            inline=field.get("inline", False)
                        )
                    
                    if embed_data.get("footer"):
                        embed.set_footer(text=embed_data.get("footer"))
                    if embed_data.get("image"):
                        embed.set_image(url=embed_data.get("image"))
                    if embed_data.get("thumbnail"):
                        embed.set_thumbnail(url=embed_data.get("thumbnail"))
                    
                    embeds.append(embed)
                
                # Send via webhook
                await webhook.send(
                    content=content if content else None,
                    embeds=embeds if embeds else None,
                    username=author_name,
                    avatar_url=author_avatar,
                    wait=True
                )
                
                restored_count += 1
                
                # Small delay to avoid rate limits
                import asyncio
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error restoring message {msg_data.get('id')}: {e}")
                failed_count += 1
                continue
        
        # Delete webhook
        try:
            await webhook.delete()
        except:
            pass
        
        embed = discord.Embed(
            title="✅ Channel Restored",
            description=f"Restored messages to {channel.mention}",
            color=0x2ecc71
        )
        embed.add_field(name="Backup Code", value=f"`{backup_code.upper()}`", inline=False)
        embed.add_field(name="Restored", value=str(restored_count), inline=True)
        if failed_count > 0:
            embed.add_field(name="Failed", value=str(failed_count), inline=True)
        embed.add_field(name="Total", value=str(len(messages)), inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Backup(bot))

