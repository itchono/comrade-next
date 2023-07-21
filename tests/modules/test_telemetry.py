import pytest

from comrade.lib.testing_utils import CapturingContext
from comrade.modules.telemetry import Telemetry


@pytest.fixture(scope="module")
async def telemetry_ext(bot) -> Telemetry:
    return bot.get_ext("Telemetry")


@pytest.mark.bot
async def test_status_cmd(
    offline_ctx: CapturingContext, telemetry_ext: Telemetry
):
    await telemetry_ext.status.callback(offline_ctx)
    embed_msg = offline_ctx.captured_message

    # Ensure status embed is sent
    assert embed_msg.embeds[0].title == "Bot Status"


@pytest.mark.bot
async def test_log_cmd_full(
    offline_ctx: CapturingContext, telemetry_ext: Telemetry
):
    """
    Test the bot sending a log file with the full log

    Expected Results
    ----------------
    - The bot sends a message with the log file attached

    Notes
    -----
    - Requires use of the `offline_ctx` fixture
      due to the bot sending attachments
    """
    await telemetry_ext.log.callback(offline_ctx)
    log_msg = offline_ctx.captured_message

    # Ensure log file is sent
    assert log_msg.attachments[0].filename == "comrade_log.txt"


@pytest.mark.bot
async def test_log_cmd_n_lines(
    offline_ctx: CapturingContext, telemetry_ext: Telemetry
):
    await telemetry_ext.log.callback(offline_ctx, 30)
    log_msg = offline_ctx.captured_message

    # Ensure log file is sent
    assert log_msg.attachments[0].filename == "comrade_log.txt"
