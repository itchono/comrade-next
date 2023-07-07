import re

import pytest
from interactions import BaseContext, Button, ComponentType, StringSelectMenu

from comrade.core.bot_subclass import Comrade
from comrade.modules.nhentai_cmds import NHentai


@pytest.fixture(scope="module")
async def nhentai_ext(bot: Comrade) -> NHentai:
    return bot.get_ext("NHentai")


@pytest.mark.bot
async def test_search_start(ctx: BaseContext, nhentai_ext: NHentai):
    """
    Make sure that we can find a gallery from search.

    This test may break if the gallery is removed from nhentai,
    or if more galleries are added to nhentai with the same tags.
    (gallery gets pushed to next page)
    """
    nhentai_search_cmd = nhentai_ext.nhentai_search

    await nhentai_search_cmd.callback(ctx, "alp love live")

    start_msg = (await ctx.channel.fetch_messages(limit=1))[0]

    assert start_msg.content == "Select a gallery to view (Page 1 / 8)"

    action_row = start_msg.components[0]

    assert action_row.type == ComponentType.ACTION_ROW

    select_menu: StringSelectMenu = action_row.components[0]
    assert select_menu.type == ComponentType.STRING_SELECT

    assert select_menu.placeholder == "Select a gallery from page 1"


@pytest.mark.bot
async def test_search_next_page(
    ctx: BaseContext, nhentai_ext: NHentai, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that we can advance to the next page of search results.

    We need to do some low-level bot hacking to get the event dispatcher
    to call the callback directly.
    """
    menu_msg_old = (await ctx.channel.fetch_messages(limit=1))[0]
    action_row = menu_msg_old.components[1]
    page_2_button: Button = action_row.components[1]

    assert page_2_button.type == ComponentType.BUTTON

    uuid = page_2_button.custom_id.split("|")[0]
    callback_key = re.compile(f"^{uuid}\|(\d+)$")

    # Determine the callback to call
    callback = ctx.bot._regex_component_callbacks[callback_key]

    # Do some wizardry to get the callback to edit the message
    async def edit_message_patch(*args, **kwargs):
        await menu_msg_old.edit(*args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(ctx, "custom_id", page_2_button.custom_id, raising=False)
        m.setattr(ctx, "edit_origin", edit_message_patch, raising=False)
        await callback(ctx)

    menu_msg = (await ctx.channel.fetch_messages(limit=1))[0]

    assert menu_msg.content == "Select a gallery to view (Page 2 / 8)"


@pytest.mark.bot
async def test_search_last_page(
    ctx: BaseContext, nhentai_ext: NHentai, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that we can advance to the last page of search results.

    We need to do some low-level bot hacking to get the event dispatcher
    to call the callback directly.
    """
    menu_msg_old = (await ctx.channel.fetch_messages(limit=1))[0]
    action_row = menu_msg_old.components[1]
    last_page_button: Button = action_row.components[-1]

    assert last_page_button.type == ComponentType.BUTTON

    uuid = last_page_button.custom_id.split("|")[0]
    callback_key = re.compile(f"^{uuid}\|(\d+)$")

    # Determine the callback to call
    callback = ctx.bot._regex_component_callbacks[callback_key]

    # Do some wizardry to get the callback to edit the message
    async def edit_message_patch(*args, **kwargs):
        await menu_msg_old.edit(*args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(ctx, "custom_id", last_page_button.custom_id, raising=False)
        m.setattr(ctx, "edit_origin", edit_message_patch, raising=False)
        await callback(ctx)

    menu_msg = (await ctx.channel.fetch_messages(limit=1))[0]

    assert menu_msg.content == "Select a gallery to view (Page 8 / 8)"


@pytest.mark.bot
async def test_same_page(
    ctx: BaseContext, nhentai_ext: NHentai, monkeypatch: pytest.MonkeyPatch
):
    """
    (Impossible) case where we try to go to the same page.

    The bot should handle this gracefully, and print a message
    """
    menu_msg_old = (await ctx.channel.fetch_messages(limit=1))[0]
    action_row = menu_msg_old.components[1]
    last_page_button: Button = action_row.components[-1]

    assert last_page_button.type == ComponentType.BUTTON
    assert last_page_button.disabled

    uuid = last_page_button.custom_id.split("|")[0]
    callback_key = re.compile(f"^{uuid}\|(\d+)$")

    # Determine the callback to call
    callback = ctx.bot._regex_component_callbacks[callback_key]

    # Do some wizardry to get the callback to edit the message
    async def edit_message_patch(*args, **kwargs):
        await menu_msg_old.edit(*args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(ctx, "custom_id", last_page_button.custom_id, raising=False)
        m.setattr(ctx, "edit_origin", edit_message_patch, raising=False)
        await callback(ctx)

    menu_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    assert menu_msg.content == "You're already on that page!"
