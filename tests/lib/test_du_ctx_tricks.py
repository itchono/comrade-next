from comrade.lib.discord_utils import context_id
from comrade.lib.testing_utils import generate_dummy_context


def test_ctx_id_guild():
    ctx_guild = generate_dummy_context(channel_id=1, dm=False)
    assert context_id(ctx_guild) == 1


def test_ctx_id_dm():
    ctx_dm = generate_dummy_context(channel_id=1, dm=True, user_id=2)
    assert context_id(ctx_dm) == 2
