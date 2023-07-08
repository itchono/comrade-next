import os
import subprocess
import sys

import pytest

from comrade.core.updater import (
    check_updates_on_branch,
    get_current_branch,
    get_current_commit_hash,
    restart_process,
    update_packages,
)
from comrade.lib.testing_utils import fake_subproc_check_output


def test_get_curr_branch(monkeypatch: pytest.MonkeyPatch):
    with monkeypatch.context() as m:
        m.setattr(subprocess, "check_output", fake_subproc_check_output)

        assert get_current_branch() == "main"


def test_get_curr_commit_hash(monkeypatch: pytest.MonkeyPatch):
    with monkeypatch.context() as m:
        m.setattr(subprocess, "check_output", fake_subproc_check_output)

        assert get_current_commit_hash() == "1234567"


def test_check_updates_on_branch(monkeypatch: pytest.MonkeyPatch):
    with monkeypatch.context() as m:
        m.setattr(subprocess, "check_output", fake_subproc_check_output)

        assert "up to date" in check_updates_on_branch()


def test_update_packages(monkeypatch: pytest.MonkeyPatch):
    with monkeypatch.context() as m:
        m.setattr(subprocess, "check_output", fake_subproc_check_output)

        assert "installed comrade" in update_packages()


def test_restarter(monkeypatch: pytest.MonkeyPatch):
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
