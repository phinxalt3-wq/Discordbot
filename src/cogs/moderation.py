import discord
from discord.ext import commands
from discord import app_commands
from src import storage
from src.utils.permissions import is_owner, is_staff
from src.utils.logging import BotLogger
from src.utils.rate_limit import rate_limiter
from datetime import datetime, timedelta
import asyncio

class Moderation(commands.Cog):
    """Moderation commands and abuse prevention"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def has_mod_perms(self, interaction: discord.Interaction) -> bool:
        """Check if user has moderation permissions"""
        return is_owner(interaction) or is_staff(interaction) or interaction.user.guild_permissions.manage_messages
    
    @app_commands.command(name="warn", description="Warn a user (Staff only)")
    @app_commands.describe(
        user="User to warn",
        reason="Reason for the warning"
    )
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        """Warn a user"""
        if not self.has_mod_perms(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        if user.bot:
            return await interaction.response.send_message("❌ You cannot warn bots.", ephemeral=True)
        
        await interaction.response.defer()
        
        # Record warning
        storage.add_warning(interaction.guild_id, user.id, interaction.user.id, reason)
        warning_count = storage.get_warning_count(interaction.guild_id, user.id)
        
        # Try to DM user
        try:
            dm_embed = discord.Embed(
                title="⚠️ Warning",
                description=f"You have been warned in **{interaction.guild.name}**",
                color=0xff9900,
                timestamp=datetime.utcnow()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Total Warnings", value=str(warning_count), inline=False)
            dm_embed.set_footer(text=f"Warned by {interaction.user.name}")
            await user.send(embed=dm_embed)
        except:
            pass  # User has DMs disabled
        
        # Send confirmation
        embed = discord.Embed(
            title="⚠️ User Warned",
            description=f"{user.mention} has been warned.",
            color=0xff9900,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Total Warnings", value=str(warning_count), inline=True)
        embed.set_footer(text=f"Warned by {interaction.user.name}")
        
        await interaction.followup.send(embed=embed)
        
        # Log warning
        await BotLogger.log_mod_action(interaction.guild, interaction.user, "warn", user, reason)
    
    @app_commands.command(name="warnings", description="View warnings for a user (Staff only)")
    @app_commands.describe(user="User to check warnings for")
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        """View warnings for a user"""
        if not self.has_mod_perms(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        warnings = storage.get_warnings(interaction.guild_id, user.id)
        warning_count = len(warnings)
        
        if warning_count == 0:
            return await interaction.followup.send(f"✅ {user.mention} has no warnings.", ephemeral=True)
        
        embed = discord.Embed(
            title=f"Warnings for {user.name}",
            description=f"Total: **{warning_count}**",
            color=0xff9900,
            timestamp=datetime.utcnow()
        )
        
        # Show last 10 warnings
        for i, warning in enumerate(warnings[-10:], start=1):
            warned_by = interaction.guild.get_member(warning.get('warned_by_id'))
            warned_by_name = warned_by.name if warned_by else "Unknown"
            timestamp = warning.get('timestamp', 'Unknown')
            embed.add_field(
                name=f"Warning #{warning_count - len(warnings) + i}",
                value=f"**Reason:** {warning.get('reason', 'No reason')}\n**By:** {warned_by_name}\n**Date:** {timestamp}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="timeout", description="Timeout a user (Staff only)")
    @app_commands.describe(
        user="User to timeout",
        duration="Duration in minutes (1-40320)",
        reason="Reason for the timeout"
    )
    async def timeout(
        self, 
        interaction: discord.Interaction, 
        user: discord.Member, 
        duration: app_commands.Range[int, 1, 40320],
        reason: str = "No reason provided"
    ):
        """Timeout a user"""
        if not self.has_mod_perms(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        if user.bot:
            return await interaction.response.send_message("❌ You cannot timeout bots.", ephemeral=True)
        
        if user.top_role >= interaction.user.top_role and not is_owner(interaction):
            return await interaction.response.send_message("❌ You cannot timeout users with equal or higher roles.", ephemeral=True)
        
        await interaction.response.defer()
        
        timeout_until = datetime.utcnow() + timedelta(minutes=duration)
        
        try:
            await user.timeout(timeout_until, reason=reason)
            
            embed = discord.Embed(
                title="⏰ User Timed Out",
                description=f"{user.mention} has been timed out for {duration} minutes.",
                color=0xff9900,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Timed out by {interaction.user.name}")
            
            await interaction.followup.send(embed=embed)
            await BotLogger.log_mod_action(interaction.guild, interaction.user, "timeout", user, reason)
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to timeout this user.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error timing out user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="kick", description="Kick a user from the server (Staff only)")
    @app_commands.describe(
        user="User to kick",
        reason="Reason for the kick"
    )
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Kick a user"""
        if not self.has_mod_perms(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        if user.bot:
            return await interaction.response.send_message("❌ You cannot kick bots.", ephemeral=True)
        
        if user.top_role >= interaction.user.top_role and not is_owner(interaction):
            return await interaction.response.send_message("❌ You cannot kick users with equal or higher roles.", ephemeral=True)
        
        await interaction.response.defer()
        
        try:
            await user.kick(reason=reason)
            
            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"{user.mention} has been kicked from the server.",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Kicked by {interaction.user.name}")
            
            await interaction.followup.send(embed=embed)
            await BotLogger.log_mod_action(interaction.guild, interaction.user, "kick", user, reason)
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to kick this user.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error kicking user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="ban", description="Ban a user from the server (Staff only)")
    @app_commands.describe(
        user="User to ban",
        reason="Reason for the ban",
        delete_days="Days of messages to delete (0-7)"
    )
    async def ban(
        self, 
        interaction: discord.Interaction, 
        user: discord.Member, 
        reason: str = "No reason provided",
        delete_days: app_commands.Range[int, 0, 7] = 0
    ):
        """Ban a user"""
        if not self.has_mod_perms(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        if user.bot:
            return await interaction.response.send_message("❌ You cannot ban bots.", ephemeral=True)
        
        if user.top_role >= interaction.user.top_role and not is_owner(interaction):
            return await interaction.response.send_message("❌ You cannot ban users with equal or higher roles.", ephemeral=True)
        
        await interaction.response.defer()
        
        # Add to blacklist
        storage.add_to_blacklist(interaction.guild_id, user.id, reason)
        
        try:
            await user.ban(reason=reason, delete_message_days=delete_days)
            
            embed = discord.Embed(
                title="🔨 User Banned",
                description=f"{user.mention} has been banned from the server.",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Messages Deleted", value=f"{delete_days} days", inline=True)
            embed.set_footer(text=f"Banned by {interaction.user.name}")
            
            await interaction.followup.send(embed=embed)
            await BotLogger.log_mod_action(interaction.guild, interaction.user, "ban", user, reason)
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to ban this user.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error banning user: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="blacklist", description="Blacklist a user from using the bot (Owner only)")
    @app_commands.describe(
        user="User to blacklist",
        reason="Reason for blacklist"
    )
    async def blacklist(self, interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
        """Blacklist a user from using the bot"""
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        await interaction.response.defer()
        
        storage.add_to_blacklist(interaction.guild_id, user.id, reason)
        
        embed = discord.Embed(
            title="🚫 User Blacklisted",
            description=f"{user.mention} has been blacklisted from using the bot.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Blacklisted by {interaction.user.name}")
        
        await interaction.followup.send(embed=embed)
        await BotLogger.log_mod_action(interaction.guild, interaction.user, "blacklist", user, reason)
    
    @app_commands.command(name="unblacklist", description="Remove a user from blacklist (Owner only)")
    @app_commands.describe(user="User to unblacklist")
    async def unblacklist(self, interaction: discord.Interaction, user: discord.User):
        """Remove a user from blacklist"""
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        await interaction.response.defer()
        
        if storage.remove_from_blacklist(interaction.guild_id, user.id):
            embed = discord.Embed(
                title="✅ User Unblacklisted",
                description=f"{user.mention} has been removed from the blacklist.",
                color=0x2ecc71,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"Unblacklisted by {interaction.user.name}")
            await interaction.followup.send(embed=embed)
            await BotLogger.log_mod_action(interaction.guild, interaction.user, "unblacklist", user, "Removed from blacklist")
        else:
            await interaction.followup.send(f"❌ {user.mention} is not blacklisted.", ephemeral=True)
    
    @app_commands.command(name="reset_ratelimit", description="Reset rate limit for a user (Owner only)")
    @app_commands.describe(user="User to reset rate limit for")
    async def reset_ratelimit(self, interaction: discord.Interaction, user: discord.User):
        """Reset rate limit for a user"""
        if not is_owner(interaction):
            return await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        
        rate_limiter.reset_user(user.id)
        await interaction.response.send_message(f"✅ Rate limit reset for {user.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))

