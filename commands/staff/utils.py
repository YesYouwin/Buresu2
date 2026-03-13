import discord
from discord import app_commands

def is_staff():
    async def predicate(interaction: discord.Interaction) -> bool:
        allowed_roles = [
            1447053023305269288,
            1446594998920417350,
            1435989883930804366,
            1441838078493986998
        ]

        if not interaction.guild:
            return False

        member = interaction.guild.get_member(interaction.user.id)

        if member is None:
            return False

        if any(role.id in allowed_roles for role in member.roles):
            return True

        if member.guild_permissions.administrator:
            return True

        raise app_commands.CheckFailure("You are not allowed to use this command.")

    return app_commands.check(predicate)
