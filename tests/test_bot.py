import sqlite3
import pytest


def test_bot_exists():
    with pytest.raises(sqlite3.OperationalError, message="Expected no tables to exist"):
        from bot import bot
        assert bot

# def test_bot_runs():
#     assert bot.run()
#     assert bot.logout()