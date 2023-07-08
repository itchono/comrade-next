from interactions import Client, Message

from comrade.core.updater import (
    get_current_branch,
    get_current_commit_hash,
    pull_repo,
    restart_process,
    update_packages,
)


def is_valid_update_wh(msg: Message) -> bool:
    """
    Scans a message in a relay channel to see
    if we need to run the update routine

    Check for GitHub webhook;
    content must be in the format:
    (Embed with title): New tag created:
    """

    # Check for webhook
    if msg.webhook_id is None:
        return False

    # Check for embed
    if len(msg.embeds) == 0:
        return False

    # Check for title
    return "New tag created:" in msg.embeds[0].title


async def perform_update(msg: Message, bot: Client) -> None:
    """
    Performs the update routine
    """
    current_commit_hash = get_current_commit_hash()
    pull_repo(get_current_branch())
    new_commit_hash = get_current_commit_hash()

    if current_commit_hash == new_commit_hash:
        await msg.channel.send(
            "No updates have been downloaded, "
            f"still at commit hash `{current_commit_hash}`"
        )
    else:
        await msg.channel.send(
            "Updates have been downloaded: "
            f"`{current_commit_hash}` -> `{new_commit_hash}`"
        )

    # Reinstall the bot package
    await msg.channel.send("Installing bot package...")
    output_log = update_packages()

    last_couple_of_lines = "\n".join(output_log.split("\n")[-5:])

    await msg.channel.send(f"```...\n{last_couple_of_lines}\n```")

    await msg.channel.send("Restarting bot...", ephemeral=True)
    await bot.stop()
    bot.logger.warning("RESTARTING BOT FOR NEW UPDATE...")
    restart_process(msg.channel.id)
