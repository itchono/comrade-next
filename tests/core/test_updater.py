import os
import sys

from pytest import MonkeyPatch

from comrade.core.updater import (
    check_updates_on_branch,
    get_current_branch,
    get_current_commit_hash,
    restart_process,
)


def test_updater_helpers():
    """
    Test the updater helpers

    Nothing to validate against, just make sure they don't throw
    """
    assert get_current_commit_hash()
    assert get_current_branch()
    assert check_updates_on_branch()


def test_restarter(monkeypatch: MonkeyPatch):
    """
    Make sure the restarter correctly
    adds args to the argv
    """
    stored_args = []

    with monkeypatch.context() as m:

        def mock_execv(*args, **kwargs):
            stored_args.append(args)

        m.setattr(os, "execv", mock_execv)

        restart_process()

        assert stored_args[0][0] == sys.argv[0]
        assert stored_args[0][1] == sys.argv

        restart_process(notify_channel=123)

        assert stored_args[1][0] == sys.argv[0]
        assert stored_args[1][1] == sys.argv + ["--notify_channel", "123"]
