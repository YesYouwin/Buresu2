
from discord import app_commands

def is_staff():
    async def predicate(interaction: app_commands.Interaction):
        allowed_roles = [
            1447053023305269288,
            1446594998920417350,
            1435989883930804366,
            1441838078493986998
        ]
        if any(role.id in allowed_roles for role in interaction.user.roles):
            return True
        if interaction.user.guild_permissions.administrator:
            return True
        return False
    return app_commands.check(predicate)
