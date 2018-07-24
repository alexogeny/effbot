import sqlite3
import pytest
import peewee


def test_bot_exists():
    with pytest.raises(peewee.OperationalError, message="Expected no tables to exist"):
        from bot import bot
        assert bot

# def test_bot_runs():
#     assert bot.run()
#     assert bot.logout()