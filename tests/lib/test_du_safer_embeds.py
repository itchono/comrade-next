from interactions import Embed

from comrade.lib.discord_utils.safer_embeds import SafeLengthEmbed


def test_embed_nominal():
    """
    Ensure the embed is created as expected
    """
    embed = SafeLengthEmbed(title="title", description="description")
    assert embed.title == "title"
    assert embed.description == "description"

    embed.add_field(name="name", value="value")
    assert embed.fields[0].name == "name"
    assert embed.fields[0].value == "value"


def test_embed_missing_fields():
    """
    Regression test against normal embed
    to make sure that missing fields are
    correctly set to None
    """
    embed = SafeLengthEmbed(title="title")
    reference_embed = Embed(title="title")
    assert embed.title == reference_embed.title
    assert embed.description == reference_embed.description


def test_embed_too_long():
    """
    Ensure that the embed is correctly
    truncated when it is too long
    """
    long_string = "abcdefghijklmnopqrstuvwxyz" * 200
    embed = SafeLengthEmbed(title=long_string, description=long_string)
    assert embed.title == long_string[:253] + "..."
    assert embed.description == long_string[:4093] + "..."

    embed.add_field(name=long_string, value=long_string)
    assert embed.fields[0].name == long_string[:253] + "..."
    assert embed.fields[0].value == long_string[:1021] + "..."

    embed.set_author(name=long_string)
    assert embed.author.name == long_string[:253] + "..."

    embed.set_footer(text=long_string)
    assert embed.footer.text == long_string[:2045] + "..."
