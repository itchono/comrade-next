import pytest
from arrow import Arrow

from comrade.core.bot_subclass import Comrade


@pytest.mark.bot
def test_start_time(bot: Comrade):
    assert isinstance(bot.start_time, Arrow)
    assert bot.start_time < Arrow.utcnow()
