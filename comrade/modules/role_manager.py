from interactions import (
    BaseContext,
    ComponentContext,
    Embed,
    Extension,
    OptionType,
    Permissions,
    Role,
    SlashContext,
    StringSelectMenu,
    StringSelectOption,
    component_callback,
    slash_command,
    slash_default_member_permission,
    slash_option,
)
from pymongo.errors import DuplicateKeyError

from comrade.core.bot_subclass import Comrade
from comrade.lib.text_utils import text_safe_length


class RoleManager(Extension):
    bot: Comrade

    @slash_command(
        name="rolemanager",
        description="Manage roles",
        sub_cmd_name="mark_joinable",
        sub_cmd_description="Mark a role as joinable",
        dm_permission=False,
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
        name="rolemanager",
        description="Manage roles",
        sub_cmd_name="unmark_joinable",
        sub_cmd_description="Unmark a role as joinable",
        dm_permission=False,
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
        name="rolemanager",
        description="Manage roles",
        sub_cmd_name="del_removed",
        sub_cmd_description="Deletes roles no longer in the server",
        dm_permission=False,
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

    def role_menu(self, ctx: BaseContext) -> StringSelectMenu:
        """
        Gets all joinable roles in a guild in the menu
        """
        joinable_roles = self.bot.db.roles.find({"guild_id": ctx.guild.id})

        roles = [ctx.guild.get_role(role["_id"]) for role in joinable_roles]

        options = [
            StringSelectOption(
                label=text_safe_length(role.name, 100),
                value=role.id,
                description="You already have this role. Click to leave."
                if role.id in ctx.author._role_ids
                else "Click to join",
            )
            for role in roles
        ]

        return StringSelectMenu(
            options,
            custom_id="role_manager",
            placeholder="Select a role to join/leave",
        )

    @slash_command(
        name="roles", description="List all joinable roles", dm_permission=False
    )
    async def list_roles(self, ctx: SlashContext):
        """
        List all joinable roles in a guild
        """

        joinable_roles = self.bot.db.roles.find({"guild_id": ctx.guild.id})

        roles = [ctx.guild.get_role(role["_id"]) for role in joinable_roles]

        if len(roles) == 0:
            await ctx.send(
                "There are no joinable roles in this server",
                ephemeral=True,
            )
            return

        mention_strs = [role.mention for role in roles]

        embed = Embed("Joinable Roles", "\n".join(mention_strs))

        embed.set_footer(
            text="Use the menu below to join/leave roles",
        )

        menu = self.role_menu(ctx)

        await ctx.send(embed=embed, ephemeral=True, components=[menu])

    @component_callback("role_manager")
    async def role_manager_callback(self, ctx: ComponentContext):
        """
        Callback for the role manager menu
        """

        # Get the role from the menu
        role = ctx.guild.get_role(int(ctx.values[0]))

        if role is None:
            # This should never happen
            await ctx.send(
                f"<@&{ctx.values[0]}> is not a valid role", ephemeral=True
            )

        # Ensure the role is joinable
        if self.bot.db.roles.find_one({"_id": role.id}) is None:
            # This should never happen
            await ctx.send(
                f"{role.mention} is not joinable/leaveable",
                ephemeral=True,
            )
            return

        # Ensure the user doesn't already have the role
        if role in ctx.author.roles:
            await ctx.author.remove_roles([role])
            result = f"Removed {role.mention}"
        else:
            await ctx.author.add_roles([role])
            result = f"Added {role.mention}"

        # Update the role menu, now that the user has joined/leaved a role
        await ctx.edit_origin(components=self.role_menu(ctx), content=result)


def setup(bot: Comrade):
    RoleManager(bot)
