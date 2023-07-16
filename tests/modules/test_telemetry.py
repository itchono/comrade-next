import pytest

from comrade.lib.testing_utils import CapturingContext
from comrade.modules.telemetry import Telemetry


@pytest.fixture(scope="module")
async def telemetry_ext(bot) -> Telemetry:
    return bot.get_ext("Telemetry")


@pytest.mark.bot
async def test_status_cmd(
    capturing_ctx: CapturingContext, telemetry_ext: Telemetry
):
    await telemetry_ext.status.callback(capturing_ctx)
    embed_msg = capturing_ctx.testing_captured_message

    # Ensure status embed is sent
    assert embed_msg.embeds[0].title == "Bot Status"


@pytest.mark.bot
async def test_log_cmd_full(
    capturing_ctx: CapturingContext, telemetry_ext: Telemetry
):
    await telemetry_ext.log.callback(capturing_ctx)
    log_msg = capturing_ctx.testing_captured_message

    # Ensure log file is sent
    assert log_msg.attachments[0].filename == "comrade_log.txt"


@pytest.mark.bot
async def test_log_cmd_n_lines(
    capturing_ctx: CapturingContext, telemetry_ext: Telemetry
):
    await telemetry_ext.log.callback(capturing_ctx, 30)
    log_msg = capturing_ctx.testing_captured_message

    # Ensure log file is sent
    assert log_msg.attachments[0].filename == "comrade_log.txt"
