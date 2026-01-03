import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
import asyncio
import time

class Utility(commands.Cog):
    """Utility commands for users and server management"""
    
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="timer", description="Set a timer for a specific duration")
    @app_commands.describe(
        minutes="Duration in minutes",
        reason="Reason for the timer (optional)"
    )
    async def timer(self, interaction: discord.Interaction, minutes: int, reason: str = None):
        """Set a timer"""
        if minutes <= 0:
            return await interaction.response.send_message("❌ Time must be greater than 0 minutes.", ephemeral=True)
        if minutes > 1440: # 24 hours
            return await interaction.response.send_message("❌ Timer cannot be longer than 24 hours.", ephemeral=True)

        end_time = int(time.time() + (minutes * 60))
        reason_text = f"\n**Reason:** {reason}" if reason else ""
        
        embed = discord.Embed(
            title="⏱️ Timer Set",
            description=f"Timer set for **{minutes} minutes**.\nEnds <t:{end_time}:R>{reason_text}",
            color=0x3498db
        )
        await interaction.response.send_message(embed=embed)
        
        await asyncio.sleep(minutes * 60)
        
        notify_embed = discord.Embed(
            title="⏰ Timer Ended!",
            description=f"{interaction.user.mention}, your timer for **{minutes} minutes** has ended!{reason_text}",
            color=0xe74c3c
        )
        try:
            await interaction.followup.send(content=interaction.user.mention, embed=notify_embed)
        except:
            # Fallback if original interaction token expired (unlikely for short timers but possible)
             if interaction.channel:
                await interaction.channel.send(content=interaction.user.mention, embed=notify_embed)

    @app_commands.command(name="avatar", description="View a user's avatar")
    @app_commands.describe(user="The user to view (default: yourself)")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        """View a user's avatar"""
        user = user or interaction.user
        
        embed = discord.Embed(
            title=f"Avatar for {user.display_name}",
            color=user.color
        )
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Get information about a user")
    @app_commands.describe(user="The user to check (default: yourself)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        """Get user information"""
        user = user or interaction.user
        
        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        roles.reverse()
        roles_str = ", ".join(roles) if roles else "None"
        
        embed = discord.Embed(title="User Information", color=user.color)
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(name="User", value=f"{user.mention}\n`{user.id}`", inline=True)
        embed.add_field(name="Joined Server", value=f"<t:{int(user.joined_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Account Created", value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name=f"Roles [{len(roles)}]", value=roles_str if len(roles_str) < 1024 else f"{len(roles)} roles", inline=False)
        
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Get information about this server")
    async def serverinfo(self, interaction: discord.Interaction):
        """Get server information"""
        guild = interaction.guild
        
        embed = discord.Embed(title=f"{guild.name} Info", color=0x3498db)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Channels", value=f"📝 {len(guild.text_channels)} | 🔊 {len(guild.voice_channels)}", inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Boosts", value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} boosts)", inline=True)
        
        embed.set_footer(text=f"ID: {guild.id}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
