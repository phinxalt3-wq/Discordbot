import discord
from src import storage

class TicketManager:
    @staticmethod
    async def create(interaction, title, embed, view=None):
        cfg = storage.get_config(interaction.guild_id)
        ch_id = cfg["channels"]["tickets"]

        if not ch_id:
            raise RuntimeError("Tickets channel not configured")

        channel = interaction.guild.get_channel(ch_id)

        thread = await channel.create_thread(
            name=f"ticket-{title.lower().replace(' ', '-')}-{interaction.user.name}",
            type=discord.ChannelType.private_thread,
            invitable=False
        )

        await thread.add_user(interaction.user)
        await thread.send(embed=embed, view=view)
        return thread

    @staticmethod
    async def close(interaction):
        if isinstance(interaction.channel, discord.Thread):
            await interaction.channel.edit(archived=True, locked=True)
