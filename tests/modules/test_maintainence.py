import os

import pytest
from interactions import BaseContext

from comrade.core.bot_subclass import Comrade
from comrade.modules.maintainence import Maintainence


@pytest.fixture(scope="module")
async def maintainence_ext(bot: Comrade) -> Maintainence:
    return bot.get_ext("Maintainence")


@pytest.mark.skip("Pending being able to run github")
async def test_update(
    ctx: BaseContext,
    maintainence_ext: Maintainence,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Check that we can update the bot
    """
    update_cmd = maintainence_ext.install_updates

    stored_args = []

    with monkeypatch.context() as m:

        def mock_execv(*args, **kwargs):
            stored_args.append(args)

        m.setattr(os, "execv", mock_execv)

        await update_cmd.callback(ctx)

        assert "--notify_channel" in stored_args[0][1]
