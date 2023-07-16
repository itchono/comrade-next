import pytest
from interactions import BaseContext

from comrade.core.comrade_client import Comrade
from comrade.lib.testing_utils import (
    fetch_latest_message,
)
from comrade.modules.helpful_converters import HelpfulConverters


@pytest.fixture(scope="module")
async def converters_ext(bot: Comrade) -> HelpfulConverters:
    return bot.get_ext("HelpfulConverters")


@pytest.mark.bot
async def test_tenor_nominal(
    ctx: BaseContext,
    converters_ext: HelpfulConverters,
    monkeypatch: pytest.MonkeyPatch,
):
    tenor_msg = await ctx.send(
        "https://tenor.com/view/kotori-kotori-itsuka-itsuka-kotori-gif-23001734"
    )

    context_cmd = converters_ext.convert_to_gif_url

    with monkeypatch.context() as m:
        m.setattr(ctx, "target", tenor_msg, raising=False)

        await context_cmd.callback(ctx)

    gif_msg = await fetch_latest_message(ctx)

    assert (
        gif_msg.embeds[0].description
        == "`https://media.tenor.com/Xlyaw4BYs0AAAAAC/kotori-kotori-itsuka.gif`"
    )


@pytest.mark.bot
async def test_tenor_invalid(
    ctx: BaseContext,
    converters_ext: HelpfulConverters,
    monkeypatch: pytest.MonkeyPatch,
):
    tenor_msg = await ctx.send("not-a-tenor-link")

    context_cmd = converters_ext.convert_to_gif_url

    with monkeypatch.context() as m:
        m.setattr(ctx, "target", tenor_msg, raising=False)

        await context_cmd.callback(ctx)

    msg = await fetch_latest_message(ctx)

    assert "There is no Tenor link in this message." in msg.content
