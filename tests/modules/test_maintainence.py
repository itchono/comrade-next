import os
import subprocess

import pytest

from comrade.core.comrade_client import Comrade
from comrade.lib.testing_utils import (
    CapturingContext,
    fake_subproc_check_output,
)
from comrade.modules.maintainence import Maintainence


@pytest.fixture(scope="module")
async def maintainence_ext(bot: Comrade) -> Maintainence:
    return bot.get_ext("Maintainence")


@pytest.mark.bot
async def test_restart(
    offline_ctx: CapturingContext,
    maintainence_ext: Maintainence,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Check that we can restart the bot
    """
    restart_cmd = maintainence_ext.restart

    stored_args = []

    with monkeypatch.context() as m:

        def mock_execv(*args, **kwargs):
            stored_args.append(args)

        async def bot_stop():
            pass

        m.setattr(os, "execv", mock_execv)
        m.setattr(subprocess, "check_output", fake_subproc_check_output)

        # IMPORTANT: PREVENT THE BOT FROM ACTUALLY STOPPING
        m.setattr(offline_ctx.bot, "stop", bot_stop)

        await restart_cmd.callback(offline_ctx)

        assert "--notify_channel" in stored_args[0][1]


@pytest.mark.bot
async def test_check_updates(
    offline_ctx: CapturingContext,
    maintainence_ext: Maintainence,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Check that we can check for updates
    """
    check_cmd = maintainence_ext.check_updates

    stored_args = []

    with monkeypatch.context() as m:

        def mock_execv(*args, **kwargs):
            stored_args.append(args)

        m.setattr(os, "execv", mock_execv)
        m.setattr(subprocess, "check_output", fake_subproc_check_output)

        await check_cmd.callback(offline_ctx)

        msg = offline_ctx.captured_message
        assert "No updates available." in msg.content


@pytest.mark.bot
async def test_install_updates(
    offline_ctx: CapturingContext,
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

        async def bot_stop():
            pass

        m.setattr(os, "execv", mock_execv)
        m.setattr(subprocess, "check_output", fake_subproc_check_output)

        # IMPORTANT: PREVENT THE BOT FROM ACTUALLY STOPPING
        m.setattr(offline_ctx.bot, "stop", bot_stop)

        await update_cmd.callback(offline_ctx)

        assert "--notify_channel" in stored_args[0][1]
