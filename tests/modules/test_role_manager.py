import pytest
from interactions import BaseContext, ComponentType, Role

from comrade.core.bot_subclass import Comrade
from comrade.lib.testing_utils import fetch_latest_message
from comrade.modules.role_manager import RoleManager


@pytest.fixture(scope="module")
async def rolemanager_ext(bot: Comrade) -> RoleManager:
    # Drop roles before we start
    bot.db.roles.drop()
    return bot.get_ext("RoleManager")


@pytest.fixture(scope="module")
async def temp_role(ctx: BaseContext) -> Role:
    role = await ctx.guild.create_role(name="rolemanager test")

    yield role

    await role.delete()


@pytest.mark.bot
async def test_nothing_joinable(ctx: BaseContext, rolemanager_ext: RoleManager):
    """
    Check that /roles returns nothing
    """

    roles_cmd = rolemanager_ext.list_roles

    await roles_cmd.callback(ctx)

    msg = await fetch_latest_message(ctx)

    assert msg.content == "There are no joinable roles in this server"


@pytest.mark.bot
async def test_mark_joinable(
    ctx: BaseContext, rolemanager_ext: RoleManager, temp_role: Role
):
    """
    Check that we can mark a role as joinable
    """

    mark_joinable_cmd = rolemanager_ext.mark_joinable
    await mark_joinable_cmd.callback(ctx, temp_role)

    msg = await fetch_latest_message(ctx)

    assert "as joinable" in msg.content


@pytest.mark.bot
async def test_cannot_double_mark(
    ctx: BaseContext, rolemanager_ext: RoleManager, temp_role: Role
):
    """
    Check that we cannot mark a role as joinable twice
    """
    mark_joinable_cmd = rolemanager_ext.mark_joinable
    await mark_joinable_cmd.callback(ctx, temp_role)

    msg = await fetch_latest_message(ctx)

    assert "is already joinable" in msg.content


@pytest.mark.bot
async def test_unmark_joinable(
    ctx: BaseContext, rolemanager_ext: RoleManager, temp_role: Role
):
    """
    Check that we can unmark a role as joinable
    """
    unmark_joinable_cmd = rolemanager_ext.unmark_joinable
    await unmark_joinable_cmd.callback(ctx, temp_role)

    msg = await fetch_latest_message(ctx)

    assert "as joinable" in msg.content


@pytest.mark.bot
async def test_cannot_unmark_nonexistent(
    ctx: BaseContext, rolemanager_ext: RoleManager, temp_role: Role
):
    """
    Check that we cannot unmark a role that is not marked as joinable
    """
    unmark_joinable_cmd = rolemanager_ext.unmark_joinable
    await unmark_joinable_cmd.callback(ctx, temp_role)

    msg = await fetch_latest_message(ctx)

    assert "is not joinable" in msg.content


@pytest.mark.bot
async def test_del_removed_roles_no_op(
    ctx: BaseContext, rolemanager_ext: RoleManager
):
    # first, check that no roles need to be deleted
    await rolemanager_ext.del_removed_roles.callback(ctx)
    msg = await fetch_latest_message(ctx)

    assert msg.content == "No roles to delete"


@pytest.mark.bot
async def test_del_removed_roles_nominal(
    ctx: BaseContext, rolemanager_ext: RoleManager
):
    temp_role_2 = await ctx.guild.create_role(name="rolemanager test 2")

    # Mark a role as joinable, delete it, and check that it is deleted
    mark_joinable_cmd = rolemanager_ext.mark_joinable
    await mark_joinable_cmd.callback(ctx, temp_role_2)

    await temp_role_2.delete()

    await rolemanager_ext.del_removed_roles.callback(ctx)

    msg = await fetch_latest_message(ctx)

    assert "removed roles" in msg.content


@pytest.mark.bot
async def test_role_menu(
    ctx: BaseContext, rolemanager_ext: RoleManager, temp_role: Role
):
    """
    Check that /roles returns a menu now
    """
    mark_joinable_cmd = rolemanager_ext.mark_joinable
    await mark_joinable_cmd.callback(ctx, temp_role)

    roles_cmd = rolemanager_ext.list_roles

    await roles_cmd.callback(ctx)

    msg = await fetch_latest_message(ctx)

    assert msg.components[0].type == ComponentType.ACTION_ROW
    assert msg.components[0].components[0].type == ComponentType.STRING_SELECT


# TODO: clicking on menu
