import pytest
from interactions import (
    BaseContext,
    ComponentType,
    StringSelectMenu,
)

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

    await nhentai_search_cmd.callback(ctx, "alp love live english kurosawa")

    start_msg = (await ctx.channel.fetch_messages(limit=1))[0]

    assert start_msg.content == "Select a gallery to view (Page 1 / 1)"

    action_row = start_msg.components[0]

    assert action_row.type == ComponentType.ACTION_ROW

    select_menu: StringSelectMenu = action_row.components[0]
    assert select_menu.type == ComponentType.STRING_SELECT

    assert select_menu.placeholder == "Select a gallery from page 1"

    ids = [option.value for option in select_menu.options]
    assert "388445" in ids


@pytest.mark.bot
async def test_search_click(
    ctx: BaseContext, nhentai_ext: NHentai, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that we can click on a gallery from search.
    """

    with monkeypatch.context() as m:
        m.setattr(ctx, "values", ["388445"], raising=False)
        await nhentai_ext.nhentai_search_callback.callback(ctx)

    start_embed_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    assert (
        start_embed_msg.content
        == "Type `np` (or click the buttons) to start reading, and advance pages."
    )

    start_embed = start_embed_msg.embeds[0]

    assert start_embed.title == "Kurosawa no Kyuujitsu | Kurosawa's Day Off"
    assert start_embed.url == "https://nhentai.net/g/388445/"
    assert start_embed.footer.text == "Found using nhentai.to Mirror"