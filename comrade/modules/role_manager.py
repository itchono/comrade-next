from interactions import (
    Embed,
    Extension,
    OptionType,
    Permissions,
    Role,
    SlashContext,
    slash_command,
    slash_default_member_permission,
    slash_option,
)
from pymongo.errors import DuplicateKeyError

from comrade.core.bot_subclass import Comrade


class RoleManager(Extension):
    bot: Comrade

    @slash_command(
        name="role_manage",
        description="Manage roles",
        sub_cmd_name="mark_joinable",
        sub_cmd_description="Mark a role as joinable",
    )
    @slash_option(
        name="role",
        description="The role to mark as joinable",
        opt_type=OptionType.ROLE,
        required=True,
    )
    @slash_default_member_permission(Permissions.MANAGE_ROLES)
    async def mark_joinable(self, ctx: SlashContext, role: Role):
        """
        Mark a role as joinable

        Inserts a role into the database, storing othe role's ID,
        as well as the ID of the guild the role is in.
        (this is done to search for the role in the database)
        """
        try:
            insertion_result = self.bot.db.roles.insert_one(
                {
                    "_id": role.id,
                    "guild_id": ctx.guild.id,
                }
            )
        except DuplicateKeyError:
            await ctx.send(
                f"{role.mention} is already joinable", ephemeral=True
            )
            return

        if insertion_result.acknowledged:
            await ctx.send(f"Marked {role.mention} as joinable", ephemeral=True)
        else:
            await ctx.send(
                f"Failed to mark {role.mention} as joinable (database error)",
                ephemeral=True,
            )

    @slash_command(
        name="role_manage",
        description="Manage roles",
        sub_cmd_name="unmark_joinable",
        sub_cmd_description="Unmark a role as joinable",
    )
    @slash_option(
        name="role",
        description="The role to unmark as joinable",
        opt_type=OptionType.ROLE,
        required=True,
    )
    @slash_default_member_permission(Permissions.MANAGE_ROLES)
    async def unmark_joinable(self, ctx: SlashContext, role: Role):
        """
        Unmarks a role as joinable

        Removes a role from the database.

        If the role is not in the database, this command will notifiy the user.
        """

        deletion_result = self.bot.db.roles.delete_one({"_id": role.id})

        if deletion_result.acknowledged and deletion_result.deleted_count == 1:
            await ctx.send(
                f"Unmarked {role.mention} as joinable", ephemeral=True
            )
        elif deletion_result.deleted_count == 0:
            await ctx.send(f"{role.mention} is not joinable", ephemeral=True)
        else:
            await ctx.send(
                f"Failed to unmark {role.mention} as joinable (database error)",
                ephemeral=True,
            )

    @slash_command(
        name="role_manage",
        description="Manage roles",
        sub_cmd_name="del_removed_roles",
        sub_cmd_description="Deletes roles no longer in the server",
    )
    @slash_default_member_permission(Permissions.MANAGE_ROLES)
    async def del_removed_roles(self, ctx: SlashContext):
        """
        Deletes roles no longer in the server

        Used if a role is deleted from the server, but not from the database.
        """
        # Get all roles in the database
        db_roles = self.bot.db.roles.find({"guild_id": ctx.guild.id})
        db_role_ids = set([db_role["_id"] for db_role in db_roles])

        # Get all roles in the server
        server_roles = ctx.guild.roles
        server_roles_ids = set([server_role.id for server_role in server_roles])

        # Get the difference between the two sets
        removed_roles = db_role_ids - server_roles_ids

        if len(removed_roles) == 0:
            await ctx.send("No roles to delete", ephemeral=True)
            return

        # Delete the removed roles from the database
        deletion_result = self.bot.db.roles.delete_many(
            {"_id": {"$in": list(removed_roles)}}
        )
        await ctx.send(
            f"Deleted {deletion_result.deleted_count} removed roles",
            ephemeral=True,
        )

    @slash_command(
        name="role",
        description="Manage roles",
        sub_cmd_name="join",
        sub_cmd_description="Join a role in the server",
    )
    @slash_option(
        name="role",
        description="The role to join",
        opt_type=OptionType.ROLE,
        required=True,
    )
    async def join_role(self, ctx: SlashContext, role: Role):
        """
        Join a role in the server

        Adds a role to the user's roles.
        """

        # Ensure the role is joinable
        if self.bot.db.roles.find_one({"_id": role.id}) is None:
            await ctx.send(
                f"{role.mention} is not joinable, "
                "run `/roles list` for a list of joinable roles.",
                ephemeral=True,
            )
            return

        # Ensure the user doesn't already have the role
        if role in ctx.author.roles:
            await ctx.send(f"You already have {role.mention}", ephemeral=True)
            return

        # Add the role to the user
        await ctx.author.add_roles([role])
        await ctx.send(f"Added {role.mention}", ephemeral=True)

    @slash_command(
        name="role",
        description="Manage roles",
        sub_cmd_name="leave",
        sub_cmd_description="Leave a role in the server",
    )
    @slash_option(
        name="role",
        description="The role to leave",
        opt_type=OptionType.ROLE,
        required=True,
    )
    async def leave_role(self, ctx: SlashContext, role: Role):
        """
        Leave a role in the server

        Removes a role from the user's roles.
        """

        # Ensure the role is joinable
        if self.bot.db.roles.find_one({"_id": role.id}) is None:
            await ctx.send(
                f"{role.mention} is not leaveable",
                "run `/roles list` for a list of joinable/leaveable roles.",
                ephemeral=True,
            )
            return

        # Ensure the user has the role
        if role not in ctx.author.roles:
            await ctx.send(f"You don't have {role.mention}", ephemeral=True)
            return

        # Remove the role from the user
        await ctx.author.remove_roles([role])
        await ctx.send(f"Removed {role.mention}", ephemeral=True)

    @slash_command(
        name="role",
        description="Manage roles",
        sub_cmd_name="list",
        sub_cmd_description="List all joinable roles",
    )
    async def list_roles(self, ctx: SlashContext):
        """
        List all joinable roles in a guild
        """

        joinable_roles = self.bot.db.roles.find({"guild_id": ctx.guild.id})

        mention_strs = [f"<@&{role['_id']}>" for role in joinable_roles]

        embed = Embed("Joinable Roles", "\n".join(mention_strs))

        embed.set_footer(
            text="Use /role join to join a role, and /role leave to leave a role"
        )

        await ctx.send(embed=embed, ephemeral=True)


def setup(bot: Comrade):
    RoleManager(bot)
