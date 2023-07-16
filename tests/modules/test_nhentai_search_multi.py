import re

import pytest
from interactions import Button, ComponentType, StringSelectMenu

from comrade.core.comrade_client import Comrade
from comrade.lib.nhentai.structures import NHentaiSortOrder
from comrade.lib.testing_utils import CapturingContext
from comrade.modules.nhentai_cmds import NHentai


@pytest.fixture(scope="module")
async def nhentai_ext(bot: Comrade) -> NHentai:
    return bot.get_ext("NHentai")


@pytest.mark.bot
async def test_search_start(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    """
    Make sure that we can find a gallery from search.

    This test may break if the gallery is removed from nhentai,
    or if more galleries are added to nhentai with the same tags.
    (gallery gets pushed to next page)
    """
    nhentai_search_cmd = nhentai_ext.nhentai_search

    await nhentai_search_cmd.callback(
        capturing_ctx, "alp love live", NHentaiSortOrder.POPULAR_ALL_TIME
    )

    start_msg = capturing_ctx.testing_captured_message

    assert start_msg.content == "Select a gallery to view (Page 1 / 8)"

    action_row = start_msg.components[0]

    assert action_row.type == ComponentType.ACTION_ROW

    select_menu: StringSelectMenu = action_row.components[0]
    assert select_menu.type == ComponentType.STRING_SELECT

    assert select_menu.placeholder == "Select a gallery from page 1"


@pytest.mark.bot
async def test_search_next_page(
    capturing_ctx: CapturingContext,
    nhentai_ext: NHentai,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Test that we can advance to the next page of search results.

    We need to do some low-level bot hacking to get the event dispatcher
    to call the callback directly.
    """
    menu_msg_old = capturing_ctx.testing_captured_message
    action_row = menu_msg_old.components[1]
    page_2_button: Button = action_row.components[1]

    assert page_2_button.type == ComponentType.BUTTON

    uuid = page_2_button.custom_id.split("|")[0]
    callback_key = re.compile(f"^{uuid}\|(\d+)$")

    # Determine the callback to call
    callback = capturing_ctx.bot._regex_component_callbacks[callback_key]

    # Do some wizardry to get the callback to edit the message
    async def edit_message_patch(*args, **kwargs):
        await menu_msg_old.edit(*args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(
            capturing_ctx, "custom_id", page_2_button.custom_id, raising=False
        )
        m.setattr(
            capturing_ctx, "edit_origin", edit_message_patch, raising=False
        )
        await callback(capturing_ctx)

    menu_msg = capturing_ctx.testing_captured_message

    assert menu_msg.content == "Select a gallery to view (Page 2 / 8)"


@pytest.mark.bot
async def test_search_last_page(
    capturing_ctx: CapturingContext,
    nhentai_ext: NHentai,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Test that we can advance to the last page of search results.

    We need to do some low-level bot hacking to get the event dispatcher
    to call the callback directly.
    """
    menu_msg_old = capturing_ctx.testing_captured_message
    action_row = menu_msg_old.components[1]
    last_page_button: Button = action_row.components[-1]

    assert last_page_button.type == ComponentType.BUTTON

    uuid = last_page_button.custom_id.split("|")[0]
    callback_key = re.compile(f"^{uuid}\|(\d+)$")

    # Determine the callback to call
    callback = capturing_ctx.bot._regex_component_callbacks[callback_key]

    # Do some wizardry to get the callback to edit the message
    async def edit_message_patch(*args, **kwargs):
        await menu_msg_old.edit(*args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(
            capturing_ctx,
            "custom_id",
            last_page_button.custom_id,
            raising=False,
        )
        m.setattr(
            capturing_ctx, "edit_origin", edit_message_patch, raising=False
        )
        await callback(capturing_ctx)

    menu_msg = capturing_ctx.testing_captured_message

    assert menu_msg.content == "Select a gallery to view (Page 8 / 8)"


@pytest.mark.bot
async def test_same_page(
    capturing_ctx: CapturingContext,
    nhentai_ext: NHentai,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    (Impossible) case where we try to go to the same page.

    The bot should handle this gracefully, and print a message
    """
    menu_msg_old = capturing_ctx.testing_captured_message
    action_row = menu_msg_old.components[1]
    last_page_button: Button = action_row.components[-1]

    assert last_page_button.type == ComponentType.BUTTON
    assert last_page_button.disabled

    uuid = last_page_button.custom_id.split("|")[0]
    callback_key = re.compile(f"^{uuid}\|(\d+)$")

    # Determine the callback to call
    callback = capturing_ctx.bot._regex_component_callbacks[callback_key]

    # Do some wizardry to get the callback to edit the message
    async def edit_message_patch(*args, **kwargs):
        await menu_msg_old.edit(*args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(
            capturing_ctx,
            "custom_id",
            last_page_button.custom_id,
            raising=False,
        )
        m.setattr(
            capturing_ctx, "edit_origin", edit_message_patch, raising=False
        )
        await callback(capturing_ctx)

    menu_msg = capturing_ctx.testing_captured_message
    assert menu_msg.content == "You're already on that page!"
